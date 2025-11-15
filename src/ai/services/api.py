from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import logging

from face_detector import FaceDetector
from face_recognizer import FaceRecognizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Vendor Face Recognition API",
    description="Real-time face detection and recognition for attendance system",
    version="1.0.0"
)

# CORS for frontend and multiple services
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
detector = FaceDetector()
recognizer = FaceRecognizer()

# Active classroom sessions
active_classrooms: Dict[str, Dict] = {}
# WebSocket connections for real-time updates
websocket_connections: Dict[str, List[WebSocket]] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, classroom_id: str):
        await websocket.accept()
        if classroom_id not in self.active_connections:
            self.active_connections[classroom_id] = []
        self.active_connections[classroom_id].append(websocket)

    def disconnect(self, websocket: WebSocket, classroom_id: str):
        if classroom_id in self.active_connections:
            self.active_connections[classroom_id].remove(websocket)

    async def broadcast_to_classroom(self, message: dict, classroom_id: str):
        if classroom_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[classroom_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)
            # Remove disconnected clients
            for connection in disconnected:
                self.active_connections[classroom_id].remove(connection)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {
        "message": "AI Vendor Face Recognition API",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "detection": "/detect",
            "recognition": "/recognize", 
            "enrollment": "/enroll",
            "classroom": "/classroom/{id}/start"
        }
    }

@app.get("/health")
async def health_check():
    """Health check for load balancers and monitoring"""
    return {
        "status": "healthy",
        "service": "face_recognition",
        "detector_available": detector.use_mtcnn,
        "students_enrolled": len(recognizer.get_enrolled_students()),
        "active_classrooms": len(active_classrooms)
    }

