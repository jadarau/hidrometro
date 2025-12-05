import os
import unittest

from src.ocr import run_ocr

class TestOCR(unittest.TestCase):
    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            run_ocr("nonexistent.png")

if __name__ == "__main__":
    unittest.main()
