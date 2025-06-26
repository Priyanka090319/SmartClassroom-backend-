# 🧠 Smart Classroom Backend (FastAPI + Face Recognition)

This is the backend component of the Smart Classroom Digital Attendance System. It allows users to register their faces and mark attendance using real-time face recognition via FastAPI.

---

## 🚀 Features

- Face registration using webcam images
- One-face-only check to prevent spoofing
- Face recognition-based attendance
- CSV attendance log with name, date, and time
- Duplicate registration and duplicate attendance prevention
- CORS-enabled API for frontend integration

---

## 🛠 Requirements

- Python 3.8 – 3.10 (not higher than 3.10 for face_recognition/dlib compatibility)

### 🔧 Install dependencies:

```bash
pip install fastapi
pip install "uvicorn[standard]"
pip install face_recognition
pip install opencv-python
pip install opencv-contrib-python
pip install numpy
pip install python-multipart
