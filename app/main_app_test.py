import mock
import os
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

import main_app


class TestListFiles(unittest.TestCase):
    def setUp(self):
        super(TestListFiles, self).setUp()
        self.client = TestClient(main_app.app)

        self.get_path_items_patcher = mock.patch("main_app.get_path_items")
        self.mock_get_path_items = self.get_path_items_patcher.start()

        self.mock_os_path_exists = mock.patch("main_app.os.path.exists").start()

    def test_list_files_success(self):
        self.mock_get_path_items.return_value = [{"Hello": "World"}]

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("count" in response.json())
        self.assertTrue("items" in response.json())
        self.assertEqual(len(response.json().get("items")), 1)

    def test_list_files_success_with_query(self):
        response = self.client.get("/?q=Documents/work")

        self.assertEqual(response.status_code, 200)
        self.mock_get_path_items.assert_called_once_with(
            main_app.ROOT_DIR + "Documents/work"
        )

    def test_list_files_path_does_not_exists(self):
        self.mock_get_path_items = self.get_path_items_patcher.stop()
        self.mock_os_path_exists.return_value = False

        response = self.client.get("/")

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            "does not exist or you don't have permissions to access it" in response.text
        )

    def test_list_files_not_txt(self):
        self.mock_get_path_items = self.get_path_items_patcher.stop()
        self.mock_os_path_exists.return_value = True

        response = self.client.get("/?q=cat.png")

        self.assertEqual(response.status_code, 404)
        self.assertTrue("Can only read .txt files" in response.text)


class TestGetDir(unittest.TestCase):
    def setUp(self):
        super(TestGetDir, self).setUp()
        self.path = "/some/path"
        self.mock_os_listdir = mock.patch("main_app.os.listdir").start()

    def test_empty_dir(self):
        self.mock_os_listdir.return_value = []

        self.assertEqual(main_app.get_dir(self.path), [])

    def test_non_empty_dir(self):
        self.mock_os_listdir.return_value = ["house", "tree.txt"]

        resp = [
            {"name": "house", "owner": None, "permissions": None, "size": None},
            {"name": "tree.txt", "owner": None, "permissions": None, "size": None},
        ]
        self.assertEqual(main_app.get_dir(self.path), resp)


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
            res = main_app.get_file(self.path)
            item = [
                {
                    "name": self.filename,
                    "owner": None,
                    "size": None,
                    "permissions": None,
                    "content": self.content,
                }
            ]
            self.assertEqual(res, item)


class TestGetStats(unittest.TestCase):
    def setUp(self):
        super(TestGetStats, self).setUp()
        self.path = "/some/path"

        self.mock_os_path_exists = mock.patch("main_app.os.path.exists").start()

        self.mock_os_stat = mock.patch("main_app.os.stat").start()

    def test_path_does_not_exists(self):
        self.mock_os_path_exists.return_value = False

        self.assertEqual(main_app.get_stats(self.path), (None, None, None))

    def test_success(self):
        self.mock_os_path_exists.return_value = True
        self.mock_os_stat.return_value = mock.MagicMock(
            st_uid="a", st_size="b", st_mode="c"
        )

        self.assertEqual(main_app.get_stats(self.path), ("a", "b", "c"))


class TestGetHostPath(unittest.TestCase):
    def setUp(self):
        super(TestGetHostPath, self).setUp()
        self.path = "/some/path"

        self.mock_os_path_exists = mock.patch("main_app.os.path.exists").start()

        self.mock_os_stat = mock.patch("main_app.os.stat").start()

    def test_normal_path(self):
        path = "/files/Users/someone/home"
        sub_path = "/Users/someone/home"
        self.assertEqual(main_app.get_host_path(path), sub_path)

    def test_path_with_multiple_file_root(self):
        path = "/files/Users/someone/files/home"
        sub_path = "/Users/someone/files/home"
        self.assertEqual(main_app.get_host_path(path), sub_path)


if __name__ == "__main__":
    unittest.main()