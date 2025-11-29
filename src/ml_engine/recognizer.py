import cv2
import numpy as np
import os

class FaceRecognizer:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        self.aligner_path = os.path.join(base, "models", "face_recognition_sface.onnx")
        self.model_path = os.path.join(base, "models", "arcface_resnet100.onnx")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError("❌ Missing ArcFace Model! Run download_models.py")

        self.aligner = cv2.FaceRecognizerSF.create(self.aligner_path, "")
        self.net = cv2.dnn.readNetFromONNX(self.model_path)
        
        # WARMUP: Run a dummy image so the first real request isn't slow
        print("🔥 Warming up AI Engine...")
        dummy = np.zeros((112, 112, 3), dtype=np.uint8)
        self._get_embedding_raw(dummy)
        print("✅ AI Ready")

    def _get_embedding(self, frame, face_data):
        # 1. Align/Crop face
        aligned_face = self.aligner.alignCrop(frame, face_data['landmarks'])
        return self._get_embedding_raw(aligned_face)

    def _get_embedding_raw(self, aligned_face):
        # 2. Preprocess for ArcFace
        blob = cv2.dnn.blobFromImage(aligned_face, 1.0/127.5, (112, 112), (127.5, 127.5, 127.5), swapRB=True)
        self.net.setInput(blob)
        return self.net.forward()[0]

    def recognize_batch(self, frame, known_faces, detector_results):
        results = []
        
        # Prepare DB
        db_ids, db_matrix = [], []
        for sid, embs in known_faces.items():
            for emb in embs:
                db_ids.append(sid)
                db_matrix.append(emb)
        
        if not db_matrix:
            # Empty DB -> Everyone is Unknown
            return [{"student_id": "Unknown", "confidence": 0.0, "box": f['box']} for f in detector_results]

        db_matrix = np.array(db_matrix, dtype=np.float32)
        
        for face in detector_results:
            query_emb = self._get_embedding(frame, face).astype(np.float32)
            
            # Vector Math: Cosine Similarity
            scores = np.dot(db_matrix, query_emb)
            max_idx = np.argmax(scores)
            max_score = scores[max_idx]
            
            # THRESHOLD: 0.30 is the "Goldilocks" zone for ArcFace
            if max_score > 0.30:
                best_match = db_ids[max_idx]
            else:
                best_match = "Unknown"

            results.append({
                "student_id": best_match,
                "confidence": float(max_score),
                "box": face['box']
            })
            
        return results