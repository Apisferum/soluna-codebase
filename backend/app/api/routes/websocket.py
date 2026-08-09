from fastapi import APIRouter, WebSocket

from app.music.websocket_chords import websocket_chord_endpoint

router = APIRouter()


@router.websocket("/ws/chords/{client_id}")
async def websocket_chords(websocket: WebSocket, client_id: str):
    """Real-time chord detection over WebSocket.

    Send audio chunks as base64 PCM and receive chord detections.
    """
    await websocket_chord_endpoint(websocket, client_id)
