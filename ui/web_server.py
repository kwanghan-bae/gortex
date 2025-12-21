import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import uvicorn

app = FastAPI(title="Gortex Web Dashboard")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.xr_connections: List[WebSocket] = [] # WebXR 기기 목록
        self.input_queue = asyncio.Queue()

    async def connect(self, websocket: WebSocket, is_xr: bool = False):
        await websocket.accept()
        self.active_connections.append(websocket)
        if is_xr:
            self.xr_connections.append(websocket)
            logger.info("🥽 WebXR Device connected.")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.xr_connections:
            self.xr_connections.remove(websocket)

    async def broadcast(self, message: str, xr_only: bool = False):
        targets = self.xr_connections if xr_only else self.active_connections
        for connection in targets:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 쿼리 파라미터나 헤더를 통해 XR 기기 여부 확인
    is_xr = websocket.query_params.get("device") == "xr"
    await manager.connect(websocket, is_xr=is_xr)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "user_input":
                    await manager.push_input(msg.get("text"))
                elif msg.get("type") == "filter_thoughts":
                    await manager.push_input(f"/filter_thoughts {msg.get('agent', '')} {msg.get('keyword', '')}")
            except:
                await manager.push_input(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def run_server(port: int = 8000):
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")

if __name__ == "__main__":
    run_server()
