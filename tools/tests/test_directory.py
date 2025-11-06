from unittest import TestCase
from src.directory.walk_dir import walk_dir
from src.directory.directory_management import DirManagement
from pathlib import Path


class TestDirectory(TestCase):
    def tearDown(self) -> None:
        print("--------------------------")
        return super().tearDown()

    def test_walk_dir(self):
        p = Path(".")
        res = walk_dir(p)
        print(res)

    def test_dirmanagement(self):
        root = Path(".")
        dm = DirManagement(root)
        print(walk_dir(dm.where))

    def test_move_to_child(self):
        root = Path(".")
        dm = DirManagement(root)
        test_dir = Path("tests")
        dm.change_to_child_dir(test_dir)
        self.assertEqual(test_dir, dm.where, "跳转目录失败")

    def test_move_to_parent(self):
        root = Path(".")
        dm = DirManagement(root)
        test_dir = Path("tests")
        # test_dir = Path('..')
        dm.change_to_child_dir(test_dir)
        dm.change_to_parent_dir()
        self.assertEqual(root.resolve(), dm.where, "跳转回根目录失败")

    def test_add_file(self):
        root = Path(".")
        dm = DirManagement(root)
        dm.add_file("test.txt")

    def test_delete_file(self):
        root = Path(".")
        dm = DirManagement(root)
        dm.add_file("test.txt")
        dm.delete_file("test.txt")
