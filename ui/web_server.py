import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import uvicorn

app = FastAPI(title="Gortex Web Dashboard")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.input_queue = asyncio.Queue() # 웹에서 들어오는 입력 큐

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

    async def push_input(self, text: str):
        """웹에서 받은 입력을 큐에 저장"""
        await self.input_queue.put(text)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 클라이언트로부터 받은 메시지 처리 (JSON 형식 가정)
            try:
                msg = json.loads(data)
                if msg.get("type") == "user_input":
                    await manager.push_input(msg.get("text"))
                elif msg.get("type") == "filter_thoughts":
                    # 메인 루프와의 통신을 위한 큐 활용 또는 글로벌 참조 필요
                    # 여기서는 단순화를 위해 큐에 특수 명령어로 주입
                    await manager.push_input(f"/filter_thoughts {msg.get('agent', '')} {msg.get('keyword', '')}")
            except:
                await manager.push_input(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def run_server(port: int = 8000):
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")

if __name__ == "__main__":
    run_server()
