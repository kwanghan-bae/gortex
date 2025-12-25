
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

if __name__ == "__main__":
    test_chainmap_serialization()
