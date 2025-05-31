import face_recognition

print("face_recognition version:", face_recognition.__version__)

# Load an example image (replace with your own image path)
image = face_recognition.load_image_file("your_image.jpg")

# Find all face locations in the image
face_locations = face_recognition.face_locations(image)

print(f"Found {len(face_locations)} face(s) in this image.")
