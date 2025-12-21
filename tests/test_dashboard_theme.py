import unittest
from gortex.ui.dashboard_theme import ThemeManager, THEMES

class TestDashboardTheme(unittest.TestCase):
    def setUp(self):
        self.theme_manager = ThemeManager()

    def test_get_theme_default(self):
        theme = self.theme_manager.get_theme()
        self.assertIsNotNone(theme)

    def test_set_theme_valid(self):
        res = self.theme_manager.set_theme("matrix")
        self.assertTrue(res)
        self.assertEqual(self.theme_manager.current_theme_name, "matrix")

    def test_set_theme_invalid(self):
        res = self.theme_manager.set_theme("non_existent")
        self.assertFalse(res)

    def test_get_color(self):
        color = self.theme_manager.get_color("agent.manager")
        self.assertIn("cyan", str(color).lower())
        
        # fallback case
        color_missing = self.theme_manager.get_color("non_existent_style")
        self.assertEqual(color_missing, "white")

    def test_list_themes(self):
        themes = self.theme_manager.list_themes()
        self.assertIn("classic", themes)
        self.assertIn("cyberpunk", themes)

if __name__ == "__main__":
    unittest.main()
