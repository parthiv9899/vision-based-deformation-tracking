import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# -----------------------------
# CONFIG
# -----------------------------
VIDEO_PATH = "Inflation_video.mp4"
OUTPUT_DIR = "output_results_inflation"

REFERENCE_POINT_A = 0
REFERENCE_POINT_B = 1

BALLOON_THICKNESS = 0.0003   # meters (0.3 mm assumed)
K_PRESSURE = 500             # arbitrary scaling constant for pressure (Pa per normalized radius)

LK_PARAMS = dict(
    winSize=(31, 31),
    maxLevel=5,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01)
)

# -----------------------------
# CREATE OUTPUT DIR
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# LOAD VIDEO
# -----------------------------
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise FileNotFoundError(f"Could not open video: {VIDEO_PATH}")

fps = cap.get(cv2.CAP_PROP_FPS)

ret, first_frame = cap.read()
if not ret:
    raise RuntimeError("Could not read first frame.")

h, w = first_frame.shape[:2]

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out_video_path = os.path.join(OUTPUT_DIR, "tracked_output_inflation.mp4")
out = cv2.VideoWriter(out_video_path, fourcc, fps, (w, h))

# -----------------------------
# MANUAL POINT SELECTION
# -----------------------------
points = []

def select_point(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])
        print(f"Point selected: ({x}, {y})")

        temp = first_frame.copy()
        for i, p in enumerate(points):
            cv2.circle(temp, (p[0], p[1]), 6, (0, 0, 255), -1)
            cv2.putText(temp, str(i), (p[0] + 8, p[1] - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        cv2.imshow("Select Marker Points (Press ENTER when done)", temp)

cv2.imshow("Select Marker Points (Press ENTER when done)", first_frame)
cv2.setMouseCallback("Select Marker Points (Press ENTER when done)", select_point)

print("\n[INFO] Click all marker dots on balloon.")
print("[INFO] Press ENTER when done, ESC to cancel.\n")

while True:
    key = cv2.waitKey(1) & 0xFF
    if key == 13:
        break
    elif key == 27:
        cap.release()
        cv2.destroyAllWindows()
        raise RuntimeError("Cancelled by user.")

cv2.destroyAllWindows()

if len(points) < 3:
    raise RuntimeError("Too few points selected.")

p0 = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
initial_points = p0.copy()

print(f"[INFO] Total points selected: {len(p0)}")

old_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

tracked_data = []
distance_data = []

frame_id = 0

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# -----------------------------
# TRACKING LOOP
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **LK_PARAMS)

    if p1 is None:
        break

    good_new = p1[st == 1]

    # Save tracked points
    for i, (x_new, y_new) in enumerate(good_new.reshape(-1, 2)):

        x0, y0 = initial_points[i].ravel()

        u = x_new - x0
        v = y_new - y0
        disp = np.sqrt(u**2 + v**2)

        tracked_data.append([frame_id, i, x_new, y_new, u, v, disp])

        cv2.circle(frame, (int(x_new), int(y_new)), 6, (0, 0, 255), -1)
        cv2.putText(frame, str(i), (int(x_new) + 8, int(y_new) - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # -----------------------------
    # DRAW LINE BETWEEN POINT 0 AND 1 + SHOW DISTANCE
    # -----------------------------
    if len(good_new) > max(REFERENCE_POINT_A, REFERENCE_POINT_B):
        xA, yA = good_new[REFERENCE_POINT_A].ravel()
        xB, yB = good_new[REFERENCE_POINT_B].ravel()

        L = np.sqrt((xB - xA)**2 + (yB - yA)**2)

        mid_x = int((xA + xB) / 2)
        mid_y = int((yA + yB) / 2)

        cv2.line(frame, (int(xA), int(yA)), (int(xB), int(yB)), (0, 255, 0), 2)
        cv2.putText(frame, f"L = {L:.2f} px", (mid_x, mid_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        distance_data.append([frame_id, L])

    out.write(frame)

    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1, 1, 2)

    frame_id += 1

cap.release()
out.release()

print("[INFO] Tracking finished.")
print(f"[INFO] Output video saved: {out_video_path}")

# -----------------------------
# SAVE CSV
# -----------------------------
df = pd.DataFrame(tracked_data, columns=["frame", "point_id", "x", "y", "u", "v", "displacement"])
csv_path = os.path.join(OUTPUT_DIR, "tracked_points.csv")
df.to_csv(csv_path, index=False)

dist_df = pd.DataFrame(distance_data, columns=["frame", "L_pixels"])
dist_csv_path = os.path.join(OUTPUT_DIR, "distance.csv")
dist_df.to_csv(dist_csv_path, index=False)

print(f"[INFO] CSV saved: {csv_path}")
print(f"[INFO] Distance CSV saved: {dist_csv_path}")

# -----------------------------
# STRAIN CALCULATION
# -----------------------------
L0 = dist_df.iloc[0]["L_pixels"]
dist_df["strain"] = (dist_df["L_pixels"] - L0) / L0

# -----------------------------
# PRESSURE, STRESS, FORCE (ESTIMATED)
# -----------------------------
# Assume radius proportional to distance
dist_df["radius_norm"] = dist_df["L_pixels"] / L0

# Pressure estimate (arbitrary)
dist_df["pressure_Pa"] = K_PRESSURE * dist_df["radius_norm"]

# Stress using membrane theory: sigma = Pr/(2t)
dist_df["stress_Pa"] = (dist_df["pressure_Pa"] * dist_df["radius_norm"]) / (2 * BALLOON_THICKNESS)

# Force estimate: F = P * A, with A = pi*r^2
dist_df["force_N"] = dist_df["pressure_Pa"] * np.pi * (dist_df["radius_norm"]**2)

stress_csv_path = os.path.join(OUTPUT_DIR, "stress_force.csv")
dist_df.to_csv(stress_csv_path, index=False)

print(f"[INFO] Stress/Force CSV saved: {stress_csv_path}")

# -----------------------------
# PLOTS
# -----------------------------
plt.figure(figsize=(8, 5))
plt.plot(dist_df["frame"], dist_df["strain"], linewidth=2)
plt.xlabel("Frame")
plt.ylabel("Engineering Strain")
plt.title("Strain vs Frame")
plt.grid(True)
plt.savefig(os.path.join(OUTPUT_DIR, "strain.png"), dpi=300)
plt.close()

plt.figure(figsize=(8, 5))
plt.plot(dist_df["frame"], dist_df["stress_Pa"], linewidth=2)
plt.xlabel("Frame")
plt.ylabel("Stress (Pa)")
plt.title("Estimated Stress vs Frame")
plt.grid(True)
plt.savefig(os.path.join(OUTPUT_DIR, "stress.png"), dpi=300)
plt.close()

plt.figure(figsize=(8, 5))
plt.plot(dist_df["frame"], dist_df["force_N"], linewidth=2)
plt.xlabel("Frame")
plt.ylabel("Force (N)")
plt.title("Estimated Force vs Frame")
plt.grid(True)
plt.savefig(os.path.join(OUTPUT_DIR, "force.png"), dpi=300)
plt.close()

print("\n✅ DONE. Check folder:", OUTPUT_DIR)
print("Outputs:")
print(" - tracked_output_with_distance.mp4")
print(" - tracked_points.csv")
print(" - distance.csv")
print(" - stress_force.csv")
print(" - avg_displacement.png")
print(" - strain.png")
print(" - stress.png")
print(" - force.png")
