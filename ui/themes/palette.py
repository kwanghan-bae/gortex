"""
Gortex 프리미엄 색상 팔레트.
Hex 기반의 정교한 색상 제어를 위해 정의됨.
"""

class Palette:
    # Core Colors
    BACKGROUND = "#1E1E2E"
    FOREGROUND = "#CDD6F4"
    
    # Accents (inspired by Catppuccin/Gemini)
    BLUE = "#89B4FA"
    CYAN = "#89DCEB"
    GREEN = "#A6E3A1"
    YELLOW = "#F9E2AF"
    RED = "#F38BA8"
    MAGENTA = "#CBA6F7"
    MAUVE = "#8839EF"
    
    # UI Elements
    GRAY = "#6C7086"
    DARK_GRAY = "#313244"
    
    # Gradients (for Header)
    GRADIENT_GEMINI = ["#4796E4", "#847ACE", "#C3677F"]
    GRADIENT_GORTEX = ["#A6E3A1", "#89DCEB", "#89B4FA"]

def get_agent_style(agent_name: str) -> str:
    mapping = {
        "manager": Palette.CYAN,
        "planner": Palette.YELLOW,
        "coder": Palette.GREEN,
        "researcher": Palette.BLUE,
        "analyst": Palette.MAGENTA,
        "system": Palette.GRAY
    }
    return mapping.get(agent_name.lower(), Palette.FOREGROUND)
