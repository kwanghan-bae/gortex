import re

def count_tokens(text: str) -> int:
    """
    텍스트의 토큰 수를 대략적으로 추정합니다.
    (Backend Agnostic Approximation)
    
    특정 토크나이저 라이브러리(tiktoken 등)를 사용하지 않고,
    일반적인 UTF-8 문자 및 단어 분포를 기반으로 보수적인 근사치를 반환합니다.
    """
    if not text:
        return 0
    
    # 공백으로 나눈 단어 수
    words = len(re.findall(r'\w+', text))
    # 전체 글자 수
    chars = len(text)
    
    # 대략적인 추정치: (글자 수 * 0.5) + 단어 수
    return int((chars * 0.5) + words)

def estimate_cost(tokens: int, model: str = "flash") -> float:
    """
    토큰 당 예상 비용 계산 (1M 토큰 당 가격 기준, USD).
    Gemini 외의 로컬 모델(Ollama)은 비용을 0으로 산정합니다.
    """
    model_lower = model.lower()
    
    # Local Models (Free)
    if any(k in model_lower for k in ["qwen", "llama", "mistral", "gemma", "phi"]):
        return 0.0

    # Gemini Pricing (Approx)
    if "pro" in model_lower:
        # Gemini 1.5 Pro: $3.5 / 1M input (Context Caching 미고려)
        return (tokens / 1_000_000) * 3.5
    elif "flash" in model_lower:
        # Gemini 1.5 Flash: $0.075 / 1M input
        return (tokens / 1_000_000) * 0.075
    
    # Unknown Model (Assume Free or Unknown)
    return 0.0