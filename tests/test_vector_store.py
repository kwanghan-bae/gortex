import json
import os
import tempfile
import unittest
from unittest.mock import patch

from gortex.utils.vector_store import LongTermMemory

class TestLongTermMemory(unittest.TestCase):
    def test_memorize_and_recall_increments_usage(self):
        with patch.object(LongTermMemory, "_get_embedding", return_value=[1.0, 0.0]):
            with tempfile.TemporaryDirectory() as tmpdir:
                ltm = LongTermMemory(store_dir=tmpdir)
                ltm.memorize("test knowledge", namespace="test_ns")
                results = ltm.recall("test knowledge", namespace="test_ns", limit=2)
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]["score"], 1.0)
                shard_path = os.path.join(tmpdir, "shard_test_ns.json")
                with open(shard_path, "r", encoding='utf-8') as f:
                    data = json.load(f)
                self.assertEqual(data[0]["usage_count"], 1)

    def test_embedding_failure_falls_back_to_zero_vector(self):
        with patch("gortex.utils.vector_store.GortexAuth.get_current_client", side_effect=Exception("failure")):
            with tempfile.TemporaryDirectory() as tmpdir:
                ltm = LongTermMemory(store_dir=tmpdir)
                vector = ltm._get_embedding("fallback")
                self.assertEqual(len(vector), 768)
                self.assertTrue(all(v == 0.0 for v in vector))

    def test_recall_filters_low_similarity(self):
        with patch.object(LongTermMemory, "_get_embedding", return_value=[1.0, 0.0]):
            with tempfile.TemporaryDirectory() as tmpdir:
                ltm = LongTermMemory(store_dir=tmpdir)
                ltm.memorize("entry", namespace="low")
                # manually reduce vector to produce low similarity
                ltm.shards["low"][0]["vector"] = [0.0, 0.0]
                results = ltm.recall("entry", namespace="low", limit=1)
                self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
