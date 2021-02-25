import unittest
from unittest.mock import patch

import main
import os.path


class TestGetStats(unittest.TestCase):

    @patch("os.path.exists")
    def test_filepath_does_not_exist(self, mock_exists):
        mock_exists.return_value = True
        bad_path = "m/m/m"
        self.assertEqual(main.get_stats(bad_path), (None, None, None), "Should return Nones")


class TestGetFile(unittest.TestCase):

    @patch("os.path.exists")
    def test_filepath_does_not_exist(self, mock_exists):
        mock_exists.return_value = True
        bad_path = "m/m/m"
        self.assertEqual(main.get_stats(bad_path), (None, None, None), "Should return Nones")

if __name__ == '__main__':
    unittest.main()
