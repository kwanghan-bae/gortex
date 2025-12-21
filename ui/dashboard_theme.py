from rich.theme import Theme

# 기본 공통 스타일
BASE_STYLES = {
    "info": "cyan",
    "warn": "bold yellow",
    "err": "bold red",
    "user": "bold green",
    "ai": "bold blue",
    "system": "dim white",
    "status.ok": "green",
    "status.busy": "yellow",
    "status.error": "red",
    "agent.manager": "bold cyan",
    "agent.planner": "bold yellow",
    "agent.coder": "bold green",
    "agent.researcher": "bold blue",
    "agent.analyst": "bold magenta",
    "agent.trend_scout": "italic magenta",
    "agent.summarizer": "dim cyan",
    "agent.optimizer": "bold red"
}

THEMES = {
    "classic": Theme(BASE_STYLES),
    "matrix": Theme({
        **BASE_STYLES,
        "user": "bold green on black",
        "ai": "bold green on black",
        "system": "dim green",
        "agent.manager": "bold green",
        "info": "green"
    }),
    "cyberpunk": Theme({
        **BASE_STYLES,
        "user": "bold magenta",
        "ai": "bold cyan",
        "agent.manager": "bold yellow",
        "info": "bright_magenta"
    }),
    "monochrome": Theme({
        k: "dim white" if "agent" not in k else "bold white" 
        for k in BASE_STYLES
    })
}

class ThemeManager:
    def __init__(self, default_theme: str = "classic"):
        self.current_theme_name = default_theme
        
    def get_theme(self, name: str = None) -> Theme:
        name = name or self.current_theme_name
        return THEMES.get(name, THEMES["classic"])

    def set_theme(self, name: str):
        if name in THEMES:
            self.current_theme_name = name
            return True
        return False

    def get_color(self, style_name: str) -> str:
        """현재 테마에서 스타일 이름에 해당하는 색상 반환"""
        theme = self.get_theme()
        return theme.styles.get(style_name, "white")

    def list_themes(self) -> list:
        return list(THEMES.keys())

# 하위 호환성을 위한 기본 테마 객체 유지
GORTEX_THEME = THEMES["classic"]