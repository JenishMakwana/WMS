from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.utils.ws_manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/alerts")
async def alerts_ws(ws: WebSocket):
    """
    Connect from the frontend to receive real-time low-stock push alerts.
    Message format: { "type": "low_stock", "product_name": "...", "sku": "...", "qty": 0 }
    """
    await manager.connect(ws)
    try:
        while True:
            # Keep connection alive; server pushes, client just listens
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
