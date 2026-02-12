# Vision-Based Surface Deformation Tracking (Balloon Experiment)

**Course:** ENR210 – Continuum Mechanics (Winter 2026)  
**Group:** Group 11  
**Activity:** Vision-based surface deformation tracking for gesture control  

This repository contains a complete **vision-based deformation tracking pipeline** that measures surface deformation using a phone camera video and **OpenCV optical flow tracking**. Marker points (black dots) are tracked on a deforming balloon surface during **inflation** and **deflation**, and the deformation is used to compute:

- **Displacement of surface points**
- **Engineering strain**
- **Estimated pressure**
- **Estimated membrane stress**
- **Estimated force**

This project is inspired by **Digital Image Correlation (DIC)** and demonstrates how low-cost vision systems can be used as soft sensors for deformation measurement.

---

## 📁 Repository Structure

Your project directory is organized as follows:

```
CONTINUUM/
│
├── docs/
│
├── output_results_deflation/
│   ├── tracked_output_deflation.mp4
│   ├── tracked_points.csv
│   ├── distance.csv
│   ├── stress_force.csv
│   ├── strain.png
│   ├── stress.png
│   └── force.png
│
├── output_results_inflation/
│   ├── tracked_output_inflation.mp4
│   ├── tracked_points.csv
│   ├── distance.csv
│   ├── stress_force.csv
│   ├── strain.png
│   ├── stress.png
│   └── force.png
│
├── Deflation_video.mp4
├── Inflation_video.mp4
│
├── deflation.py
├── inflation.py
│
└── README.md
```

---

## 🎯 Objective

The main goal of this project is to experimentally measure surface deformation using video tracking and connect the results with continuum mechanics theory.

### We aim to:
✅ Track marker points on a deformable surface  
✅ Compute displacement of points relative to a reference frame  
✅ Compute strain using a distance-based strain definition  
✅ Estimate stress and force using simplified membrane theory  
✅ Generate graphs and CSV data for poster/report submission  

---

## 🧪 Experimental Setup (Balloon Deformation)

### Materials Used
- Balloon (soft deformable surface)
- Permanent marker (black dots)
- Smartphone camera (video recording)
- Laptop with Python installed

### Procedure
1. Draw multiple black marker dots on the balloon.
2. Record two videos:
   - Balloon **inflation**
   - Balloon **deflation**
3. Run the Python scripts and manually select marker points in the first frame.
4. The program tracks marker movement using optical flow.
5. The program computes strain/stress/force and generates plots.

---

## 🧠 Continuum Mechanics Theory Used

### 1. Displacement Field

A material point moves from its reference configuration \( \mathbf{X} \) to the deformed configuration \( \mathbf{x} \):

\[
\mathbf{x} = \mathbf{X} + \mathbf{u}
\]

Where \( \mathbf{u} \) is the displacement vector.

In 2D image coordinates:

\[
u = x - x_0, \quad v = y - y_0
\]

Displacement magnitude:

\[
|\mathbf{u}| = \sqrt{u^2 + v^2}
\]

---

### 2. Engineering Strain (Distance-Based)

Instead of using spatial derivatives, strain is computed from the change in distance between two reference points:

If initial distance is \( L_0 \) and deformed distance is \( L \):

\[
\varepsilon = \frac{L - L_0}{L_0}
\]

Distance between points:

\[
L = \sqrt{(x_B-x_A)^2 + (y_B-y_A)^2}
\]

This method is robust and well-suited for low-cost vision experiments.

---

### 3. Membrane Stress (Thin Balloon Approximation)

For a thin spherical membrane under internal pressure \(P\):

\[
\sigma = \frac{Pr}{2t}
\]

Where:
- \( \sigma \) = membrane stress (Pa)
- \( P \) = internal pressure (Pa)
- \( r \) = radius of balloon (m)
- \( t \) = balloon thickness (m)

Since we do not use a pressure sensor, pressure is approximated using:

\[
P = k \cdot r
\]

Where \(k\) is a scaling constant chosen for estimation/graphing.

---

### 4. Force Estimation

Force is estimated using:

\[
F = P \cdot A
\]

Cross-sectional area:

\[
A = \pi r^2
\]

So:

\[
F = P\pi r^2
\]

---

## 💻 Computer Vision Method Used

### Optical Flow Tracking (Lucas–Kanade Method)

Tracking is performed using OpenCV's Lucas–Kanade optical flow algorithm:

- `cv2.calcOpticalFlowPyrLK()`

This method estimates motion of points based on image intensity changes.

---

## 📌 Key Feature of Our Implementation

### Manual Marker Point Selection
Automatic dot detection was unreliable due to lighting/reflection and background noise, so we implemented a manual selection system:

- User clicks marker points in the first frame
- Presses **ENTER** to begin tracking

This ensures high tracking accuracy.

---

## 🎥 Video Output Features

The generated output video includes:

- Marker points (red dots)
- Marker IDs (blue text)
- A green line connecting reference points A and B
- Real-time distance \(L\) displayed in pixels

Example overlay:

- `L = 143.52 px`

---

## 📊 Outputs Generated

Each script generates:

### Video Output
- `tracked_output_deflation.mp4`
- `tracked_output_inflation.mp4`

### CSV Files
- `tracked_points.csv` → x, y positions + displacement
- `distance.csv` → distance between reference points
- `stress_force.csv` → strain, pressure, stress, force

### Graphs
- `strain.png` → strain vs frame
- `stress.png` → stress vs frame
- `force.png` → force vs frame

---

## ⚙️ Installation Requirements

Install required Python libraries:

```bash
pip install opencv-python numpy pandas matplotlib
```

---

## ▶️ How to Run the Project

### 1️⃣ Run Inflation Script

```bash
python inflation.py
```

### 2️⃣ Run Deflation Script

```bash
python deflation.py
```

---

## 🖱️ How to Select Points (Important)

When the first frame opens:

1. Click all black marker dots on the balloon surface
2. Press **ENTER** to start tracking
3. Press **ESC** to cancel

⚠️ Recommended: select 5–10 points for best stability.

---

## 📈 Notes on Deflation Output (Important Concept)

You may observe that **average displacement increases during deflation**.

This is correct because displacement is measured relative to the **initial reference configuration** (frame 0).

If frame 0 is the fully inflated balloon, then during deflation points move away from that initial position, causing displacement magnitude to increase.

This does not indicate an error — it depends on the chosen reference configuration.

---

## 🚀 Applications

This approach can be extended to:

- Gesture control via skin deformation tracking
- Soft robotics actuator deformation measurement
- Wearable soft sensors (vision-based sensing)
- Digital Image Correlation (DIC) based strain field measurement
- Low-cost mechanical testing experiments

---

## ⚠️ Limitations

- Pressure is not directly measured (estimated using proportional model).
- Thickness is assumed constant (0.3 mm).
- Radius is assumed proportional to pixel distance.
- Optical flow can drift under very large deformation or blur.

---

## 🔥 Future Improvements

- Automatic marker dot detection (thresholding + contour filtering)
- Camera calibration to convert pixels → mm
- Multi-point strain tensor computation
- Strain field heatmap visualization
- Real-time tracking and live graph generation
- Real pressure measurement using low-cost pressure sensor

---

## 👨‍💻 Authors

**Group 11 – ENR210 Continuum Mechanics (Winter 2026)**  
(Add group member names here)

---

## 📜 License

This project is intended for **academic and educational use**.
