import json
import unittest
from unittest.mock import MagicMock, patch
from gortex.utils.message_queue import GortexMessageQueue

class TestGortexMessageQueue(unittest.TestCase):
    def test_dummy_publish_no_redis(self):
        mq = GortexMessageQueue()
        mq.client = None
        self.assertIsNone(mq.publish("channel", {"a": 1}))

    @patch("gortex.utils.message_queue.redis")
    def test_publish_with_client(self, mock_redis):
        mock_client = MagicMock()
        mock_redis.from_url.return_value = mock_client
        mq = GortexMessageQueue(url="redis://localhost:6379")
        mq.publish("channel", {"foo": "bar"})
        mock_client.publish.assert_called()

    @patch("gortex.utils.message_queue.redis")
    def test_push_and_pop_task(self, mock_redis):
        mock_client = MagicMock()
        mock_redis.from_url.return_value = mock_client
        mq = GortexMessageQueue()
        task = {"task": "index"}
        mq.push_task("queue", task)
        mock_client.lpush.assert_called()
        mock_client.brpop.return_value = ("queue", json.dumps(task).encode())
        result = mq.pop_task("queue")
        self.assertEqual(result, task)

if __name__ == '__main__':
    unittest.main()
