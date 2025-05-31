"""from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import numpy as np
import io
import os
from datetime import datetime

# Import attendance logger functions
from attendance_logger import initialize_csv, log_attendance

app = FastAPI()

# Enable CORS (for React frontend or testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:3000"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"message": "Smart Classroom Backend is running"}

# Constants
FACES_DIR = "faces"
LOG_FILE = "attendance_log.csv"
# Ensure the faces directory and CSV are ready
os.makedirs(FACES_DIR, exist_ok=True)
initialize_csv()

@app.post("/register/")
async def register(name: str = Form(...), file: UploadFile = Form(...)):
    print(f"Register called for name: {name}")
    contents = await file.read()
    print(f"File size received: {len(contents)} bytes")
    img = face_recognition.load_image_file(io.BytesIO(contents))
    encodings = face_recognition.face_encodings(img)

    if len(encodings) == 0:
        print("No face detected on register")
        return JSONResponse(content={"status": "error", "message": "No face detected."}, status_code=400)

    encoding = encodings[0]
    safe_name = name.strip().replace(" ", "_")
    file_path = os.path.join(FACES_DIR, f"{safe_name}.npy")
    np.save(file_path, encoding)
    print(f"Saved face encoding at {file_path}")

    return {"status": "success", "message": f"Student {name} successfully registered."}

@app.post("/attendance/")
async def attendance(file: UploadFile = Form(...)):
    print("Attendance called")
    contents = await file.read()
    print(f"File size received: {len(contents)} bytes")
    img = face_recognition.load_image_file(io.BytesIO(contents))
    encodings = face_recognition.face_encodings(img)

    if len(encodings) == 0:
        print("No face detected on attendance")
        return JSONResponse(content={"status": "error", "message": "No face detected."}, status_code=400)

    captured_encoding = encodings[0]

    for filename in os.listdir(FACES_DIR):
        known_encoding = np.load(os.path.join(FACES_DIR, filename))
        match = face_recognition.compare_faces([known_encoding], captured_encoding)[0]
        if match:
            raw_name = os.path.splitext(filename)[0]
            name = raw_name.replace("_", " ")
            print(f"Face matched: {name}")
            log_attendance(name, "Present")
            return {"status": "success", "message": f"Hello {name}, your attendance is marked."}

    print("Face not recognized")
    return JSONResponse(content={"status": "fail", "message": "Face not recognized. Please register first."}, status_code=404)   """



# File: main.py

from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import numpy as np
import io
import os
import cv2
from datetime import datetime
from attendance_logger import initialize_csv, log_attendance

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Smart Classroom Backend is running"}

# Constants
FACES_DIR = "faces"
LOG_FILE = "attendance_log.csv"
TOLERANCE = 0.45  # Lower = stricter match

# Setup
os.makedirs(FACES_DIR, exist_ok=True)
initialize_csv()

def save_debug_image(img_array, face_locations, file_name):
    """Draw rectangles around detected faces and save image."""
    img = img_array.copy()
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
    cv2.imwrite(file_name, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

@app.post("/register/")
async def register(name: str = Form(...), file: UploadFile = Form(...)):
    contents = await file.read()
    img = face_recognition.load_image_file(io.BytesIO(contents))
    face_locations = face_recognition.face_locations(img)
    encodings = face_recognition.face_encodings(img, face_locations)

    save_debug_image(img, face_locations, "debug_register.jpg")

    if len(encodings) == 0:
        return JSONResponse(content={"status": "error", "message": "No face detected."}, status_code=400)
    elif len(encodings) > 1:
        return JSONResponse(content={"status": "error", "message": "Multiple faces detected. Please use a single face image."}, status_code=400)

    encoding = encodings[0]
    safe_name = name.strip().replace(" ", "_")
    file_path = os.path.join(FACES_DIR, f"{safe_name}.npy")
    np.save(file_path, encoding)

    return {"status": "success", "message": f"Student {name} successfully registered."}

@app.post("/attendance/")
async def attendance(file: UploadFile = Form(...)):
    contents = await file.read()
    img = face_recognition.load_image_file(io.BytesIO(contents))
    face_locations = face_recognition.face_locations(img)
    encodings = face_recognition.face_encodings(img, face_locations)

    save_debug_image(img, face_locations, "debug_attendance.jpg")

    if len(encodings) == 0:
        return JSONResponse(content={"status": "error", "message": "No face detected."}, status_code=400)
    elif len(encodings) > 1:
        return JSONResponse(content={"status": "error", "message": "Multiple faces detected. Please ensure only one person is in front of the camera."}, status_code=400)

    captured_encoding = encodings[0]
    known_faces = []
    names = []

    for filename in os.listdir(FACES_DIR):
        if filename.endswith(".npy"):
            known_encoding = np.load(os.path.join(FACES_DIR, filename))
            known_faces.append(known_encoding)
            raw_name = os.path.splitext(filename)[0]
            names.append(raw_name.replace("_", " "))

        if not known_faces:
           return JSONResponse(content={"message": "No registered faces found."}, status_code=404)

    # Compute distances and find best match
    distances = face_recognition.face_distance(known_faces, captured_encoding)
    best_match_index = np.argmin(distances)

    if distances[best_match_index] < TOLERANCE:
        name = names[best_match_index]
        log_attendance(name, "Present")
        return {"status": "success", "message": f"Hello {name}, your attendance is marked."}
    else:
        return JSONResponse(content={"status": "fail", "message": "Face not recognized. Please register first."}, status_code=404)
