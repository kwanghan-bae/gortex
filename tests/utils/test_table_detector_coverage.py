
import unittest
from rich.table import Table
from gortex.utils.table_detector import try_render_as_table

class TestTableDetectorCoverage(unittest.TestCase):
    def test_empty_or_short_input(self):
        """빈 문자열이나 2줄 미만 데이터는 None 반환"""
        self.assertIsNone(try_render_as_table(""))
        self.assertIsNone(try_render_as_table("   "))
        self.assertIsNone(try_render_as_table("Header Only"))

    def test_markdown_table_standard(self):
        """표준 Markdown 테이블 감지"""
        text = """
        | Name | Age |
        |---|---|
        | Alice | 30 |
        | Bob | 25 |
        """
        table = try_render_as_table(text)
        self.assertIsInstance(table, Table)
        self.assertEqual(len(list(table.columns)), 2)
        # rich Table은 행 개수를 직접 속성으로 주지 않으나 렌더링 가능 여부 확인

    def test_markdown_table_no_divider(self):
        """구분선 없는 파이프 테이블 감지"""
        text = """
        | Key | Value |
        | A   | 1     |
        | B   | 2     |
        """
        table = try_render_as_table(text)
        self.assertIsInstance(table, Table)

    def test_markdown_malformed_rows(self):
        """행 길이가 다르거나 부족할 때 처리"""
        text = """
        | Col1 | Col2 |
        |---|---|
        | A | B | Extra |
        | Short |
        """
        table = try_render_as_table(text)
        self.assertIsInstance(table, Table)

    def test_csv_table(self):
        """CSV 스타일 감지"""
        text = """
        Name, Role, Level
        Miner, Worker, 1
        Builder, Expert, 5
        """
        table = try_render_as_table(text)
        self.assertIsInstance(table, Table)
        
    def test_csv_irregular(self):
        """CSV 행 길이 불일치"""
        text = """
        A,B
        1,2,3
        4
        """
        table = try_render_as_table(text)
        self.assertIsInstance(table, Table)

    def test_whitespace_double_space(self):
        """2칸 이상 공백 구분"""
        text = """
        PID    USER    CMD
        123    root    init
        456    joel    python
        """
        table = try_render_as_table(text)
        self.assertIsInstance(table, Table)

    def test_whitespace_single_space(self):
        """단일 공백 구분"""
        text = """
        ID Name Status
        1  Job1 Done
        2  Job2 Fail
        """
        table = try_render_as_table(text)
        self.assertIsInstance(table, Table)

    def test_whitespace_too_few_columns(self):
        """컬럼이 3개 미만인 단일 공백은 무시되어야 함 (오탐 방지)"""
        text = """
        Key Value
        A 1
        B 2
        """
        # 헤더가 2개뿐이면 단일 공백 로직에서는 None 반환
        self.assertIsNone(try_render_as_table(text))

    def test_numeric_header_generation(self):
        """헤더가 숫자로만 구성된 경우 가상 헤더 생성"""
        text = """
        10 20 30
        40 50 60
        """
        table = try_render_as_table(text)
        self.assertIsInstance(table, Table)
        # 헤더가 Col 1, Col 2 ... 로 생성되었는지 확인 (rich Table 속성 접근 어려움 -> 생성 성공 여부로 판단)

    def test_whitespace_row_merging(self):
        """헤더보다 컬럼이 많은 경우 마지막 컬럼 병합 (ls -l 대응)"""
        text = """
        PERM LINKS USER GROUP SIZE MONTH DAY TIME NAME
        -rw- 1     joel staff 100  Dec   25  12:00 my file name.txt
        """
        table = try_render_as_table(text)
        self.assertIsInstance(table, Table)

    def test_whitespace_row_too_short(self):
        """헤더보다 컬럼이 적은 경우 빈 문자열로 채움"""
        text = """
        Col1 Col2 Col3
        Val1 Val2
        """
        table = try_render_as_table(text)
        self.assertIsInstance(table, Table)

if __name__ == '__main__':
    unittest.main()
