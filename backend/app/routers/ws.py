from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.core.websocket_manager import ws_manager
from app.core.deps import get_db
from app.core.security import verify_token

router = APIRouter()

@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    user = verify_token(token, db)
    if not user:
        await websocket.close(code=1008) # Policy violation
        return
        
    await ws_manager.connect(websocket, user.id)
    try:
        while True:
            # We don't expect the client to send messages here, just listen
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user.id)
