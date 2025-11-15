import cv2
import numpy as np


class FaceDetector:
    """AI Vendor Face Detection with MTCNN and OpenCV fallback"""
    
    def __init__(self, mtcnn_threshold=0.8):
        self.mtcnn_threshold = mtcnn_threshold
        self.use_mtcnn = False
        self.mtcnn_detector = None
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """Initialize available face detection algorithms"""
        try:
            from mtcnn import MTCNN
            self.mtcnn_detector = MTCNN()
            self.use_mtcnn = True
            print("✅ MTCNN loaded - High accuracy mode")
        except ImportError:
            print("⚠️ MTCNN not available - Using OpenCV")
        
        self.opencv_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        if self.opencv_detector.empty():
            raise Exception("❌ Failed to load OpenCV face detector")
    
    def detect_faces(self, frame, force_opencv=False):
        """Detect faces using best available method"""
        if self.use_mtcnn and not force_opencv:
            return self._detect_mtcnn(frame)
        return self._detect_opencv(frame)
    
    def _detect_mtcnn(self, frame):
        """MTCNN detection with optimization"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = frame.shape[:2]
            scale_x = scale_y = 1.0
            
            # Resize for performance
            if w > 640:
                new_w = 640
                new_h = int(h * (new_w / w))
                rgb_frame = cv2.resize(rgb_frame, (new_w, new_h))
                scale_x = w / new_w
                scale_y = h / new_h
            
            results = self.mtcnn_detector.detect_faces(rgb_frame)
            faces = []
            
            for result in results:
                if result['confidence'] > self.mtcnn_threshold and len(faces) < 10:
                    x, y, width, height = result['box']
                    faces.append({
                        'box': (int(abs(x * scale_x)), int(abs(y * scale_y)),
                               int(width * scale_x), int(height * scale_y)),
                        'confidence': result['confidence'],
                        'detector': 'MTCNN'
                    })
            return faces
            
        except Exception as e:
            print(f"MTCNN error: {e}")
            return self._detect_opencv(frame)
    
    def _detect_opencv(self, frame):
        """OpenCV Haar Cascade detection"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.opencv_detector.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        return [{'box': (x, y, w, h), 'confidence': 0.95, 'detector': 'OpenCV'}
                for x, y, w, h in faces[:10]]


class FaceDetectionApp:
    """Real-time face detection with performance monitoring"""
    
    def __init__(self):
        self.detector = FaceDetector()
        self.force_opencv = False
        self.skip_frames = True
        self.frame_count = 0
        self.processing_times = []
        self.total_faces = 0
    
    def run(self):
        """Run interactive face detection"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 20)

        if not cap.isOpened():
            print("❌ Cannot open webcam")
            return

        print("✅ Webcam started!")
        print("Controls: 'q'=quit | 's'=save | '1'=MTCNN | '2'=OpenCV | '3'=toggle skip")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            self.frame_count += 1
            
            # Skip frames if enabled
            if self.skip_frames and self.frame_count % 2 != 0:
                continue
            
            # Detect faces
            start = cv2.getTickCount()
            faces = self.detector.detect_faces(frame, self.force_opencv)
            processing_time = (cv2.getTickCount() - start) / cv2.getTickFrequency()
            
            # Update stats
            self.processing_times.append(processing_time)
            if len(self.processing_times) > 10:
                self.processing_times.pop(0)
            self.total_faces += len(faces)
            
            # Draw results
            self._draw_results(frame, faces, processing_time)
            
            cv2.imshow('Face Detection', frame)
            
            # Handle input
            if not self._handle_input(frame):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        self._print_summary()
    
    def _draw_results(self, frame, faces, processing_time):
        """Draw detection boxes and info overlay"""
        avg_time = sum(self.processing_times) / len(self.processing_times)
        fps = 1.0 / avg_time if avg_time > 0 else 0
        
        # Draw face boxes
        for face in faces:
            x, y, w, h = face['box']
            color = (0, 255, 0) if face['detector'] == 'MTCNN' else (255, 0, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            label = f"{face['confidence']:.2f}" if face['detector'] == 'MTCNN' else "Face"
            cv2.putText(frame, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Info overlay
        detector = "OpenCV" if self.force_opencv else ("MTCNN" if self.detector.use_mtcnn else "OpenCV")
        info = [
            f"Detector: {detector}",
            f"Faces: {len(faces)}",
            f"FPS: {fps:.1f}",
            f"Time: {avg_time*1000:.0f}ms",
            f"Skip: {'ON' if self.skip_frames else 'OFF'}"
        ]
        
        for i, line in enumerate(info):
            cv2.putText(frame, line, (10, 30 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def _handle_input(self, frame):
        """Handle keyboard controls"""
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            return False
        elif key == ord('s'):
            cv2.imwrite('face_capture.jpg', frame)
            print("✅ Saved: face_capture.jpg")
        elif key == ord('1') and self.detector.use_mtcnn:
            self.force_opencv = False
            print("→ MTCNN mode")
        elif key == ord('2'):
            self.force_opencv = True
            print("→ OpenCV mode")
        elif key == ord('3'):
            self.skip_frames = not self.skip_frames
            print(f"→ Frame skip: {'ON' if self.skip_frames else 'OFF'}")
        
        return True
    
    def _print_summary(self):
        """Print performance summary"""
        if not self.processing_times:
            return
        
        avg_time = sum(self.processing_times) / len(self.processing_times)
        print(f"\n📊 Performance Summary")
        print(f"Frames: {self.frame_count} | Avg: {avg_time*1000:.0f}ms | FPS: {1/avg_time:.1f}")
        print(f"Total faces detected: {self.total_faces}")


if __name__ == "__main__":
    FaceDetectionApp().run()