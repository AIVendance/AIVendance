# face_recognizer.py - HIGH ACCURACY WITH PRE-TRAINED MODEL
import cv2
import numpy as np
import pickle
import os
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import urllib.request

logger = logging.getLogger(__name__)

class HighAccuracyFaceRecognizer:
    """
    High-accuracy face recognition using pre-trained OpenFace model
    No dlib required - uses OpenCV DNN with deep learning
    """
    
    def __init__(self, model_path: str = "face_data", recognition_threshold: float = 0.7):
        self.model_path = model_path
        self.recognition_threshold = recognition_threshold
        self.known_embeddings: Dict[str, List[np.ndarray]] = {}
        self.student_info: Dict[str, Dict] = {}
        self.embedding_file = os.path.join(model_path, "embeddings.pkl")
        
        # Initialize pre-trained models
        self.face_net, self.face_detector = self._initialize_models()
        
        os.makedirs(model_path, exist_ok=True)
        self._load_embeddings()
        
        print(f"✅ High-Accuracy Face Recognizer initialized with {len(self.known_embeddings)} enrolled students")
        print("🔬 Using pre-trained OpenFace model (deep learning)")
    
    def _initialize_models(self):
        """Initialize pre-trained face recognition and detection models"""
        model_dir = "pretrained_models"
        os.makedirs(model_dir, exist_ok=True)
        
        # Download models if they don't exist
        self._download_models_if_needed(model_dir)
        
        # Paths to model files
        face_net_path = os.path.join(model_dir, "openface_model.t7")
        proto_path = os.path.join(model_dir, "deploy.prototxt")
        model_detection_path = os.path.join(model_dir, "res10_300x300_ssd_iter_140000.caffemodel")
        
        # Load face recognition model (OpenFace)
        try:
            face_net = cv2.dnn.readNetFromTorch(face_net_path)
            print("✅ Loaded OpenFace recognition model")
        except Exception as e:
            print(f"❌ Failed to load OpenFace model: {e}")
            print("🔄 Using enhanced feature extraction as fallback")
            face_net = None
        
        # Load face detection model
        try:
            face_detector = cv2.dnn.readNetFromCaffe(proto_path, model_detection_path)
            print("✅ Loaded face detection model")
        except Exception as e:
            print(f"❌ Failed to load face detection model: {e}")
            print("🔄 Using Haar cascade as fallback")
            face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        return face_net, face_detector
    
    def _download_models_if_needed(self, model_dir):
        """Download pre-trained models if they don't exist"""
        # OpenFace model
        face_net_path = os.path.join(model_dir, "openface_model.t7")
        if not os.path.exists(face_net_path):
            print("📥 Downloading OpenFace model...")
            try:
                urllib.request.urlretrieve(
                    "https://storage.cmusatyalab.org/openface-models/nn4.small2.v1.t7",
                    face_net_path
                )
                print("✅ OpenFace model downloaded")
            except Exception as e:
                print(f"❌ Failed to download OpenFace model: {e}")
        
        # Face detection model files
        proto_path = os.path.join(model_dir, "deploy.prototxt")
        model_detection_path = os.path.join(model_dir, "res10_300x300_ssd_iter_140000.caffemodel")
        
        if not os.path.exists(proto_path):
            print("📥 Downloading face detection prototxt...")
            try:
                urllib.request.urlretrieve(
                    "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt",
                    proto_path
                )
                print("✅ Face detection prototxt downloaded")
            except Exception as e:
                print(f"❌ Failed to download prototxt: {e}")
        
        if not os.path.exists(model_detection_path):
            print("📥 Downloading face detection model...")
            try:
                urllib.request.urlretrieve(
                    "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20180205_fp16/res10_300x300_ssd_iter_140000_fp16.caffemodel",
                    model_detection_path
                )
                print("✅ Face detection model downloaded")
            except Exception as e:
                print(f"❌ Failed to download face detection model: {e}")
    
    def _load_embeddings(self):
        """Load saved face embeddings from disk"""
        try:
            if os.path.exists(self.embedding_file):
                with open(self.embedding_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_embeddings = data.get('embeddings', {})
                    self.student_info = data.get('student_info', {})
                print(f"📁 Loaded {len(self.known_embeddings)} student embeddings")
        except Exception as e:
            print(f"❌ Failed to load embeddings: {e}")
            self.known_embeddings = {}
    
    def _save_embeddings(self):
        """Save face embeddings to disk"""
        try:
            data = {
                'embeddings': self.known_embeddings,
                'student_info': self.student_info,
                'last_updated': datetime.utcnow().isoformat()
            }
            with open(self.embedding_file, 'wb') as f:
                pickle.dump(data, f)
            print(f"💾 Saved {len(self.known_embeddings)} embeddings")
        except Exception as e:
            print(f"❌ Failed to save embeddings: {e}")
    
    def detect_face_dnn(self, image: np.ndarray) -> List[tuple]:
        """Detect faces using DNN model (more accurate than Haar)"""
        if isinstance(self.face_detector, cv2.CascadeClassifier):
            # Fallback to Haar cascade
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.1, 4)
            return [(x, y, w, h) for (x, y, w, h) in faces]
        
        # Use DNN face detector
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.face_detector.setInput(blob)
        detections = self.face_detector.forward()
        
        faces = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:  # Confidence threshold
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                faces.append((startX, startY, endX - startX, endY - startY))
        
        return faces
    
    def get_deep_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Extract 128-dimensional face embedding using pre-trained OpenFace model
        This is MUCH more accurate than basic feature extraction
        """
        if self.face_net is None:
            # Fallback to enhanced features if OpenFace not available
            return self._get_enhanced_embedding(face_image)
        
        try:
            # Preprocess face for OpenFace model
            face_blob = cv2.dnn.blobFromImage(
                face_image, 
                1.0 / 255, 
                (96, 96),  # OpenFace input size
                (0, 0, 0), 
                swapRB=True, 
                crop=False
            )
            
            # Get embedding from OpenFace model
            self.face_net.setInput(face_blob)
            embedding = self.face_net.forward()
            
            # Normalize embedding
            embedding = embedding.flatten()
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            print(f"❌ Deep embedding failed: {e}")
            # Fallback to enhanced features
            return self._get_enhanced_embedding(face_image)
    
    def _get_enhanced_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """Enhanced feature extraction fallback"""
        try:
            # Multiple feature extraction methods combined
            face_resized = cv2.resize(face_image, (150, 150))
            
            features = []
            
            # Multi-scale color histograms
            for scale in [1.0, 0.7]:
                scaled = cv2.resize(face_resized, (0, 0), fx=scale, fy=scale)
                for channel in range(3):
                    hist = cv2.calcHist([scaled], [channel], None, [64], [0, 256])
                    hist = cv2.normalize(hist, hist).flatten()
                    features.extend(hist)
            
            # LBP features
            gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            lbp = self._local_binary_pattern(gray)
            lbp_hist = cv2.calcHist([lbp], [0], None, [256], [0, 256])
            lbp_hist = cv2.normalize(lbp_hist, lbp_hist).flatten()
            features.extend(lbp_hist[:128])
            
            return np.array(features, dtype=np.float32)
            
        except Exception:
            return np.zeros(512)  # Return zeros if extraction fails
    
    def _local_binary_pattern(self, image, points=8, radius=1):
        """Calculate Local Binary Pattern"""
        lbp = np.zeros_like(image)
        for i in range(points):
            x = radius * np.cos(2 * np.pi * i / points)
            y = radius * np.sin(2 * np.pi * i / points)
            
            fx, fy = np.floor(x), np.floor(y)
            cx, cy = np.ceil(x), np.ceil(y)
            
            ty = y - fy
            tx = x - fx
            
            w1 = (1 - tx) * (1 - ty)
            w2 = tx * (1 - ty)
            w3 = (1 - tx) * ty
            w4 = tx * ty
            
            neighbor = (w1 * np.roll(image, (-int(fy), -int(fx))) +
                       w2 * np.roll(image, (-int(fy), -int(cx))) +
                       w3 * np.roll(image, (-int(cy), -int(fx))) +
                       w4 * np.roll(image, (-int(cy), -int(cx))))
            
            lbp += (neighbor > image) * (1 << i)
        
        return lbp.astype(np.uint8)
    
    def enroll_student(self, student_id: str, face_images: List[np.ndarray], 
                      student_name: Optional[str] = None) -> bool:
        """Enroll a new student with high-accuracy embeddings"""
        try:
            if len(face_images) < 5:
                print(f"❌ Need at least 5 images for good accuracy, got {len(face_images)}")
                return False
            
            embeddings = []
            valid_images = 0
            
            for i, face_img in enumerate(face_images):
                try:
                    if face_img is None or face_img.size == 0:
                        continue
                    
                    # Use deep learning embedding (much more accurate)
                    embedding = self.get_deep_embedding(face_img)
                    if embedding is not None and len(embedding) > 0:
                        embeddings.append(embedding)
                        valid_images += 1
                        print(f"✅ Processed image {i+1} with deep learning")
                    
                except Exception as e:
                    print(f"⚠️  Failed to process image {i+1}: {e}")
                    continue
            
            print(f"📊 Valid deep embeddings: {len(embeddings)}")
            
            if len(embeddings) < 3:
                print(f"❌ Only {len(embeddings)} valid embeddings, need at least 3")
                return False
            
            # Store multiple embeddings for better recognition
            self.known_embeddings[student_id] = embeddings
            
            self.student_info[student_id] = {
                'name': student_name or student_id,
                'enrolled_date': datetime.utcnow().isoformat(),
                'images_used': valid_images,
                'model_type': 'OpenFace' if self.face_net is not None else 'Enhanced'
            }
            
            self._save_embeddings()
            
            print(f"🎉 Successfully enrolled {student_id} with {valid_images} deep embeddings")
            return True
            
        except Exception as e:
            print(f"❌ Enrollment failed: {e}")
            return False
    
    def recognize_face(self, face_image: np.ndarray) -> Tuple[str, float]:
        """Recognize face with high accuracy using deep learning"""
        try:
            if face_image is None or face_image.size == 0:
                return "Unknown", 0.0
            
            if not self.known_embeddings:
                return "Unknown", 0.0
            
            query_embedding = self.get_deep_embedding(face_image)
            best_match = "Unknown"
            best_similarity = 0.0
            
            # Compare with all known embeddings
            for student_id, known_embeddings in self.known_embeddings.items():
                similarities = []
                for known_embedding in known_embeddings:
                    similarity = self._cosine_similarity(query_embedding, known_embedding)
                    similarities.append(similarity)
                
                # Use maximum similarity for this student
                max_similarity = max(similarities) if similarities else 0
                
                if max_similarity > best_similarity and max_similarity > self.recognition_threshold:
                    best_similarity = max_similarity
                    best_match = student_id
            
            return best_match, float(best_similarity)
            
        except Exception as e:
            print(f"❌ Recognition failed: {e}")
            return "Unknown", 0.0
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def get_enrolled_students(self) -> List[str]:
        return list(self.known_embeddings.keys())
    
    def get_student_info(self, student_id: str) -> Optional[Dict]:
        return self.student_info.get(student_id)
    
    def remove_student(self, student_id: str) -> bool:
        try:
            if student_id in self.known_embeddings:
                del self.known_embeddings[student_id]
                if student_id in self.student_info:
                    del self.student_info[student_id]
                self._save_embeddings()
                print(f"✅ Removed student: {student_id}")
                return True
            else:
                print(f"❌ Student {student_id} not found")
                return False
        except Exception as e:
            print(f"❌ Error removing student: {e}")
            return False
    
    def get_system_stats(self) -> Dict:
        return {
            'total_students': len(self.known_embeddings),
            'recognition_threshold': self.recognition_threshold,
            'using_deep_learning': self.face_net is not None,
            'model_type': 'OpenFace' if self.face_net is not None else 'Enhanced Features'
        }


# Global instance
face_recognizer = HighAccuracyFaceRecognizer()