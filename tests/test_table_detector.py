import unittest
from gortex.utils.table_detector import try_render_as_table

class TestTableDetector(unittest.TestCase):
    def test_markdown_table(self):
        text = "| Name | Value |\n|---|---|\n| A | 1 |\n| B | 2 |"
        table = try_render_as_table(text)
        self.assertIsNotNone(table)
        self.assertEqual(len(table.columns), 2)
        self.assertEqual(table.columns[0].header, "Name")

    def test_csv_table(self):
        text = "name,value\nalpha,10\nbeta,20"
        table = try_render_as_table(text)
        self.assertIsNotNone(table)
        self.assertEqual(len(table.columns), 2)
        self.assertEqual(table.columns[1].header, "value")

    def test_whitespace_table(self):
        text = "Agent  Status  Score\nCoder   Active  100\nPlanner Idle    80"
        table = try_render_as_table(text)
        self.assertIsNotNone(table)
        self.assertEqual(len(table.columns), 3)
        self.assertTrue(any(col.header.startswith("Agent") for col in table.columns))

    def test_not_a_table(self):
        table = try_render_as_table("single line")
        self.assertIsNone(table)

if __name__ == '__main__':
    unittest.main()
