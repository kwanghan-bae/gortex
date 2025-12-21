import unittest
from gortex.utils.translator import i18n

class TestGortexLocalization(unittest.TestCase):
    def test_translation_key_mapping(self):
        """한국어 및 영어 사전의 핵심 키값이 존재하고 올바르게 매핑되는지 테스트"""
        # 한국어 테스트
        msg_ko = i18n.t("task.all_completed", lang="ko")
        self.assertEqual(msg_ko, "모든 계획된 작업을 완료했습니다.")
        
        # 영어 테스트
        msg_en = i18n.t("task.all_completed", lang="en")
        self.assertEqual(msg_en, "All planned tasks have been successfully completed.")

    def test_variable_substitution(self):
        """메시지 내 변수 치환({goal}, {steps} 등)이 정상적으로 이루어지는지 테스트"""
        res = i18n.t("task.plan_established", lang="ko", goal="테스트", steps=5)
        self.assertIn("계획을 수립했습니다: 테스트 (5 단계)", res)
        
        res_en = i18n.t("task.plan_established", lang="en", goal="Test", steps=3)
        self.assertIn("New plan established: Test (3 steps)", res_en)

    def test_missing_key_fallback(self):
        """존재하지 않는 키 요청 시 키 자체를 반환하는지 테스트 (안전 모드)"""
        res = i18n.t("non.existent.key")
        self.assertEqual(res, "non.existent.key")

if __name__ == '__main__':
    unittest.main()