@app.post("/detect")
async def detect_faces(
    image: UploadFile = File(..., description="Image file for face detection"),
    classroom_id: Optional[str] = None,
    force_opencv: bool = False
):
    """
    Detect faces in an uploaded image
    - Used for enrollment and general face detection
    - Returns bounding boxes and confidence scores
    """
    try:
        # Validate image
        if not image.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")

        # Read and decode image
        image_data = await image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(400, "Invalid image format or corrupted file")

        # Detect faces
        faces = detector.detect_faces(img, force_opencv=force_opencv)
        
        logger.info(f"Detected {len(faces)} faces in image from classroom {classroom_id}")

        return {
            "success": True,
            "faces_detected": len(faces),
            "faces": faces,
            "detector_used": "MTCNN" if detector.use_mtcnn and not force_opencv else "OpenCV",
            "image_dimensions": f"{img.shape[1]}x{img.shape[0]}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        raise HTTPException(500, f"Face detection failed: {str(e)}")

@app.post("/recognize")
async def recognize_faces(
    image: UploadFile = File(..., description="Image file for face recognition"),
    classroom_id: Optional[str] = None,
    force_opencv: bool = False
):
    """
    Recognize faces in an uploaded image
    - Used for attendance marking
    - Returns student IDs with confidence scores
    """
    try:
        # Read and decode image
        image_data = await image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(400, "Invalid image format")

        # Detect faces first
        faces = detector.detect_faces(img, force_opencv=force_opencv)
        
        if not faces:
            return {
                "success": True,
                "faces_detected": 0,
                "recognitions": [],
                "message": "No faces detected"
            }

        # Recognize each face
        recognitions = []
        for i, face in enumerate(faces):
            x, y, w, h = face['box']
            face_region = img[y:y+h, x:x+w]
            
            student_id, confidence = recognizer.recognize_face(face_region)
            
            recognitions.append({
                "face_id": i,
                "student_id": student_id,
                "confidence": float(confidence),
                "bounding_box": face['box'],
                "detector_confidence": face['confidence'],
                "status": "recognized" if student_id != "Unknown" else "unknown"
            })

        logger.info(f"Recognized {len([r for r in recognitions if r['status'] == 'recognized'])} students in classroom {classroom_id}")

        return {
            "success": True,
            "faces_detected": len(faces),
            "recognized_faces": len([r for r in recognitions if r['status'] == 'recognized']),
            "recognitions": recognitions,
            "classroom_id": classroom_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Recognition error: {str(e)}")
        raise HTTPException(500, f"Face recognition failed: {str(e)}")

@app.post("/enroll")
async def enroll_student(
    student_id: str,
    images: List[UploadFile] = File(..., description="Multiple face images for enrollment"),
    classroom_id: Optional[str] = None
):
    """
    Enroll a new student with multiple face images
    - Used by admin during student registration
    - Requires 3+ images for better accuracy
    """
    try:
        if len(images) < 3:
            raise HTTPException(400, "At least 3 images required for enrollment")

        processed_faces = []
        
        for image in images:
            # Read and decode each image
            image_data = await image.read()
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                continue

            # Detect faces in image
            faces = detector.detect_faces(img)
            if faces:
                # Use the first detected face
                x, y, w, h = faces[0]['box']
                face_region = img[y:y+h, x:x+w]
                processed_faces.append(face_region)

        if len(processed_faces) < 2:
            raise HTTPException(400, "Could not detect faces in enough images")

        # Enroll the student
        success = recognizer.enroll_student(student_id, processed_faces)
        
        if success:
            logger.info(f"Successfully enrolled student {student_id} with {len(processed_faces)} images")
            
            return {
                "success": True,
                "student_id": student_id,
                "images_processed": len(processed_faces),
                "message": f"Student {student_id} enrolled successfully",
                "total_enrolled": len(recognizer.get_enrolled_students())
            }
        else:
            raise HTTPException(500, "Failed to enroll student - embedding generation failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enrollment error for student {student_id}: {str(e)}")
        raise HTTPException(500, f"Enrollment failed: {str(e)}")

@app.get("/enrolled-students")
async def get_enrolled_students():
    """Get list of all enrolled students"""
    return {
        "success": True,
        "total_students": len(recognizer.get_enrolled_students()),
        "students": recognizer.get_enrolled_students()
    }

@app.post("/classroom/{classroom_id}/start")
async def start_classroom_session(
    classroom_id: str,
    background_tasks: BackgroundTasks
):
    """
    Start a classroom session for real-time attendance
    - Creates session for WebSocket connections
    - Prepares for continuous face recognition
    """
    if classroom_id in active_classrooms:
        raise HTTPException(400, f"Classroom {classroom_id} session already active")

    active_classrooms[classroom_id] = {
        "session_id": str(uuid.uuid4()),
        "classroom_id": classroom_id,
        "started_at": datetime.utcnow().isoformat(),
        "students_present": [],
        "total_detections": 0
    }
    
    logger.info(f"Started classroom session: {classroom_id}")

    return {
        "success": True,
        "session_id": active_classrooms[classroom_id]["session_id"],
        "classroom_id": classroom_id,
        "started_at": active_classrooms[classroom_id]["started_at"],
        "message": f"Classroom session {classroom_id} started"
    }

@app.post("/classroom/{classroom_id}/stop")
async def stop_classroom_session(classroom_id: str):
    """Stop a classroom session"""
    if classroom_id not in active_classrooms:
        raise HTTPException(404, f"No active session for classroom {classroom_id}")

    session_data = active_classrooms.pop(classroom_id)
    
    logger.info(f"Stopped classroom session: {classroom_id}")

    return {
        "success": True,
        "classroom_id": classroom_id,
        "session_duration": "TODO: Calculate duration",
        "total_detections": session_data["total_detections"],
        "final_attendance": session_data["students_present"]
    }

@app.websocket("/ws/classroom/{classroom_id}")
async def websocket_classroom(websocket: WebSocket, classroom_id: str):
    """
    WebSocket for real-time attendance updates
    - Frontend connects to get live recognition results
    - Instructor dashboard shows real-time attendance
    """
    await manager.connect(websocket, classroom_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, classroom_id)
        logger.info(f"WebSocket disconnected for classroom {classroom_id}")

async def process_frame_for_attendance(classroom_id: str, frame_data: np.ndarray):
    """
    Process a frame for attendance and broadcast results via WebSocket
    - Used by camera services for continuous monitoring
    """
    try:
        # Recognize faces in frame
        recognitions = await recognize_faces_internal(frame_data, classroom_id)
        
        # Update classroom session
        if classroom_id in active_classrooms:
            active_classrooms[classroom_id]["total_detections"] += 1
            
            # Add new students to present list
            for rec in recognitions["recognitions"]:
                if (rec["status"] == "recognized" and 
                    rec["student_id"] not in active_classrooms[classroom_id]["students_present"]):
                    active_classrooms[classroom_id]["students_present"].append(rec["student_id"])
        
        # Broadcast to all connected clients
        await manager.broadcast_to_classroom({
            "type": "attendance_update",
            "classroom_id": classroom_id,
            "recognitions": recognitions["recognitions"],
            "timestamp": datetime.utcnow().isoformat(),
            "total_present": len(active_classrooms[classroom_id]["students_present"]) if classroom_id in active_classrooms else 0
        }, classroom_id)
        
    except Exception as e:
        logger.error(f"Frame processing error for classroom {classroom_id}: {str(e)}")

async def recognize_faces_internal(frame: np.ndarray, classroom_id: str):
    """Internal recognition function for frame processing"""
    faces = detector.detect_faces(frame)
    
    recognitions = []
    for i, face in enumerate(faces):
        x, y, w, h = face['box']
        face_region = frame[y:y+h, x:x+w]
        
        student_id, confidence = recognizer.recognize_face(face_region)
        
        recognitions.append({
            "face_id": i,
            "student_id": student_id,
            "confidence": float(confidence),
            "bounding_box": face['box'],
            "status": "recognized" if student_id != "Unknown" else "unknown",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return {
        "faces_detected": len(faces),
        "recognitions": recognitions
    }

@app.get("/classroom/{classroom_id}/status")
async def get_classroom_status(classroom_id: str):
    """Get current status of a classroom session"""
    if classroom_id not in active_classrooms:
        raise HTTPException(404, f"No active session for classroom {classroom_id}")
    
    session = active_classrooms[classroom_id]
    
    return {
        "success": True,
        "classroom_id": classroom_id,
        "session_active": True,
        "started_at": session["started_at"],
        "students_present": session["students_present"],
        "total_detections": session["total_detections"],
        "connected_clients": len(manager.active_connections.get(classroom_id, []))
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting AI Vendor Face Recognition API")
    print("📊 Available endpoints:")
    print("   - POST /detect     - Face detection")
    print("   - POST /recognize  - Face recognition") 
    print("   - POST /enroll     - Student enrollment")
    print("   - WS   /ws/classroom/{id} - Real-time updates")
    
    uvicorn.run(
        app,
        host="0.0.0.0",  # Allow connections from other machines
        port=8001,
        reload=True  # Auto-reload during development
    )