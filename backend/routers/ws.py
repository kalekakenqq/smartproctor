from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models.session import TestSession
from backend.services.auth_service import decode_access_token
from backend.services.ws_manager import manager

router = APIRouter(tags=["ws"])


@router.websocket("/ws/sessions/{session_id}")
async def session_ws(websocket: WebSocket, session_id: int, token: str = Query(...)):
    try:
        payload = decode_access_token(token)
    except Exception:
        await websocket.close(code=4401)
        return

    db: Session = SessionLocal()
    try:
        session = db.query(TestSession).filter(TestSession.id == session_id).first()
        if not session:
            await websocket.close(code=4404)
            return
        user_id = int(payload.get("sub"))
        role = payload.get("role")
        if role == "student" and session.student_id != user_id:
            await websocket.close(code=4403)
            return
    finally:
        db.close()

    await manager.connect(session_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
