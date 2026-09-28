# ✋ Hand Gesture Volume Control

Control your Windows system volume using **real-time hand gestures** — no keyboard or mouse required.

This project uses **MediaPipe Hand Landmarker** for real-time hand tracking and **PyCaw** to control the Windows master audio volume.

## 🎥 Demo

A computer vision project that turns your webcam into a touch-free volume controller.

### Gesture Controls

| Gesture | Action |
|---|---|
| 🤏 Thumb + Index Finger | Control Volume |
| ✊ Closed Fist | Mute |
| 🖐 Open Palm | Unmute |

---

## ✨ Features

- Real-time hand tracking
- Gesture-based Windows volume control
- Smooth volume adjustment
- Closed-fist mute
- Open-palm unmute
- Gesture confirmation to prevent accidental actions
- Real-time volume percentage
- Visual volume meter
- Webcam-based interaction
- Touch-free computer control

---

## 🧠 How It Works

The webcam captures live video frames which are processed using **MediaPipe Hand Landmarker**.

The detected hand landmarks are then used to recognize different gestures.

### 🤏 Volume Control

The distance between the thumb tip and index finger tip determines the volume.

```text
Thumb + Index Finger
        ↓
Distance Calculation
        ↓
Distance → Volume %
        ↓
Smoothing
        ↓
Windows Master Volume
```

Moving the fingers closer together decreases the volume, while moving them farther apart increases it.

### ✊ Mute

A closed fist is detected when the tracked fingers are folded.

```text
Closed Fist
     ↓
Mute Windows Audio
```

### 🖐 Unmute

An open palm is detected when the fingers are extended.

```text
Open Palm
    ↓
Unmute Windows Audio
```

---

## 🛠️ Technologies Used

- **Python**
- **OpenCV** – Webcam capture and visual interface
- **MediaPipe** – Hand landmark detection
- **PyCaw** – Windows audio control
- **NumPy** – Numerical processing
- **Comtypes** – Windows COM interface

---

## 📂 Project Structure

```text
Hand-Gesture-Volume-Control/
│
├── main.py
├── requirements.txt
├── hand_landmarker.task
├── README.md
└── .gitignore
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/HADASSAHMOL2024/Hand-Gesture-Volume-Control.git
```

Move into the project directory:

```bash
cd Hand-Gesture-Volume-Control
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Project

Start the application:

```bash
python main.py
```

Make sure your webcam is connected and accessible.

Press:

```text
Q
```

to close the application.

---

## 🎮 Gesture Controls

### 🤏 Volume

Use your thumb and index finger to control the volume.

```text
Fingers closer  → Lower Volume
Fingers farther → Higher Volume
```

### ✊ Mute

Make a closed fist.

```text
Closed Fist → Mute
```

### 🖐 Unmute

Show an open palm.

```text
Open Palm → Unmute
```

---

## 📊 Gesture Detection

The application uses MediaPipe hand landmarks to determine whether fingers are extended or folded.

For volume control, the distance between these landmarks is used:

```text
Thumb Tip  → Landmark 4
Index Tip  → Landmark 8
```

The measured distance is mapped to a **0–100% volume range** and smoothed to provide stable volume control.

---

## 🔒 Privacy

The webcam stream is processed locally by the application.

No webcam frames are uploaded to a remote server by this project.

---

## 🚀 Future Improvements

Possible future improvements include:

- Media playback controls
- Screen brightness control
- Application-specific volume control
- Custom gesture mapping
- Presentation controls
- Multi-hand support
- Customizable gesture sensitivity
- Cross-platform audio support

---

## 👩‍💻 Author

**Hadassah Mol**

M.Tech | AI/ML | Computer Vision | Software Development

**GitHub:**  
https://github.com/HADASSAHMOL2024

**Portfolio:**  
https://hadassahmol2024.github.io/

---

## ⭐ Support

If you find this project interesting, consider giving the repository a ⭐ on GitHub!
