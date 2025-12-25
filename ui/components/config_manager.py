
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit.shortcuts import radiolist_dialog, message_dialog
from prompt_toolkit.styles import Style
from gortex.core.config import GortexConfig
from gortex.core.auth import GortexAuth
from gortex.ui.themes.palette import Palette

class ConfigManagerUI:
    """터미널 대화형 인터페이스를 통해 시스템 설정을 관리합니다."""

    def __init__(self, console: Console):
        self.console = console
        self.config = GortexConfig()
        self.auth = GortexAuth()
        self.dialog_style = Style.from_dict({
            'dialog': 'bg:#000000',
            'dialog.body': 'bg:#111111 #ffffff',
            'dialog.shadow': 'bg:#000000',
        })

    def run_menu(self):
        """메인 설정 메뉴 실행 (Live 컨텍스트 밖에서 호출되어야 함)"""
        while True:
            choice = radiolist_dialog(
                title="Gortex Configuration",
                text="설정할 항목을 선택하세요:",
                values=[
                    ("provider", f"LLM Provider [{self.auth.get_provider()}]"),
                    ("theme", f"Theme [{self.config.get('theme', 'classic')}]"),
                    ("language", f"Language [{self.config.get('language', 'ko')}]"),
                    ("exit", "Exit & Save"),
                ],
                style=self.dialog_style
            ).run()

            if choice == "exit" or choice is None:
                break
            
            if choice == "provider":
                self._menu_provider()
            elif choice == "theme":
                self._menu_theme()
            elif choice == "language":
                self._menu_language()

        self.console.print(Panel(Text("✅ Configuration Saved & Applied", style=Palette.GREEN), border_style=Palette.GREEN))

    def _menu_provider(self):
        current = self.auth.get_provider().lower()
        new_provider = radiolist_dialog(
            title="Select AI Provider",
            text="사용할 LLM 공급자를 선택하세요. (즉시 반영됨)",
            values=[
                ("gemini", "Gemini (Recommended)"),
                ("ollama", "Ollama (Local Privacy)"),
                ("openai", "OpenAI (GPT-4o)"),
            ],
            default=current,
            style=self.dialog_style
        ).run()

        if new_provider:
            try:
                self.apply_provider(new_provider)
                message_dialog(title="Success", text=f"Active provider switched to: {new_provider.upper()}", style=self.dialog_style).run()
            except Exception as e:
                message_dialog(title="Error", text=f"Failed to switch provider: {e}", style=self.dialog_style).run()

    def _menu_theme(self):
        current = self.config.get("theme", "classic")
        new_theme = radiolist_dialog(
            title="Select Theme",
            text="UI 테마를 선택하세요.",
            values=[("classic", "Classic"), ("cyberpunk", "Cyberpunk"), ("hacker", "Hacker")],
            default=current,
            style=self.dialog_style
        ).run()
        
        if new_theme:
            self.update_setting("theme", new_theme)

    def _menu_language(self):
        current = self.config.get("language", "ko")
        new_lang = radiolist_dialog(
            title="Select Language",
            text="시스템 언어를 선택하세요 (UI 텍스트)",
            values=[("ko", "Korean (한국어)"), ("en", "English")],
            default=current,
            style=self.dialog_style
        ).run()
        
        if new_lang:
            self.update_setting("language", new_lang)

    # --- Logic Methods for Testing ---
    def apply_provider(self, provider_name: str):
        self.auth.set_provider(provider_name)

    def update_setting(self, key: str, value: str):
        self.config.set(key, value)
        # 테스트 통과 및 사용자 피드백을 위해 메시지 출력
        self.console.print(Panel(Text(f"✅ Setting Updated: {key} = {value}", style=Palette.GREEN)))
