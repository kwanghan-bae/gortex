
import os
import unittest

class TestBannedLibs(unittest.TestCase):
    def test_no_prompt_toolkit_in_active_input_logic(self):
        """test_no_prompt_toolkit_in_active_input_logic: main.py에서 prompt_toolkit을 사용하여 입력을 받는 로직이 활성화되지 않았는지 검사"""
        target_file = "gortex/main.py"
        if not os.path.exists(target_file):
            target_file = "main.py" # try root if not found

        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. prompt_toolkit import가 있더라도, get_user_input 함수 내에서 사용되지 않는지 확인
        # (완전 제거는 힘드므로, get_user_input 내에서 prompt_session.prompt_async 호출이 주석 처리되었거나 없는지 확인)
        
        # 단순 문자열 매칭으로 검사
        lines = content.split('\n')
        in_get_user_input = False
        violation_found = False
        
        for line in lines:
            stripped = line.strip()
            if "def get_user_input" in stripped:
                in_get_user_input = True
                continue
            
            if in_get_user_input and stripped.startswith("def "): # 함수 끝
                in_get_user_input = False
            
            if in_get_user_input:
                # get_user_input 내부에서 prompt_session 사용 감지
                # 주석(#)으로 시작하지 않는 줄에서 prompt_session 호출이 있으면 위반
                if "prompt_session" in stripped and not stripped.startswith("#"):
                     # 예외: logger.info("...prompt_session...") 같은 경우 제외해야 하지만 여기선 단순하게
                     if "prompt_async" in stripped:
                         violation_found = True
                         print(f"Violation: {stripped}")

        self.assertFalse(violation_found, 
            "Critical Regression: 'prompt_toolkit' is active in get_user_input! This caused input hang/freeze issues. Use console.input instead.")

if __name__ == '__main__':
    unittest.main()
