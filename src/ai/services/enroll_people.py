# enroll_people.py
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from face_detector import FaceDetector
from face_recognizer import HighAccuracyFaceRecognizer

class FaceEnroller:
    def __init__(self):
        self.recognizer = HighAccuracyFaceRecognizer(recognition_threshold=0.6)
        self.detector = FaceDetector()  # existing detector
    
    def show_current_students(self):
        """Show currently enrolled students"""
        students = self.recognizer.get_enrolled_students()
        print(f"\n📊 Currently enrolled: {len(students)} students")
        if students:
            for i, student in enumerate(students, 1):
                info = self.recognizer.get_student_info(student)
                images_used = info.get('images_used', '?') if info else '?'
                print(f"   {i}. {student} ({images_used} images)")
        print()
    
    def enroll_person(self, person_name=None):
        """Enroll a new person"""
        if person_name is None:
            person_name = input("Enter person's name/ID: ").strip()
            if not person_name:
                print("❌ Name cannot be empty")
                return False
        
        print(f"\n🎯 Enrolling: {person_name}")
        print("📸 We'll capture 5 images")
        print("💡 Move head slightly between captures for better accuracy")
        print("Press 'c' to capture, 'q' to quit enrollment")
        
        cap = cv2.VideoCapture(0)
        captured_images = []
        capture_count = 0
        
        while capture_count < 5:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Detect faces
            faces = self.detector.detect_faces(frame)
            
            # Show instructions on frame
            cv2.putText(frame, f"Enrolling: {person_name}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Captured: {capture_count}/5 - Press 'c' to capture", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, "Press 'q' to quit enrollment", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw face detection
            for face in faces:
                x, y, w, h = face['box']
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected - Press C", (x, y-15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            cv2.imshow(f'Enroll: {person_name} - Press C to Capture', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c') and faces:
                # Capture the face
                x, y, w, h = faces[0]['box']
                face_region = frame[y:y+h, x:x+w]
                
                # Validate face region
                if face_region.size > 0 and face_region.shape[0] > 50 and face_region.shape[1] > 50:
                    captured_images.append(face_region.copy())
                    capture_count += 1
                    print(f"✅ Captured image {capture_count}/5 for {person_name}")
                    
                    # Show preview
                    preview = cv2.resize(face_region, (200, 200))
                    cv2.imshow('Captured Face', preview)
                    cv2.waitKey(300)
                    cv2.destroyWindow('Captured Face')
                else:
                    print("⚠️  Face too small, try again")
                    
            elif key == ord('q'):
                print("⏹️  Enrollment cancelled")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if captured_images:
            print(f"🔄 Processing {len(captured_images)} images for {person_name}...")
            success = self.recognizer.enroll_student(person_name, captured_images, person_name)
            
            if success:
                print(f"🎉 Successfully enrolled {person_name}!")
                return True
            else:
                print(f"❌ Failed to enroll {person_name}")
                return False
        else:
            print("❌ No images captured")
            return False
    
    def test_recognition(self):
        """Test recognition of all enrolled people"""
        students = self.recognizer.get_enrolled_students()
        if not students:
            print("❌ No students enrolled yet!")
            return
        
        print(f"\n🧪 Testing recognition of {len(students)} enrolled people...")
        print("Look at the camera to see who gets recognized!")
        print("Press 'q' to quit test")
        
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Detect faces
            faces = self.detector.detect_faces(frame)
            
            recognized_any = False
            
            for face in faces:
                x, y, w, h = face['box']
                face_region = frame[y:y+h, x:x+w]
                
                # Recognize face
                student_id, confidence = self.recognizer.recognize_face(face_region)
                
                # Display results
                if student_id != "Unknown":
                    recognized_any = True
                    color = (0, 255, 0)  # Green - Recognized
                    text = f"{student_id} ({confidence:.2f})"
                    status = "✅ RECOGNIZED"
                else:
                    color = (0, 0, 255)  # Red - Unknown
                    text = "Unknown"
                    status = "❌ Not enrolled"
                
                # Draw bounding box and text
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
                cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                cv2.putText(frame, status, (x, y+h+25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Show instructions and stats
            cv2.putText(frame, f"Enrolled: {len(students)} people", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, "Press 'q' to quit test", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            if not recognized_any and faces:
                cv2.putText(frame, "Face detected but not recognized!", 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, "Enroll this person using the main menu", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            cv2.imshow('Recognition Test - Press Q to quit', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Recognition test completed")
    
    def delete_student(self):
        """Delete an enrolled student"""
        students = self.recognizer.get_enrolled_students()
        if not students:
            print("❌ No students to delete")
            return
        
        print("\n🗑️  Delete Student")
        print("=================")
        for i, student in enumerate(students, 1):
            print(f"{i}. {student}")
        
        try:
            choice = int(input(f"\nEnter number to delete (1-{len(students)}): "))
            if 1 <= choice <= len(students):
                student_to_delete = students[choice-1]
                confirm = input(f"Delete {student_to_delete}? (y/n): ").lower()
                if confirm == 'y':
                    success = self.recognizer.remove_student(student_to_delete)
                    if success:
                        print(f"✅ Deleted {student_to_delete}")
                    else:
                        print(f"❌ Failed to delete {student_to_delete}")
                else:
                    print("❌ Deletion cancelled")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def run_menu(self):
        """Main menu interface"""
        while True:
            print("\n" + "="*50)
            print("🎯 FACE ENROLLMENT SYSTEM")
            print("="*50)
            self.show_current_students()
            print("1. 📸 Enroll New Person")
            print("2. 🧪 Test Recognition")
            print("3. 🗑️  Delete Student") 
            print("4. 🚪 Exit")
            print("-"*50)
            
            choice = input("Choose option (1-4): ").strip()
            
            if choice == '1':
                self.enroll_person()
            elif choice == '2':
                self.test_recognition()
            elif choice == '3':
                self.delete_student()
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice, please try again")

def main():
    print("🚀 Face Enrollment System")
    print("=========================")
    print("You can enroll multiple people and test recognition")
    
    enroller = FaceEnroller()
    enroller.run_menu()

if __name__ == "__main__":
    main()