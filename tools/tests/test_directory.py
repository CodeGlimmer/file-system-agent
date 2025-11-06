"""
测试 WorkingDir 类的所有功能
"""
import pytest
import sys
import os
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.file_system_tools.working_dir import WorkingDir  # noqa: E402


class TestWorkingDirInit:
    """测试 WorkingDir 初始化功能"""

    def test_init_with_valid_path(self, tmp_path):
        """测试使用有效路径初始化"""
        wd = WorkingDir(tmp_path)
        assert wd.where == tmp_path.resolve()
        assert wd._root == tmp_path.resolve()
        assert len(wd.trace) == 1
        assert wd.trace[0] == tmp_path.resolve()

    def test_init_with_nonexistent_path(self):
        """测试使用不存在的路径初始化，应该抛出 FileNotFoundError"""
        nonexistent_path = Path("/nonexistent/path/to/nowhere")
        with pytest.raises(FileNotFoundError, match="路径.*不存在"):
            WorkingDir(nonexistent_path)

    def test_init_resolves_relative_path(self, tmp_path):
        """测试初始化时会将相对路径转换为绝对路径"""
        # 创建一个子目录
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        # 切换到临时目录
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            wd = WorkingDir(Path("subdir"))
            assert wd.where == subdir.resolve()
            assert wd.where.is_absolute()
        finally:
            os.chdir(original_cwd)


class TestChangeToChildDir:
    """测试切换到子目录的功能"""

    def test_change_to_valid_child_dir(self, tmp_path):
        """测试切换到有效的子目录"""
        # 创建子目录
        child_dir = tmp_path / "child"
        child_dir.mkdir()
        
        wd = WorkingDir(tmp_path)
        wd.change_to_child_dir(child_dir)
        
        assert wd.where == child_dir
        assert len(wd.trace) == 2
        assert wd.trace[-1] == child_dir

    def test_change_to_nonexistent_child(self, tmp_path):
        """测试切换到不存在的子目录，应该抛出 FileNotFoundError"""
        wd = WorkingDir(tmp_path)
        nonexistent = tmp_path / "nonexistent"
        
        with pytest.raises(FileNotFoundError, match="不存在子目录"):
            wd.change_to_child_dir(nonexistent)

    def test_change_to_file_instead_of_dir(self, tmp_path):
        """测试尝试切换到文件而非目录，应该抛出 NotADirectoryError"""
        # 创建一个文件
        test_file = tmp_path / "test.txt"
        test_file.touch()
        
        wd = WorkingDir(tmp_path)
        
        with pytest.raises(NotADirectoryError, match="期望是一个目录，但传入的是文件"):
            wd.change_to_child_dir(test_file)

    def test_change_to_symlink_dir(self, tmp_path):
        """测试尝试切换到符号链接目录，应该抛出 NotADirectoryError"""
        # 创建一个真实目录和指向它的符号链接
        real_dir = tmp_path / "real_dir"
        real_dir.mkdir()
        
        link_dir = tmp_path / "link_dir"
        try:
            link_dir.symlink_to(real_dir)
            
            wd = WorkingDir(tmp_path)
            
            with pytest.raises(NotADirectoryError, match="期望是一个目录，但传入的是链接"):
                wd.change_to_child_dir(link_dir)
        except OSError:
            # Windows 上可能没有权限创建符号链接，跳过此测试
            pytest.skip("无法创建符号链接，可能是权限问题")

    def test_change_to_nested_child(self, tmp_path):
        """测试连续切换到嵌套的子目录"""
        # 创建嵌套目录结构
        level1 = tmp_path / "level1"
        level2 = level1 / "level2"
        level3 = level2 / "level3"
        level3.mkdir(parents=True)
        
        wd = WorkingDir(tmp_path)
        wd.change_to_child_dir(level1)
        assert wd.where == level1
        assert len(wd.trace) == 2
        
        wd.change_to_child_dir(level2)
        assert wd.where == level2
        assert len(wd.trace) == 3
        
        wd.change_to_child_dir(level3)
        assert wd.where == level3
        assert len(wd.trace) == 4


