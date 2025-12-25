
import json
import logging
from collections import ChainMap
from gortex.core.persistence import DistributedSaver

# 로깅 설정
logging.basicConfig(level=logging.INFO)

def test_chainmap_serialization():
    print("🧪 Testing ChainMap Serialization Fix...")
    
    # 1. ChainMap 생성
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'b': 3, 'c': 4}
    chain = ChainMap(dict1, dict2) # {'a': 1, 'b': 2, 'c': 4} (b는 dict1 우선)
    
    print(f"📦 ChainMap Object: {chain}")
    
    # 2. Saver 인스턴스 (Mocking primary)
    saver = DistributedSaver(primary_saver=None, mirror_path="logs/test_mirror.json")
    
    # 3. Serialization 시도
    try:
        serialized = saver._make_serializable(chain)
        print(f"✅ Serialized Output: {serialized}")
        
        # 4. JSON Dump 검증
        json_output = json.dumps(serialized)
        print(f"✅ JSON Dump Success: {json_output}")
        
        # 값 검증
        assert serialized['a'] == 1
        assert serialized['b'] == 2 # First dict wins
        assert serialized['c'] == 4
        print("🎉 Verification Passed!")
        
    except Exception as e:
        print(f"❌ Serialization Failed: {e}")
        exit(1)

def test_config_field_failure():
    print("\n🧪 Testing 'config' field serialization loop...")
    saver = DistributedSaver(primary_saver=None, mirror_path="logs/test_mirror_config.json")
    
    # ChainMap in config (This was the bug)
    config = ChainMap({'a': 1}, {'b': 2})
    checkpoint = {"some": "data"}
    metadata = {"meta": "data"}
    
    # Simulate _replicate logic manually (since it's internal)
    try:
        serializable_state = {
            "v": 3,
            "ts": 123456789.0,
            "config": config, # <--- ⚠️ This is where it fails if not wrapped
            "checkpoint": saver._make_serializable(checkpoint),
            "metadata": saver._make_serializable(metadata)
        }
        
        # This roughly simulates what json.dump does inside _replicate
        # But wait, _replicate calls json.dump.
        # So we should call _replicate directly if we can, or simulate the json.dump failure.
        
        # Let's call _replicate if we can mock os.replace
        saver._replicate(config, checkpoint, metadata)
        print("🎉 _replicate passed with ChainMap in config!")
        
    except TypeError as e:
        if "ChainMap" in str(e) and "not JSON serializable" in str(e):
             print(f"✅ Caught Expected Error (Bug Reproduced): {e}")
             return
        print(f"❌ Unexpected TypeError: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        
    # If we are here after fixing the bug, we should actually expect PASS.
    # But right now we are verifying if it fails or passes.
    # User said it failed.
    pass

if __name__ == "__main__":
    test_chainmap_serialization()
    test_config_field_failure()
