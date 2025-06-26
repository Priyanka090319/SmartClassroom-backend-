
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import numpy as np
import io
import os
import cv2
from attendance_logger import initialize_csv, log_attendance, already_marked_today

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
    img = img_array.copy()
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
    cv2.imwrite(file_name, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

def is_face_already_registered(new_encoding):
    for filename in os.listdir(FACES_DIR):
        if filename.endswith(".npy"):
            known_encoding = np.load(os.path.join(FACES_DIR, filename))
            distance = face_recognition.face_distance([known_encoding], new_encoding)[0]
            if distance < TOLERANCE:
                existing_name = os.path.splitext(filename)[0].replace("_", " ")
                return True, existing_name
    return False, None

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
        return JSONResponse(content={"status": "error", "message": "Multiple faces detected. Use a single face image."}, status_code=400)

    encoding = encodings[0]

    already_registered, existing_name = is_face_already_registered(encoding)
    if already_registered:
        return JSONResponse(
            content={
                "status": "error",
                "message": f"This face is already registered as {existing_name}. Cannot register with another name."
            },
            status_code=403
        )

    safe_name = name.strip().replace(" ", "_")
    file_path = os.path.join(FACES_DIR, f"{safe_name}.npy")
    np.save(file_path, encoding)

    return {"status": "success", "message": f"Hello {name}, you are successfully registered."}

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
        return JSONResponse(content={"status": "error", "message": "No registered faces found."}, status_code=404)

    distances = face_recognition.face_distance(known_faces, captured_encoding)
    best_match_index = np.argmin(distances)

    if distances[best_match_index] < TOLERANCE:
        name = names[best_match_index]

        if already_marked_today(name):
            return JSONResponse(
                content={"status": "info", "message": f"{name}, you have already marked your attendance today."},
                status_code=200
            )

        log_attendance(name, "Present")
        return {"status": "success", "message": f"Hello {name}, your attendance is marked."}
    else:
        return JSONResponse(content={"status": "fail", "message": "Face not recognized. Please register first."}, status_code=404)


