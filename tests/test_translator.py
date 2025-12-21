import json
import unittest
from unittest.mock import MagicMock, patch
from gortex.utils.translator import SystemTranslator, SynapticTranslator

class TestSystemTranslator(unittest.TestCase):
    @patch.object(SystemTranslator, "_load_all_dicts")
    def test_t_returns_formatted_message(self, _):
        translator = SystemTranslator()
        translator.dictionaries = {
            "ko": {"greet": "안녕 {name}"},
            "en": {"greet": "Hello {name}"}
        }
        self.assertEqual(translator.t("greet", lang="en", name="Joel"), "Hello Joel")
        self.assertEqual(translator.t("missing", lang="en"), "missing")

    @patch.object(SystemTranslator, "_load_all_dicts")
    def test_t_handles_format_errors(self, _):
        translator = SystemTranslator()
        translator.dictionaries = {"ko": {"bad": "Hello {missing}"}}
        self.assertEqual(translator.t("bad", lang="ko"), "Hello {missing}")

class TestSynapticTranslator(unittest.TestCase):
    def setUp(self):
        self.auth_mock = MagicMock()
        self.auth_context = patch("gortex.utils.translator.GortexAuth", return_value=self.auth_mock)
        self.auth_context.start()
        self.addCleanup(self.auth_context.stop)
        self.translator = SynapticTranslator()

    def test_detect_and_translate_success(self):
        response = MagicMock()
        response.text = json.dumps({
            "detected_lang": "en",
            "is_korean": False,
            "translated_text": "Hi there",
            "confidence": 0.98
        })
        self.auth_mock.generate.return_value = response
        result = self.translator.detect_and_translate("Hello", target_lang="ko")
        self.assertEqual(result["detected_lang"], "en")
        self.assertEqual(result["translated_text"], "Hi there")

    def test_translate_response_handles_failure(self):
        self.auth_mock.generate.side_effect = RuntimeError("no api")
        text = "안녕하세요"
        self.assertEqual(self.translator.translate_response(text, "en"), text)

    def test_translate_batch_returns_original_on_error(self):
        self.auth_mock.generate.side_effect = RuntimeError("boom")
        payload = {"thought": "idea"}
        result = self.translator.translate_batch(payload, "en")
        self.assertEqual(result, payload)

    def test_translate_batch_short_circuits_for_korean(self):
        payload = {"thought": "idea"}
        result = self.translator.translate_batch(payload, "ko")
        self.assertEqual(result, payload)
