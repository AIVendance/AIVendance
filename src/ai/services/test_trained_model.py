# Save this as test_trained_model.py in ai/services/
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from face_recognizer import FaceRecognizerWithDataset
from face_detector import FaceDetector

def test_trained_model():
    print("🧪 Testing Trained Model with Webcam")
    print("====================================")
    
    # Initialize
    recognizer = FaceRecognizerWithDataset()
    detector = FaceDetector()
    
    print(f"Enrolled students: {len(recognizer.get_enrolled_students())}")
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("❌ Cannot open webcam")
        return
    
    print("✅ Webcam started! Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect faces
        faces = detector.detect_faces(frame)
        
        # Process each face
        for i, face in enumerate(faces):
            x, y, w, h = face['box']
            
            # Draw bounding box
            color = (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Recognize face
            face_region = frame[y:y+h, x:x+w]
            student_id, confidence = recognizer.recognize_face(face_region)
            
            # Display results
            if student_id != "Unknown":
                status_text = f"{student_id} ({confidence:.2f})"
                color = (0, 255, 0)  # Green
            else:
                status_text = "Unknown"
                color = (0, 0, 255)  # Red
            
            cv2.putText(frame, status_text, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Display info
        cv2.putText(frame, f"Enrolled: {len(recognizer.get_enrolled_students())}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Trained Model - Press 'q' to quit", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Trained Face Recognition', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Test completed")

if __name__ == "__main__":
    test_trained_model()