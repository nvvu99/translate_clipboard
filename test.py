import unittest
from googletrans import translate_text


class TestTranslator(unittest.TestCase):
    def test_translate(self):
        self.assertEqual(translate_text("vi", "solution"), "giải pháp")


if __name__ == "__main__":
    unittest.main()