class TestChangeToParentDir:
    """测试切换到父目录的功能"""

    def test_change_to_parent_from_child(self, tmp_path):
        """测试从子目录切换到父目录"""
        child_dir = tmp_path / "child"
        child_dir.mkdir()
        
        wd = WorkingDir(tmp_path)
        wd.change_to_child_dir(child_dir)
        assert wd.where == child_dir
        
        wd.change_to_parent_dir()
        assert wd.where == tmp_path.resolve()
        assert len(wd.trace) == 1

    def test_change_to_parent_at_root(self, tmp_path, capsys):
        """测试在根目录时切换到父目录，应该保持不变并打印提示"""
        wd = WorkingDir(tmp_path)
        wd.change_to_parent_dir()
        
        assert wd.where == tmp_path.resolve()
        captured = capsys.readouterr()
        assert "已经是顶层目录" in captured.out

    def test_multiple_parent_changes(self, tmp_path):
        """测试多次切换到父目录"""
        # 创建三层嵌套目录
        level1 = tmp_path / "level1"
        level2 = level1 / "level2"
        level3 = level2 / "level3"
        level3.mkdir(parents=True)
        
        wd = WorkingDir(tmp_path)
        wd.change_to_child_dir(level1)
        wd.change_to_child_dir(level2)
        wd.change_to_child_dir(level3)
        
        assert len(wd.trace) == 4
        
        wd.change_to_parent_dir()
        assert wd.where == level2
        assert len(wd.trace) == 3
        
        wd.change_to_parent_dir()
        assert wd.where == level1
        assert len(wd.trace) == 2
        
        wd.change_to_parent_dir()
        assert wd.where == tmp_path.resolve()
        assert len(wd.trace) == 1


class TestWhereProperty:
    """测试 where 属性"""

    def test_where_returns_current_path(self, tmp_path):
        """测试 where 属性返回当前路径"""
        wd = WorkingDir(tmp_path)
        assert wd.where == tmp_path.resolve()
        assert isinstance(wd.where, Path)

    def test_where_updates_after_navigation(self, tmp_path):
        """测试导航后 where 属性正确更新"""
        child_dir = tmp_path / "child"
        child_dir.mkdir()
        
        wd = WorkingDir(tmp_path)
        initial_where = wd.where
        
        wd.change_to_child_dir(child_dir)
        assert wd.where != initial_where
        assert wd.where == child_dir


class TestTraceProperty:
    """测试 trace 属性"""

    def test_trace_initial_state(self, tmp_path):
        """测试 trace 初始状态只包含根目录"""
        wd = WorkingDir(tmp_path)
        trace = wd.trace
        assert len(trace) == 1
        assert trace[0] == tmp_path.resolve()

    def test_trace_records_navigation(self, tmp_path):
        """测试 trace 记录导航历史"""
        child1 = tmp_path / "child1"
        child2 = child1 / "child2"
        child2.mkdir(parents=True)
        
        wd = WorkingDir(tmp_path)
        wd.change_to_child_dir(child1)
        wd.change_to_child_dir(child2)
        
        trace = wd.trace
        assert len(trace) == 3
        assert trace[0] == tmp_path.resolve()
        assert trace[1] == child1
        assert trace[2] == child2

    def test_trace_returns_copy(self, tmp_path):
        """测试 trace 返回副本，修改不影响内部状态"""
        child_dir = tmp_path / "child"
        child_dir.mkdir()
        
        wd = WorkingDir(tmp_path)
        trace1 = wd.trace
        trace1.append(Path("/fake/path"))
        
        trace2 = wd.trace
        assert len(trace2) == 1
        assert trace1 is not trace2

    def test_trace_updates_on_parent_navigation(self, tmp_path):
        """测试返回父目录时 trace 正确更新"""
        child_dir = tmp_path / "child"
        child_dir.mkdir()
        
        wd = WorkingDir(tmp_path)
        wd.change_to_child_dir(child_dir)
        assert len(wd.trace) == 2
        
        wd.change_to_parent_dir()
        assert len(wd.trace) == 1


