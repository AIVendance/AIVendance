import cv2
import numpy as np
import os

class FaceRecognizer:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        
        # 1. SFace (Alignment)
        self.aligner_path = os.path.join(base, "models", "face_recognition_sface.onnx")
        # 2. LIGHT ArcFace (Recognition)
        self.model_path = os.path.join(base, "models", "arcface_int8.onnx")  # <--- CHANGED
        
        if not os.path.exists(self.aligner_path):
            raise FileNotFoundError("❌ Missing SFace Model!")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError("❌ Missing ArcFace INT8 Model! Run the download command.")

        # Load Aligner
        self.aligner = cv2.FaceRecognizerSF.create(
            model=self.aligner_path,
            config="",
            backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
            target_id=cv2.dnn.DNN_TARGET_CPU
        )
        
        # Load Recognizer
        self.net = cv2.dnn.readNetFromONNX(self.model_path)
        print("✅ Lightweight ArcFace (Int8) Loaded")

    def _get_embedding(self, frame, face_data):
        # 1. Align
        aligned_face = self.aligner.alignCrop(frame, face_data['landmarks'])
        
        # 2. Preprocess
        # ArcFace INT8 expects the same input: 112x112, RGB, Normalized
        rgb_face = cv2.cvtColor(aligned_face, cv2.COLOR_BGR2RGB)
        blob = cv2.dnn.blobFromImage(
            rgb_face, 
            1.0 / 127.5, 
            (112, 112), 
            (127.5, 127.5, 127.5), 
            swapRB=False
        )
        
        # 3. Inference
        self.net.setInput(blob)
        embedding = self.net.forward()[0]
        
        # 4. Normalize
        return embedding / np.linalg.norm(embedding)

    def recognize_batch(self, frame, known_faces, detector_results):
        results = []
        db_ids, db_matrix = [], []
        
        for sid, embs in known_faces.items():
            for emb in embs:
                db_ids.append(sid)
                db_matrix.append(emb)
        
        # Handle Empty DB
        if not db_matrix:
            return [{"student_id": "Unknown", "confidence": 0.0, "box": f['box']} for f in detector_results]

        db_matrix = np.array(db_matrix, dtype=np.float32)
        
        for face in detector_results:
            query_emb = self._get_embedding(frame, face).astype(np.float32)
            
            # Vector Math
            scores = np.dot(db_matrix, query_emb)
            max_idx = np.argmax(scores)
            max_score = scores[max_idx]
            
            # Threshold: 0.25 is safe for this model
            if max_score > 0.25:
                best_match = db_ids[max_idx]
            else:
                best_match = "Unknown"

            results.append({
                "student_id": best_match,
                "confidence": float(max_score),
                "box": face['box']
            })
            
        return results