# 🧠 Smart Classroom Backend (FastAPI + Face Recognition)

---

## ✅ Overview:

* This backend handles face-based **registration** and **attendance marking**.
* Built using **FastAPI**, **face\_recognition**, and **OpenCV**.
* Attendance data is saved in a **CSV file**, and registered faces are stored as `.npy` files.

---

## 🛠️ Setup Instructions (Step-by-Step)

**1. Create virtual environment**

```bash
python -m venv venv
```

**2. Activate the virtual environment**

* **Windows**:

  ```bash
  venv\Scripts\activate
  ```

* **Mac/Linux**:

  ```bash
  source venv/bin/activate
  ```

**3. Install required libraries**

```bash
pip install fastapi "uvicorn[standard]" face_recognition opencv-python opencv-contrib-python numpy python-multipart
```

**4. (Optional for anti-spoofing / blink detection)**

```bash
pip install dlib imutils scipy cmake
```

**5. Run the backend server**

```bash
uvicorn main:app --reload
```

---

## 📂 Project Files & Folders

* `main.py` – Main FastAPI app for registration and attendance
* `attendance_logger.py` – Utility module to log and check attendance in the CSV file
* `utils.py` *(optional)* – Contains helper functions like face matching, encoding loading etc.
* `registered_faces/` – Folder that stores `.npy` face encodings for each registered user
* `attendance.csv` – Automatically generated CSV log with Name, Date, Time, and Status
* `debug_images/` *(optional)* – Stores debug images with rectangles drawn on detected faces
* `README.md` – This documentation file

---

## 🌐 API Endpoints

### `POST /register/`

* Registers a new user with a unique name and facial encoding
* Form fields: `name`, `file` (image)
* Returns error if:

  * Face already exists
  * Multiple or no faces in the image

### `POST /attendance/`

* Marks attendance for a recognized user
* Form field: `file` (image)
* Checks:

  * Is the face already registered?
  * Has attendance already been marked today?
  * Does the image contain exactly one face?

---

## 🧾 Attendance Log Format

Saved in `attendance.csv` with the following format:

```
Name,Date,Time,Status
Priyanka,2025-06-24,09:15:12,Present
```

---

## 📌 Notes

* Requires clear image input with exactly one visible face
* Prevents spoofing by restricting registration/attendance to one face only
* Easily integrates with any frontend using HTTP `POST` requests
* Works well with webcam-captured images from React (e.g., `react-webcam`)

---

## 🔗 Useful Links

* [FastAPI Documentation](https://fastapi.tiangolo.com/)
* [face\_recognition GitHub](https://github.com/ageitgey/face_recognition)
* [OpenCV Documentation](https://docs.opencv.org/)
* [NumPy Documentation](https://numpy.org/doc/)
