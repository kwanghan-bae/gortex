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
    "status.error": "red",
    # Agent Specific Colors
    "agent.manager": "bold cyan",
    "agent.planner": "bold yellow",
    "agent.coder": "bold green",
    "agent.researcher": "bold blue",
    "agent.analyst": "bold magenta",
    "agent.trend_scout": "italic magenta",
    "agent.summarizer": "dim cyan",
    "agent.optimizer": "bold red"
})

