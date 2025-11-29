from typing import List
import numpy as np
from fastapi import UploadFile, HTTPException
from src.utils.image_processing import read_image_from_bytes

class EnrollmentService:
    async def enroll_student(self, repo, detector, recognizer, student_id, full_name, files):
        if len(files) > 10: raise HTTPException(400, "Max 10 images")
        if len(files) < 3: raise HTTPException(400, "Need 3 images")
        
        valid_embeddings = []
        for f in files:
            img = read_image_from_bytes(await f.read())
            faces = detector.detect(img)
            if faces:
                # Largest face
                faces.sort(key=lambda x: x['box'][2]*x['box'][3], reverse=True)
                emb = recognizer._get_embedding(img, faces[0])
                if emb is not None: valid_embeddings.append(emb)

        if not valid_embeddings: raise HTTPException(400, "No faces found")
        
        # DUPLICATE CHECK
        known = await repo.get_all_embeddings()
        avg_new = np.mean(valid_embeddings, axis=0)
        
        for sid, embs in known.items():
            for stored in embs:
                score = np.dot(avg_new, stored)
                if score > 0.5: # 0.5 is safe threshold for "Same Person" check
                    raise HTTPException(400, f"Face already enrolled as {sid}")

        await repo.create_user(student_id, full_name, f"{student_id}@edu")
        await repo.save_embedding(student_id, valid_embeddings[0])
        return len(valid_embeddings)

enrollment_service = EnrollmentService()