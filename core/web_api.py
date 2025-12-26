import logging
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

logger = logging.getLogger("GortexWebAPI")

app = FastAPI(title="Gortex Agent OS API", version="5.7.0")

# CORS 설정 (웹 프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    """실시간 이벤트 스트리밍을 위한 웹소켓 관리자"""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.get("/status")
async def get_status():
    from gortex.core.observer import GortexObserver
    observer = GortexObserver()
    return observer.get_stats()

@app.get("/agents")
async def list_agents():
    from gortex.core.registry import registry
    agents = []
    for name in registry.list_agents():
        meta = registry.get_metadata(name)
        agents.append({
            "name": name,
            "role": meta.role,
            "version": meta.version,
            "tools": meta.tools
        })
    return agents

@app.get("/knowledge/graph")
async def get_knowledge_graph():
    from gortex.utils.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    kg.build_from_system()
    return {"nodes": kg.nodes, "edges": kg.edges}

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 클라이언트로부터의 메시지는 현재 처리하지 않음 (단방향 스트리밍 위주)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def start_web_server(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()
