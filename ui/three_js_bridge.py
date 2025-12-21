import random
import math
from typing import Dict, Any, List

class ThreeJsBridge:
    """
    2D 지식 그래프 및 사고 트리를 3D 공간 데이터로 변환하는 브리지.
    """
    def __init__(self):
        self.nodes_3d = []
        self.edges_3d = []

    def convert_kg_to_3d(self, kg_data: Dict[str, Any]) -> Dict[str, Any]:
        """지식 그래프를 3D 좌표가 포함된 노드와 엣지로 변환"""
        nodes = kg_data.get("nodes", {})
        edges = kg_data.get("edges", [])
        
        converted_nodes = []
        node_map = {}
        
        # 노드를 구체(Sphere) 상에 무작위 배치 (기초 알고리즘)
        phi = math.pi * (3.0 - math.sqrt(5.0)) # golden angle
        
        for i, (node_id, info) in enumerate(nodes.items()):
            y = 1 - (i / float(len(nodes) - 1)) * 2 if len(nodes) > 1 else 0
            radius = math.sqrt(1 - y * y)
            theta = phi * i
            
            x = math.cos(theta) * radius
            z = math.sin(theta) * radius
            
            # 스케일 조정
            scale = 50
            pos = {"x": x * scale, "y": y * scale, "z": z * scale}
            
            converted_node = {
                "id": node_id,
                "position": pos,
                "type": info.get("type", "unknown"),
                "label": node_id,
                "color": self._get_color_by_type(info.get("type"))
            }
            converted_nodes.append(converted_node)
            node_map[node_id] = pos

        converted_edges = []
        for edge in edges:
            if edge["from"] in node_map and edge["to"] in node_map:
                converted_edges.append({
                    "from": edge["from"],
                    "to": edge["to"],
                    "start": node_map[edge["from"]],
                    "end": node_map[edge["to"]],
                    "type": edge.get("type", "relation")
                })
                
        return {"nodes": converted_nodes, "edges": converted_edges}

    def _get_color_by_type(self, node_type: str) -> str:
        colors = {
            "class": "#00ff00", # Green
            "function": "#0000ff", # Blue
            "rule": "#ff00ff", # Magenta
            "module": "#ffff00", # Yellow
            "analysis": "#00ffff" # Cyan
        }
        return colors.get(node_type, "#ffffff")
