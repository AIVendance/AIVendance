import cv2
import numpy as np
import os

# 1. SETUP PATHS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "ai_models")

# Define model paths (Make sure these file names match EXACTLY what you have in your folder!)
DETECTION_MODEL = os.path.join(MODELS_DIR, "face_detection_yunet.onnx")
# Update this filename if yours is different (e.g., arcface_int8.onnx)
RECOGNITION_MODEL = os.path.join(MODELS_DIR, "face_recognition_sface.onnx") 

# 2. INITIALIZE MODELS
try:
    # Initialize Detector (YuNet)
    detector = cv2.FaceDetectorYN.create(
        DETECTION_MODEL,
        "",
        (320, 320), # Default input size
        0.9,        # Score threshold
        0.3,        # NMS threshold
        5000        # Top K
    )
    
    # Initialize Recognizer (SFace/ArcFace)
    recognizer = cv2.FaceRecognizerSF.create(
        RECOGNITION_MODEL,
        ""
    )
    print("✅ AI Models Loaded Successfully")
except Exception as e:
    print(f"❌ Error loading AI models: {e}")
    print(f"Checked path: {DETECTION_MODEL}")

def get_face_embedding(image_file_content):
    """
    Takes raw image bytes, detects a face, and returns its 128-D embedding.
    """
    # 1. Convert bytes to OpenCv Image
    nparr = np.frombuffer(image_file_content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return {"error": "Could not decode image"}

    # 2. Resize for consistent detection (Optional but recommended)
    height, width, _ = img.shape
    detector.setInputSize((width, height))

    # 3. Detect Faces
    # faces output: [x, y, w, h, x_re, y_re, x_le, y_le, ...]
    _, faces = detector.detect(img)

    if faces is None:
        return {"error": "No face detected in image"}
    
    # For enrollment, we assume the photo has only ONE face (the student)
    # We take the first face found
    face_data = faces[0]

    # 4. Align & Crop Face
    aligned_face = recognizer.alignCrop(img, face_data)

    # 5. Generate Embedding (Feature Vector)
    feat = recognizer.feature(aligned_face)
    
    # feature() returns a numpy array, we need a standard list for the database
    return {"embedding": feat[0].tolist()}