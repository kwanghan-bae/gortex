import unittest
from unittest.mock import MagicMock, patch
from gortex.ui.three_js_bridge import ThreeJsBridge

class TestDependencyVisualization(unittest.TestCase):
    def setUp(self):
        self.bridge = ThreeJsBridge()

    def test_apply_clustering(self):
        # 1. Prepare dummy 3D nodes
        nodes = [
            {"id": "core.auth", "label": "core/auth.py"},
            {"id": "core.state", "label": "core/state.py"},
            {"id": "utils.tools", "label": "utils/tools.py"},
            {"id": "agents.coder", "label": "agents/coder.py"}
        ]
        graph = {"nodes": nodes, "edges": []}
        
        # 2. Apply clustering
        clustered = self.bridge.apply_clustering(graph)
        
        # 3. Verify groups
        core_nodes = [n for n in clustered["nodes"] if n["cluster_id"] == "core"]
        utils_nodes = [n for n in clustered["nodes"] if n["cluster_id"] == "utils"]
        
        self.assertEqual(len(core_nodes), 2)
        self.assertEqual(len(utils_nodes), 1)
        # Check colors are assigned
        self.assertTrue("cluster_color" in core_nodes[0])
        # Same cluster should have same color
        self.assertEqual(core_nodes[0]["cluster_color"], core_nodes[1]["cluster_color"])
        # Different clusters should have different colors (probabilistically, md5 hash)
        self.assertNotEqual(core_nodes[0]["cluster_color"], utils_nodes[0]["cluster_color"])

    def test_convert_dependency_graph(self):
        # 1. Prepare raw dependency data
        dep_data = {
            "nodes": [
                {"id": "a", "value": 5, "connections": 2},
                {"id": "b", "value": 3, "connections": 1}
            ],
            "edges": [{"from": "a", "to": "b"}]
        }
        
        # 2. Convert
        result = self.bridge.convert_dependency_graph(dep_data)
        
        # 3. Verify structure
        self.assertIn("nodes", result)
        self.assertIn("edges", result)
        self.assertEqual(len(result["nodes"]), 2)
        self.assertEqual(len(result["edges"]), 1)
        # Check if clustering was applied (cluster_id key existence)
        self.assertIn("cluster_id", result["nodes"][0])

if __name__ == '__main__':
    unittest.main()