import mock
import os
import unittest

import main_app
import util


class TestGetDir(unittest.TestCase):
    def setUp(self):
        super(TestGetDir, self).setUp()
        self.path = "/some/path"
        self.mock_os_listdir = mock.patch("util.os.listdir").start()

    def test_empty_dir(self):
        self.mock_os_listdir.return_value = []

        self.assertEqual(util.get_dir(self.path), [])

    def test_non_empty_dir(self):
        self.mock_os_listdir.return_value = ["house", "tree.txt"]

        resp = [
            {
                "name": "house",
                "owner": mock.ANY,
                "permissions": mock.ANY,
                "size": mock.ANY,
            },
            {
                "name": "tree.txt",
                "owner": mock.ANY,
                "permissions": mock.ANY,
                "size": mock.ANY,
            },
        ]
        self.assertEqual(util.get_dir(self.path), resp)


class TestGetFile(unittest.TestCase):
    def setUp(self):
        super(TestGetFile, self).setUp()
        self.path = "/some/path.txt"
        self.filename = "path.txt"
        self.content = "blabla"

    def test_get_file_success(self):
        with mock.patch(
            "builtins.open", mock.mock_open(read_data=self.content)
        ) as mock_file:
            res = util.get_file(self.path)
            item = [
                {
                    "name": self.filename,
                    "owner": mock.ANY,
                    "size": mock.ANY,
                    "permissions": mock.ANY,
                    "content": self.content,
                }
            ]
            self.assertEqual(res, item)


# class TestGetStats(unittest.TestCase):
#     def setUp(self):
#         super(TestGetStats, self).setUp()
#         self.path = "/some/path"

#         self.mock_os_path_exists = mock.patch("util.os.path.exists").start()

#         self.mock_os_stat = mock.patch("util.os.stat").start()

#     def test_path_does_not_exists(self):
#         self.mock_os_path_exists.return_value = False

#         self.assertEqual(util.get_stats(self.path), (None, None, None))

#     def test_success(self):
#         self.mock_os_path_exists.return_value = True
#         self.mock_os_stat.return_value = mock.MagicMock(
#             st_uid="a", st_size="b", st_mode="c"
#         )

#         self.assertEqual(util.get_stats(self.path), ("a", "b", "c"))


if __name__ == "__main__":
    unittest.main()
