import mock
import os
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

import main_app


class TestListFiles(unittest.TestCase):
    def setUp(self):
        super(TestListFiles, self).setUp()
        os.environ["ROOT_DIR"] = ""
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
            os.environ["ROOT_DIR"] + "Documents/work"
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

        self.assertEqual(response.status_code, 403)
        self.assertTrue("Can only read .txt files" in response.text)


class TestGetHostPath(unittest.TestCase):
    def setUp(self):
        super(TestGetHostPath, self).setUp()
        self.path = "/some/path"

        self.mock_os_path_exists = mock.patch("util.os.path.exists").start()

        self.mock_os_stat = mock.patch("util.os.stat").start()

    def test_normal_path(self):
        path = "/files/Users/someone/home"
        sub_path = "/Users/someone/home"
        self.assertEqual(main_app.get_host_path(path), sub_path)

    def test_path_with_multiple_file_root(self):
        path = "/files/Users/someone/files/home"
        sub_path = "/Users/someone/files/home"
        self.assertEqual(main_app.get_host_path(path), sub_path)


class TestSafePathJoin(unittest.TestCase):
    def test_no_path_no_root(self):
        self.assertEqual(main_app.safe_path_join(path="", root=""), "")

    def test_no_path(self):
        self.assertEqual(main_app.safe_path_join(path="", root="/home"), "/home")

    def test_prepend_slash_no_root(self):
        self.assertEqual(
            main_app.safe_path_join(path="/file.txt", root=""), "/file.txt"
        )

    def test_prepend_slash_root_and_path(self):
        self.assertEqual(
            main_app.safe_path_join(path="/nested/file", root="/root"),
            "/root/nested/file",
        )

    def test_root_and_path(self):
        self.assertEqual(
            main_app.safe_path_join(path="home", root="/root"), "/root/home"
        )

    def test_no_root(self):
        self.assertEqual(main_app.safe_path_join(path="home", root=""), "home")


if __name__ == "__main__":
    unittest.main()
