import unittest
from googletrans.translator import Translator


class TestTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = Translator()

    def test_translate(self):
        self.assertEqual(self.translator.translate("solution", "vi").text, "giải pháp")


if __name__ == "__main__":
    unittest.main()
