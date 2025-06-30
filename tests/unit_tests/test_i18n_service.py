import unittest
from infrastructure.i18n.i18n_service import I18nService
from cli.i18n import MESSAGES

class TestI18nService(unittest.TestCase):
    def setUp(self):
        self.i18n = I18nService(MESSAGES, default_lang="es")

    def test_get_message_es(self):
        msg = self.i18n.get("MENU_MAIN_TITLE", lang="es")
        self.assertEqual(msg, "Menú Principal")

    def test_get_message_en(self):
        msg = self.i18n.get("MENU_MAIN_TITLE", lang="en")
        self.assertEqual(msg, "Main Menu")

    def test_get_message_default(self):
        msg = self.i18n.get("MENU_MAIN_TITLE")
        self.assertEqual(msg, "Menú Principal")

    def test_get_message_with_kwargs(self):
        msg = self.i18n.get("SUCCESS_REFACTOR", lang="es", output_file="file.gcode")
        self.assertIn("file.gcode", msg)

    def test_fallback_to_key(self):
        msg = self.i18n.get("nonexistent_key", lang="es")
        self.assertEqual(msg, "nonexistent_key")

if __name__ == "__main__":
    unittest.main()
