import json
import os
import tempfile
import unittest
from gortex.utils.asset_manager import SynapticAssetManager

class TestSynapticAssetManager(unittest.TestCase):
    def setUp(self):
        self.asset_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.asset_path = self.asset_file.name
        SynapticAssetManager._asset_path = self.asset_path
        SynapticAssetManager._instance = None

    def tearDown(self):
        if os.path.exists(self.asset_path):
            os.remove(self.asset_path)
        SynapticAssetManager._instance = None
        SynapticAssetManager._asset_path = "assets.json"

    def test_get_icon_fallbacks_to_disk(self):
        custom = {"icons": {"custom": "🔥"}}
        with open(self.asset_path, "w", encoding="utf-8") as f:
            json.dump(custom, f)
        manager = SynapticAssetManager()
        self.assertEqual(manager.get_icon("custom"), "🔥")
        self.assertEqual(manager.get_icon("missing", default="?"), "?")

    def test_get_agent_label_defaults(self):
        manager = SynapticAssetManager()
        self.assertEqual(manager.get_agent_label("unknown"), "UNKNOWN")
        self.assertEqual(manager.get_template("reboot"), "[MENTAL REBOOT] 에이전트의 사고가 재설정되었습니다.")

if __name__ == '__main__':
    unittest.main()
