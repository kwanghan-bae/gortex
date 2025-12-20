from rich.theme import Theme

# KORTEX & Gortex SPEC에 정의된 컬러 팔레트 적용
GORTEX_THEME = Theme({
    "info": "cyan",
    "warn": "bold yellow",
    "err": "bold red",
    "user": "bold green",
    "ai": "bold blue",
    "system": "dim white",
    "mgr.thought": "italic cyan",
    "cdr.exec": "bold green",
    "radar.new": "bold magenta",
    "status.ok": "green",
    "status.busy": "yellow",
    "status.error": "red"
})