class TestWalkDir:
    """测试 walk_dir 方法"""

    def test_walk_empty_directory(self, tmp_path):
        """测试遍历空目录"""
        wd = WorkingDir(tmp_path)
        result = wd.walk_dir()
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_walk_directory_with_files(self, tmp_path):
        """测试遍历包含文件的目录"""
        # 创建几个文件
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.py"
        file1.write_text("test content 1")
        file2.write_text("test content 2")
        
        wd = WorkingDir(tmp_path)
        result = wd.walk_dir()
        
        assert len(result) == 2
        file_names = {item["file_name"] for item in result}
        assert "file1.txt" in file_names
        assert "file2.py" in file_names
        
        for item in result:
            assert item["file_type"] == "file"
            assert item["target"] is None
            assert item["size"] >= 0

    def test_walk_directory_with_subdirs(self, tmp_path):
        """测试遍历包含子目录的目录"""
        subdir1 = tmp_path / "subdir1"
        subdir2 = tmp_path / "subdir2"
        subdir1.mkdir()
        subdir2.mkdir()
        
        wd = WorkingDir(tmp_path)
        result = wd.walk_dir()
        
        assert len(result) == 2
        for item in result:
            assert item["file_type"] == "directory"
            assert item["target"] is None

    def test_walk_mixed_content(self, tmp_path):
        """测试遍历包含文件和目录的混合内容"""
        # 创建文件
        file1 = tmp_path / "readme.txt"
        file1.write_text("readme")
        
        # 创建目录
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        wd = WorkingDir(tmp_path)
        result = wd.walk_dir()
        
        assert len(result) == 2
        
        types = {item["file_name"]: item["file_type"] for item in result}
        assert types["readme.txt"] == "file"
        assert types["subdir"] == "directory"

    def test_walk_with_symlink(self, tmp_path):
        """测试遍历包含符号链接的目录"""
        # 创建一个文件和指向它的链接
        real_file = tmp_path / "real_file.txt"
        real_file.write_text("content")
        
        link_file = tmp_path / "link_file.txt"
        try:
            link_file.symlink_to(real_file)
            
            wd = WorkingDir(tmp_path)
            result = wd.walk_dir()
            
            # 找到链接项
            link_items = [item for item in result if item["file_type"] == "link"]
            assert len(link_items) == 1
            assert link_items[0]["file_name"] == "link_file.txt"
            assert link_items[0]["target"] == "real_file.txt"
        except OSError:
            pytest.skip("无法创建符号链接，可能是权限问题")

    def test_walk_metadata_structure(self, tmp_path):
        """测试 walk_dir 返回的元数据结构"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        wd = WorkingDir(tmp_path)
        result = wd.walk_dir()
        
        assert len(result) == 1
        metadata = result[0]
        
        # 验证所有必需的键都存在
        required_keys = {"file_name", "full_name", "file_type", "size", "target"}
        assert set(metadata.keys()) == required_keys
        
        # 验证数据类型
        assert isinstance(metadata["file_name"], str)
        assert isinstance(metadata["full_name"], str)
        assert isinstance(metadata["file_type"], str)
        assert isinstance(metadata["size"], int)
        assert metadata["target"] is None or isinstance(metadata["target"], str)

    def test_walk_after_navigation(self, tmp_path):
        """测试导航到子目录后遍历"""
        # 创建目录结构
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        file_in_root = tmp_path / "root_file.txt"
        file_in_root.touch()
        
        file_in_subdir = subdir / "sub_file.txt"
        file_in_subdir.touch()
        
        wd = WorkingDir(tmp_path)
        
        # 在根目录遍历
        root_result = wd.walk_dir()
        assert len(root_result) == 2
        
        # 切换到子目录
        wd.change_to_child_dir(subdir)
        
        # 在子目录遍历
        sub_result = wd.walk_dir()
        assert len(sub_result) == 1
        assert sub_result[0]["file_name"] == "sub_file.txt"


class TestIntegrationScenarios:
    """集成测试：测试多个功能组合使用"""

    def test_complete_navigation_workflow(self, tmp_path):
        """测试完整的导航工作流"""
        # 创建复杂的目录结构
        docs = tmp_path / "docs"
        src = tmp_path / "src"
        tests = tmp_path / "tests"
        
        docs.mkdir()
        src.mkdir()
        tests.mkdir()
        
        (docs / "readme.md").touch()
        (src / "main.py").touch()
        (tests / "test_main.py").touch()
        
        wd = WorkingDir(tmp_path)
        
        # 遍历根目录
        root_items = wd.walk_dir()
        assert len(root_items) == 3
        
        # 导航到 src
        wd.change_to_child_dir(src)
        src_items = wd.walk_dir()
        assert len(src_items) == 1
        assert src_items[0]["file_name"] == "main.py"
        
        # 返回根目录
        wd.change_to_parent_dir()
        assert wd.where == tmp_path.resolve()
        
        # 检查 trace
        trace = wd.trace
        assert len(trace) == 1
        assert trace[0] == tmp_path.resolve()

    def test_deep_navigation_and_trace(self, tmp_path):
        """测试深度导航和路径追踪"""
        # 创建深层目录
        deep_path = tmp_path / "a" / "b" / "c" / "d"
        deep_path.mkdir(parents=True)
        
        wd = WorkingDir(tmp_path)
        
        # 逐层向下导航
        current = tmp_path
        for dirname in ["a", "b", "c", "d"]:
            current = current / dirname
            wd.change_to_child_dir(current)
        
        # 验证当前位置和 trace
        assert wd.where == deep_path
        assert len(wd.trace) == 5
        
        # 逐层返回
        for _ in range(4):
            wd.change_to_parent_dir()
        
        assert wd.where == tmp_path.resolve()
        assert len(wd.trace) == 1


# Pytest fixtures
@pytest.fixture
def temp_workspace(tmp_path):
    """创建一个临时工作空间用于测试"""
    # 创建一些标准目录和文件
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").touch()
    (tmp_path / "src" / "main.py").touch()
    
    return tmp_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
