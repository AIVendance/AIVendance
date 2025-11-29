from datetime import datetime
from typing import Dict, List
from fastapi import WebSocket
from src.db.repository import AttendanceRepository

class AttendanceService:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

    def calculate_arrival_status(self, session, now):
        start = session.actual_start_time.replace(tzinfo=None) if session.actual_start_time else datetime.now()
        delay = (now - start).total_seconds() / 60
        if delay <= 10: return "Present"
        elif delay <= 30: return "Late"
        else: return "Very Late"

    async def process_frame(self, repo, detector, recognizer, frame, classroom_id):
        # 1. Detect & Recognize
        faces = detector.detect(frame)
        known_faces = await repo.get_all_embeddings()
        results = recognizer.recognize_batch(frame, known_faces, faces)
        
        print(f"👀 Room {classroom_id}: Saw {len(results)} faces")

        # --- LOGIC FIX: REMOVE DUPLICATES ---
        # If two faces claim to be "Student 101", keep the best one.
        from collections import defaultdict
        id_groups = defaultdict(list)
        for i, res in enumerate(results):
            if res['student_id'] != "Unknown":
                id_groups[res['student_id']].append(i)
        
        for sid, indices in id_groups.items():
            if len(indices) > 1:
                # Sort by confidence (High -> Low)
                indices.sort(key=lambda x: results[x]['confidence'], reverse=True)
                # Mark losers as Unknown
                for idx in indices[1:]:
                    results[idx]['student_id'] = "Unknown"
        # ------------------------------------

        session = await repo.get_active_session_by_room(classroom_id)
        logs = []
        
        if session:
            now = datetime.now()
            for res in results:
                sid = res['student_id']
                res['time'] = now.strftime("%H:%M")
                
                if sid == "Unknown":
                    res['status'] = "Unknown"
                    res['duration'] = "0m"
                    logs.append(res)
                    continue

                if not await repo.check_enrollment(sid, session.course_code):
                    res['status'] = "⚠️ WRONG CLASS"
                    logs.append(res)
                    continue 

                arr_stat = self.calculate_arrival_status(session, now)
                _, duration = await repo.log_attendance(session.session_id, sid, arr_stat)
                
                # Strict Time Rule (1 min for testing)
                final_stat = f"{arr_stat} (Confirmed)" if duration >= 1 else f"{arr_stat} (Building: {int(duration)}m)"
                
                res['status'] = final_stat
                res['duration'] = f"{int(duration)}m"
                logs.append(res)
        
        await self.broadcast(classroom_id, logs)
        return logs

    async def connect_websocket(self, ws: WebSocket, room_id: str):
        await ws.accept()
        if room_id not in self.connections: self.connections[room_id] = []
        self.connections[room_id].append(ws)

    async def broadcast(self, room_id, data):
        if room_id in self.connections:
            self.connections[room_id] = [ws for ws in self.connections[room_id] if ws.client_state.name=="CONNECTED"]
            for ws in self.connections[room_id]:
                try: await ws.send_json({"type":"update", "data":data})
                except: pass

attendance_service = AttendanceService()