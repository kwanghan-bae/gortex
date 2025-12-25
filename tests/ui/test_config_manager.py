
import unittest
from unittest.mock import MagicMock, patch
from gortex.ui.components.config_manager import ConfigManagerUI
from gortex.core.config import GortexConfig
from gortex.core.auth import GortexAuth

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # 모듈 의존성을 Mock으로 대체
        self.mock_console = MagicMock()
        self.mock_auth = MagicMock(spec=GortexAuth)
        self.mock_config = MagicMock(spec=GortexConfig)
        
        # ConfigManagerUI 인스턴스 생성 (의존성 주입이 없다면 patch 사용)
        with patch('gortex.ui.components.config_manager.GortexAuth', return_value=self.mock_auth), \
             patch('gortex.ui.components.config_manager.GortexConfig', return_value=self.mock_config):
            self.manager = ConfigManagerUI(self.mock_console)

    def test_switch_provider_logic(self):
        """프로바이더 변경 로직 테스트"""
        # given
        new_provider = "openai"
        
        # when
        self.manager.apply_provider(new_provider)
        
        # then
        self.mock_auth.set_provider.assert_called_with("openai")
        self.mock_config.save.assert_not_called() # auth 내부에서 세이브하는지, manager가 하는지 확인 필요.
                                                 # 현재 GortexAuth.set_provider가 _save_config를 부름. 
                                                 # 여기서는 GortexConfig 동기화를 테스트.

    def test_update_config_value(self):
        """설정값(테마) 변경 테스트"""
        # when
        self.manager.update_setting("theme", "cyberpunk")
        
        # then
        self.mock_config.set.assert_called_with("theme", "cyberpunk")
        self.mock_console.print.assert_called()

if __name__ == '__main__':
    unittest.main()
