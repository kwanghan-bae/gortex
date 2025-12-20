import re

def count_tokens(text: str) -> int:
    """
    텍스트의 토큰 수를 대략적으로 추정합니다.
    Gemini는 문자와 단어 경계에 따라 토큰을 나누지만,
    일반적으로 한글은 1자당 1~2토큰, 영어는 단어당 약 1.3토큰으로 계산됩니다.
    여기서는 보수적으로 (글자 수 / 2) + (단어 수) 정도로 계산합니다.
    """
    if not text:
        return 0
    
    # 공백으로 나눈 단어 수
    words = len(re.findall(r'\w+', text))
    # 전체 글자 수
    chars = len(text)
    
    # 대략적인 추정치 (Gemini API는 실제 응답에서 토큰 정보를 주지만, 
    # google-genai 라이브러리의 응답 객체에서 확인 필요)
    return int((chars * 0.5) + words)

def estimate_cost(tokens: int, model: str = "flash") -> float:
    """토큰 당 예상 비용 계산 (1M 토큰 당 가격 기준)"""
    if "pro" in model.lower():
        # Gemini 1.5 Pro: $3.5 / 1M input
        return (tokens / 1_000_000) * 3.5
    else:
        # Gemini 1.5 Flash: $0.075 / 1M input
        return (tokens / 1_000_000) * 0.075
