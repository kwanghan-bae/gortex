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
                "color": self._get_color_by_type(info.get("type")),
                "spatial_metadata": {
                    "glow": 0.5 if info.get("type") == "rule" else 0.2,
                    "haptic_feedback": "light" if info.get("type") == "function" else "medium",
                    "scale": 1.5 if info.get("type") == "class" else 1.0
                }
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
        
        # [Knowledge Mapping] 지식 노드 간 상관관계 엣지 추가
        for node_id, info in nodes.items():
            if info.get("links") and node_id in node_map:
                for target_id in info["links"]:
                    if target_id in node_map:
                        converted_edges.append({
                            "from": node_id,
                            "to": target_id,
                            "start": node_map[node_id],
                            "end": node_map[target_id],
                            "type": "correlation"
                        })
                
        return {"nodes": converted_nodes, "edges": converted_edges}

    def convert_thought_to_3d(self, thought_tree: List[Dict[str, Any]]) -> Dict[str, Any]:
        """사고 과정을 3D 신경망 구조로 변환"""
        converted_nodes = []
        node_map = {}
        
        # 계층별 배치를 위한 기초 알고리즘
        for i, item in enumerate(thought_tree):
            node_id = item.get("id")
            parent_id = item.get("parent_id")
            
            # 확신도에 따른 크기 및 밝기 조절
            certainty = item.get("certainty", 0.5)
            size = 1 + certainty * 2
            
            # 위치 계산 (단순 계층형 트리 배치)
            depth = 0
            curr = item
            while curr.get("parent_id"):
                depth += 1
                # 부모 노드 찾기 (단순화)
                parent = next((t for t in thought_tree if t["id"] == curr["parent_id"]), None)
                if not parent: break
                curr = parent
            
            pos = {
                "x": depth * 20,
                "y": (i % 5) * 10 - 20,
                "z": (i // 5) * 10 - 20
            }
            
            converted_node = {
                "id": node_id,
                "position": pos,
                "text": item.get("text"),
                "certainty": certainty,
                "size": size,
                "type": item.get("type", "analysis"),
                "color": "#ffaa00" if item.get("type") == "decision" else "#00aaff",
                "visual_payload": item.get("visual_payload") # 시각적 데이터 주입
            }
            converted_nodes.append(converted_node)
            node_map[node_id] = pos

        converted_edges = []
        for item in thought_tree:
            if item.get("parent_id") and item["parent_id"] in node_map:
                converted_edges.append({
                    "from": item["parent_id"],
                    "to": item["id"],
                    "start": node_map[item["parent_id"]],
                    "end": node_map[item["id"]]
                })
                
        return {"nodes": converted_nodes, "edges": converted_edges}

    def convert_causal_graph_to_3d(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """인과 관계 그래프를 3D 타임라인 구조로 변환"""
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        converted_nodes = []
        node_map = {}
        import math
        
        # 시간순 배치를 위해 노드 순회
        for i, node in enumerate(nodes):
            # 시간축(X)을 따라 배치하고 Y, Z는 무작위성을 부여하여 겹침 방지
            pos = {
                "x": i * 15,
                "y": math.sin(i) * 10,
                "z": math.cos(i) * 10
            }
            
            converted_node = {
                "id": node["id"],
                "position": pos,
                "label": node["label"],
                "agent": node["agent"],
                "event": node["event"],
                "color": self._get_color_by_agent(node["agent"])
            }
            converted_nodes.append(converted_node)
            node_map[node["id"]] = pos

        converted_edges = []
        for edge in edges:
            if edge["from"] in node_map and edge["to"] in node_map:
                converted_edges.append({
                    "from": edge["from"],
                    "to": edge["to"],
                    "start": node_map[edge["from"]],
                    "end": node_map[edge["to"]]
                })
                
        return self.apply_clustering({"nodes": converted_nodes, "edges": converted_edges})

    def convert_dependency_graph(self, dep_data: Dict[str, Any]) -> Dict[str, Any]:
        """의존성 그래프 데이터를 3D 시각화 데이터로 변환 (군집화 적용)"""
        raw_nodes = dep_data.get("nodes", [])
        raw_edges = dep_data.get("edges", [])
        
        converted_nodes = []
        node_map = {}
        import math
        
        # 간단한 원형 배치 또는 Force-directed Layout (여기선 원형+높이 변형)
        count = len(raw_nodes)
        for i, node in enumerate(raw_nodes):
            theta = (i / count) * 2 * math.pi
            radius = 30 + (node.get("connections", 0) * 2) # 연결 많을수록 바깥쪽? 아니면 안쪽? 여기선 바깥
            
            pos = {
                "x": math.cos(theta) * radius,
                "y": math.sin(theta) * radius,
                "z": (i % 5) * 10
            }
            
            converted_nodes.append({
                "id": node["id"],
                "label": node["id"],
                "value": node.get("value", 1), # 크기용
                "position": pos,
                "type": "module"
            })
            node_map[node["id"]] = pos
            
        converted_edges = []
        for edge in raw_edges:
            if edge["from"] in node_map and edge["to"] in node_map:
                converted_edges.append({
                    "from": edge["from"],
                    "to": edge["to"],
                    "start": node_map[edge["from"]],
                    "end": node_map[edge["to"]],
                    "weight": edge.get("weight", 1)
                })

        # 군집화 적용
        graph_3d = {"nodes": converted_nodes, "edges": converted_edges}
        return self.apply_clustering(graph_3d)

    def convert_kg_to_3d(self, nodes: Dict[str, Any], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synaptic Index 기반 지식 그래프를 3D 공간 데이터로 변환"""
        converted_nodes = []
        node_map = {}
        import math
        
        # 임의의 3D 공간 배치
        for i, (node_id, info) in enumerate(nodes.items()):
            pos = {
                "x": math.cos(i) * 50,
                "y": math.sin(i) * 50,
                "z": (i % 10) * 10
            }
            converted_nodes.append({
                "id": node_id,
                "label": info.get("name"),
                "type": info.get("type"),
                "position": pos,
                "color": self._get_color_by_type(info.get("type"))
            })
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
        
        # [Knowledge Mapping] 지식 노드 간 상관관계 엣지 추가
        for node_id, info in nodes.items():
            if info.get("links") and node_id in node_map:
                for target_id in info["links"]:
                    if target_id in node_map:
                        converted_edges.append({
                            "from": node_id,
                            "to": target_id,
                            "start": node_map[node_id],
                            "end": node_map[target_id],
                            "type": "correlation"
                        })
                
        return self.apply_clustering({"nodes": converted_nodes, "edges": converted_edges})

    def apply_impact_highlight(self, graph_3d: Dict[str, Any], impact_data: Dict[str, List[str]]) -> Dict[str, Any]:
        """특정 노드 및 연결된 영향 범위 노드들에 하이라이트(Glow) 적용"""
        direct_files = impact_data.get("direct", [])
        indirect_files = impact_data.get("indirect", [])
        target_file = impact_data.get("target", "")
        
        for node in graph_3d.get("nodes", []):
            node_file = node.get("file") or node.get("label", "").split(":")[-1].strip()
            
            if node_file == target_file:
                node["color"] = "#ff0000" # 강렬한 빨강 (타겟)
                node["spatial_metadata"] = {"glow": 1.0, "scale": 2.0}
            elif node_file in direct_files:
                node["color"] = "#ff4444" # 빨강 (직접 영향)
                node["spatial_metadata"] = {"glow": 0.7, "scale": 1.5}
            elif node_file in indirect_files:
                node["color"] = "#ff8888" # 연한 빨강 (간접 영향)
                node["spatial_metadata"] = {"glow": 0.4, "scale": 1.2}
                
        return graph_3d

    def apply_clustering(self, graph_3d: Dict[str, Any]) -> Dict[str, Any]:
        """노드 간의 이름 유사도 및 파일 경로를 기반으로 군집화(Clustering) 수행"""
        nodes = graph_3d.get("nodes", [])
        if not nodes: return graph_3d
        
        clusters = {} # {cluster_id: color}
        import hashlib
        
        for node in nodes:
            label = node.get("label", "")
            # 단순 클러스터링 전략: 파일 경로나 이름의 첫 단어 활용
            # 예: "core/auth.py" -> "core", "test_manager" -> "test"
            if "/" in label:
                cluster_id = label.split("/")[0]
            elif "_" in label:
                cluster_id = label.split("_")[0]
            else:
                cluster_id = "general"
                
            # 클러스터별 고유 색상 생성 (해시 활용)
            if cluster_id not in clusters:
                color_hash = hashlib.md5(cluster_id.encode()).hexdigest()[:6]
                clusters[cluster_id] = f"#{color_hash}"
                
            node["cluster_id"] = cluster_id
            node["cluster_color"] = clusters[cluster_id]
            # 클러스터 강조를 위해 기본 색상도 조정 가능
            # node["color"] = clusters[cluster_id] 
            
        return graph_3d

    def _get_color_by_agent(self, agent_name: str) -> str:
        """에이전트별 고유 색상 매핑"""
        colors = {
            "manager": "#ff0000",
            "planner": "#00ff00",
            "coder": "#0000ff",
            "analyst": "#ffff00",
            "researcher": "#00ffff",
            "trend_scout": "#ff00ff"
        }
        return colors.get(agent_name.lower(), "#ffffff")

    def convert_simulation_to_3d(self, current_graph: Dict[str, Any], delta: Dict[str, Any]) -> Dict[str, Any]:
        """예상되는 상태 변화(Simulation)를 고스트 노드 데이터로 변환"""
        ghost_nodes = []
        ghost_edges = []
        
        # 마지막 노드의 위치를 기준으로 배치 (연속성 확보)
        last_pos = current_graph["nodes"][-1]["position"] if current_graph.get("nodes") else {"x": 0, "y": 0, "z": 0}
        
        for i, node_name in enumerate(delta.get("added_nodes", [])):
            pos = {
                "x": last_pos["x"] + 20 + (i * 10),
                "y": last_pos["y"] + 10,
                "z": last_pos["z"] + random.randint(-10, 10)
            }
            ghost_nodes.append({
                "id": f"ghost_{node_name}_{i}",
                "label": f"[PREVIEW] {node_name}",
                "position": pos,
                "is_ghost": True,
                "color": "#ffffff", # 흰색 고스트
                "opacity": 0.4
            })
            # 마지막 실제 노드에서 고스트 노드로 점선 연결 (가정)
            if current_graph.get("nodes"):
                ghost_edges.append({
                    "from": current_graph["nodes"][-1]["id"],
                    "to": f"ghost_{node_name}_{i}",
                    "is_dashed": True
                })
                
        return {"nodes": ghost_nodes, "edges": ghost_edges}

    def convert_intent_to_3d(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자의 장기 목표 및 의도 맵을 3D 시각화 데이터로 변환"""
        if not intent_data or "intent_nodes" not in intent_data:
            return {"nodes": [], "edges": []}
            
        nodes = []
        edges = []
        node_map = {}
        
        # 상단 목표 레이어 배치를 위한 기본 위치 (Y축 높게 설정)
        base_y = 100
        
        for i, item in enumerate(intent_data["intent_nodes"]):
            node_id = item["id"]
            status = item.get("status", "pending")
            
            # 상태별 색상
            color = "#00ff00" if status == "done" else ("#ffff00" if status == "in_progress" else "#888888")
            
            pos = {
                "x": (i % 5) * 30 - 40,
                "y": base_y + (i // 5) * 20,
                "z": 50
            }
            
            nodes.append({
                "id": f"intent_{node_id}",
                "label": f"[GOAL] {item['label']}",
                "position": pos,
                "color": color,
                "status": status,
                "is_intent": True
            })
            node_map[node_id] = pos
            
            if item.get("parent_id") and item["parent_id"] in node_map:
                edges.append({
                    "from": f"intent_{item['parent_id']}",
                    "to": f"intent_{node_id}",
                    "start": node_map[item["parent_id"]],
                    "end": pos,
                    "type": "intent_relation"
                })
                
        return {"nodes": nodes, "edges": edges}

    def _get_color_by_type(self, node_type: str) -> str:
        colors = {
            "class": "#00ff00", # Green
            "function": "#0000ff", # Blue
            "rule": "#ff00ff", # Magenta
            "module": "#ffff00", # Yellow
            "analysis": "#00ffff" # Cyan
        }
        return colors.get(node_type, "#ffffff")
