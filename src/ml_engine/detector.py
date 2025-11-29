import cv2
import numpy as np
import os

class FaceDetector:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base, "models", "face_detection_yunet.onnx")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Missing Model: {model_path}")

        self.detector = cv2.FaceDetectorYN.create(
            model=model_path,
            config="",
            input_size=(320, 320), # Fixed size for consistency
            score_threshold=0.6, 
            nms_threshold=0.3,
            top_k=5000,
            backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
            target_id=cv2.dnn.DNN_TARGET_CPU
        )

    def detect(self, frame):
        # Resize for speed (detection runs on small image, boxes scaled up)
        h, w = frame.shape[:2]
        scale = 320 / w
        h_small = int(h * scale)
        w_small = 320
        
        small_frame = cv2.resize(frame, (w_small, h_small))
        self.detector.setInputSize((w_small, h_small))
        
        _, faces = self.detector.detect(small_frame)
        
        results = []
        if faces is not None:
            for face in faces:
                # Scale boxes back to original size
                box = face[0:4] / scale
                landmarks = face[4:14] / scale
                
                results.append({
                    # FIX: Add .tolist() so FastAPI can read it
                    'box': box.astype(int).tolist(),
                    'confidence': float(face[14]),
                    # Landmarks are internal-only (for recognizer), so numpy is fine here
                    'landmarks': landmarks.astype(np.float32)
                })
        return results