import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.core.mq import GortexMessageBus

class TestGortexMQ(unittest.TestCase):
    def setUp(self):
        # Redis 클라이언트를 모킹하여 테스트
        self.mock_redis = MagicMock()
        with patch("redis.from_url", return_value=self.mock_redis):
            self.mq = GortexMessageBus(url="redis://mock:6379/0")

    def test_publish_event(self):
        """이벤트 발행 시 Redis publish가 올바른 형식으로 호출되는지 테스트"""
        payload = {"data": "test"}
        self.mq.publish_event("test_chan", "TestAgent", "test_event", payload)
        
        self.assertTrue(self.mock_redis.publish.called)
        args = self.mock_redis.publish.call_args[0]
        self.assertEqual(args[0], "test_chan")
        
        message = json.loads(args[1])
        self.assertEqual(message["agent"], "TestAgent")
        self.assertEqual(message["type"], "test_event")
        self.assertEqual(message["payload"], payload)

    def test_enqueue_task(self):
        """작업 추가 시 Redis rpush가 호출되는지 테스트"""
        task = {"cmd": "analyze"}
        self.mq.enqueue_task("task_queue", task)
        
        self.assertTrue(self.mock_redis.rpush.called)
        args = self.mock_redis.rpush.call_args[0]
        self.assertEqual(args[0], "task_queue")
        self.assertEqual(json.loads(args[1]), task)

    def test_dummy_mode_resilience(self):
        """Redis가 없을 때(Dummy mode) 에러 없이 로그만 남기는지 테스트"""
        with patch("gortex.core.mq.redis", None):
            dummy_mq = GortexMessageBus()
            self.assertFalse(dummy_mq.is_connected)
            # 아래 호출들이 예외를 발생시키지 않아야 함
            dummy_mq.publish_event("a", "b", "c", {})
            dummy_mq.enqueue_task("q", {})

if __name__ == "__main__":
    unittest.main()