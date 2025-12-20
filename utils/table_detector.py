import re
from typing import List, Optional
from rich.table import Table

def try_render_as_table(text: str, title: str = "Data Table") -> Optional[Table]:
    """
    텍스트 데이터가 테이블 형식(CSV, ASCII Table, ls -l 등)인지 감지하고
    가능하다면 Rich.Table 객체로 변환합니다.
    """
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    if len(lines) < 2:
        return None

    # 1. Markdown 스타일 테이블 (| 구분자)
    if any('|' in line for line in lines[:2]):
        # 파이프로 시작하고 끝나는지, 혹은 중간에 있는지 확인
        header_line = lines[0].strip('|').strip()
        header_parts = [p.strip() for p in header_line.split('|') if p.strip()]
        
        if len(header_parts) >= 2:
            table = Table(title=title, show_header=True, header_style="bold cyan", border_style="magenta")
            for h in header_parts:
                table.add_column(h)
            
            count = 0
            # 두 번째 줄이 구분선(---)인지 확인하고 건너뜀
            start_idx = 1
            if len(lines) > 1 and all(c in '-:| ' for c in lines[1]):
                start_idx = 2
                
            for line in lines[start_idx:]:
                row = [p.strip() for p in line.strip('|').split('|')]
                # 데이터가 부족하면 빈 값으로 채우거나 남는 데이터는 버림
                if len(row) >= len(header_parts):
                    table.add_row(*row[:len(header_parts)])
                    count += 1
            
            if count > 0:
                return table

    # 2. 공백 기반 구분 (ls -l, ps, pandas 출력 등)

    # 첫 줄을 헤더로 가정하고 컬럼 수 파악
    header_parts = re.split(r'\s{2,}', lines[0]) # 2개 이상의 공백으로 구분
    if len(header_parts) < 2:
        # 콤마 기반 구분 (CSV) 시도
        header_parts = lines[0].split(',')
        if len(header_parts) < 2:
            return None
        
        # CSV 처리
        table = Table(title=title, show_header=True, header_style="bold magenta", border_style="yellow")
        for h in header_parts:
            table.add_column(h.strip())
        
        count = 0
        for line in lines[1:]:
            row = line.split(',')
            if len(row) == len(header_parts):
                table.add_row(*[r.strip() for r in row])
                count += 1
        
        return table if count > 0 else None

    # 공백 기반 테이블 처리
    table = Table(title=title, show_header=True, header_style="bold yellow", border_style="blue")
    for h in header_parts:
        table.add_column(h.strip())

    count = 0
    for line in lines[1:]:
        # 헤더와 동일한 패턴으로 분리 시도
        row = re.split(r'\s{2,}', line)
        if len(row) == len(header_parts):
            table.add_row(*[r.strip() for r in row])
            count += 1
        elif len(row) > len(header_parts):
            # 컬럼이 더 많은 경우 (마지막 컬럼에 공백이 포함된 경우 등) 대응
            table.add_row(*[r.strip() for r in row[:len(header_parts)-1]], " ".join(row[len(header_parts)-1:]))
            count += 1

    return table if count > 0 else None
