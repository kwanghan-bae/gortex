import unittest
from gortex.ui.three_js_bridge import ThreeJsBridge

class TestThreeJsBridge(unittest.TestCase):
    def test_convert_thought_to_3d_creates_edges(self):
        bridge = ThreeJsBridge()
        thought_tree = [
            {"id": "n1", "text": "start", "type": "analysis"},
            {"id": "n2", "parent_id": "n1", "text": "child", "type": "design", "visual_payload": {"data": 1}},
            {"id": "n3", "parent_id": "n2", "text": "leaf", "type": "decision", "certainty": 0.9}
        ]
        converted = bridge.convert_thought_to_3d(thought_tree)
        self.assertEqual(len(converted["nodes"]), 3)
        self.assertEqual(len(converted["edges"]), 2)
        node_ids = {node["id"] for node in converted["nodes"]}
        self.assertSetEqual(node_ids, {"n1", "n2", "n3"})
        edge_targets = {edge["to"] for edge in converted["edges"]}
        self.assertIn("n2", edge_targets)
        self.assertIn("n3", edge_targets)

if __name__ == '__main__':
    unittest.main()
