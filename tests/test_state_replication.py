import unittest
import os
import json
from datetime import datetime
from langchain_core.messages import AIMessage
from gortex.core.persistence import DistributedSaver

class TestStateReplication(unittest.TestCase):
    def setUp(self):
        self.mirror_path = "tests/test_state_mirror.json"
        self.saver = DistributedSaver(mirror_path=self.mirror_path)

    def tearDown(self):
        if os.path.exists(self.mirror_path):
            os.remove(self.mirror_path)
        if os.path.exists(self.mirror_path + ".tmp"):
            os.remove(self.mirror_path + ".tmp")

    def test_put_replicates_to_file(self):
        """상태 저장 시 파일로 정상 복제되는지 테스트"""
        # LangGraph 표준 컨피그 구조
        config = {
            "configurable": {
                "thread_id": "t1",
                "checkpoint_ns": ""
            }
        }
        
        checkpoint = {
            "id": "c1",
            "ts": datetime.now().isoformat(),
            "channel_values": {
                "messages": [AIMessage(content="Hello Gortex v3.0")],
                "counter": 100
            }
        }
        metadata = {"step": "test"}
        
        # 1. 저장 실행
        self.saver.put(config, checkpoint, metadata, {})
        
        # 2. 미러 파일 존재 확인
        self.assertTrue(os.path.exists(self.mirror_path))
        
        # 3. 내용 정합성 확인
        with open(self.mirror_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["config"]["configurable"]["thread_id"], "t1")
            
            # AIMessage 직렬화 검증
            msgs = data["checkpoint"]["channel_values"]["messages"]
            self.assertEqual(msgs[0]["type"], "ai")
            self.assertEqual(msgs[0]["content"], "Hello Gortex v3.0")
            
            self.assertEqual(data["checkpoint"]["channel_values"]["counter"], 100)

if __name__ == '__main__':
    unittest.main()