import re
from typing import List, Optional
from rich.table import Table

def try_render_as_table(text: str, title: str = "Data Table") -> Optional[Table]:
    """
    텍스트 데이터가 테이블 형식(CSV, ASCII Table, Markdown, ls -l 등)인지 감지하고
    가능하다면 Rich.Table 객체로 변환합니다.
    """
    # 1. 전처리: 빈 줄 제거 및 각 줄의 양 끝 공백 제거
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    if len(lines) < 2:
        return None

    # --- Markdown 스타일 테이블 감지 (| 구분자) ---
    # 파이프 기호가 포함된 라인이 2개 이상이면 마크다운 테이블로 의심
    if sum(1 for line in lines[:3] if '|' in line) >= 1:
        header_line = lines[0].strip('|')
        header_parts = [p.strip() for p in header_line.split('|') if p.strip()]
        
        if len(header_parts) >= 2:
            table = Table(title=title, show_header=True, header_style="bold cyan", border_style="magenta")
            for h in header_parts:
                table.add_column(h)
            
            count = 0
            start_idx = 1
            # Markdown 구분선 (---|---|---) 감지 및 건너뛰기
            if len(lines) > 1 and re.match(r'^[|:\s\-]+$', lines[1]):
                start_idx = 2
                
            for line in lines[start_idx:]:
                if '|' not in line: continue
                # 파이프로 나누기 (양 끝 파이프 제거 후)
                row = [p.strip() for p in line.strip('|').split('|')]
                
                # 데이터가 부족하면 빈 값으로 채우거나 남는 데이터는 버림
                if len(row) >= len(header_parts):
                    table.add_row(*row[:len(header_parts)])
                    count += 1
                elif len(row) > 0:
                    # 부족한 경우 빈 문자열로 채움
                    row += [""] * (len(header_parts) - len(row))
                    table.add_row(*row)
                    count += 1
            
            if count > 0:
                return table

    # --- CSV 스타일 감지 (콤마 구분) ---
    if ',' in lines[0] and len(lines[0].split(',')) >= 2:
        header_parts = [p.strip() for p in lines[0].split(',')]
        table = Table(title=title, show_header=True, header_style="bold magenta", border_style="yellow")
        for h in header_parts:
            table.add_column(h)
        
        count = 0
        for line in lines[1:]:
            row = [p.strip() for p in line.split(',')]
            if len(row) >= len(header_parts):
                table.add_row(*row[:len(header_parts)])
                count += 1
        if count > 0:
            return table

    # --- 공백 기반 테이블 감지 (ls -l, pandas 출력 등) ---
    # 먼저 2개 이상의 공백 또는 탭으로 구분된 경우 시도
    header_parts = re.split(r'\s{2,}', lines[0])
    
    # 만약 2개 이상의 공백으로 나뉘지 않는다면 단일 공백 시도
    if len(header_parts) < 2:
        header_parts = lines[0].split()
        # 단일 공백인 경우, 최소 3개 이상의 컬럼이 있어야 테이블로 간주 (오탐 방지)
        if len(header_parts) < 3:
            return None

    table = Table(title=title, show_header=True, header_style="bold yellow", border_style="blue")
    for h in header_parts:
        table.add_column(h)

    count = 0
    for line in lines[1:]:
        # 먼저 2개 이상의 공백으로 분리 시도
        row = re.split(r'\s{2,}', line)
        
        # 만약 컬럼 수가 안 맞으면 단일 공백으로 분리 시도
        if len(row) != len(header_parts):
            row = line.split()
            
        if len(row) == len(header_parts):
            table.add_row(*row)
            count += 1
        elif len(row) > len(header_parts):
            # 컬럼이 더 많은 경우 마지막 컬럼에 합침 (예: 파일명에 공백이 있는 경우)
            table.add_row(*row[:len(header_parts)-1], " ".join(row[len(header_parts)-1:]))
            count += 1
        elif len(row) > 0 and len(row) < len(header_parts):
            # 부족한 경우 빈 값으로 채움
            row += [""] * (len(header_parts) - len(row))
            table.add_row(*row)
            count += 1

    return table if count > 0 else None
