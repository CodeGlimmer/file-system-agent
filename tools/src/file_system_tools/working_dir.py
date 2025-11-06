from pathlib import Path
from .file_type import FileType
from .file_metadata import FileMetadata
import ipdb


class WorkingDir:
    """工作目录类，限制了agent的tool的能力范围，防止越权访问文件系统，属于内部工具，使用pathlib管理路径"""

    def __init__(self, root: Path):
        """建立工作目录，类似与一棵树，建立是提供文件树的树根

        Args:
            root (Path): 工作目录的根路径，会被转换成完整路径(resolve)
        Raises:
            FileNotFoundError: 路径不存在时抛出
        """
        if not root.exists():
            raise FileNotFoundError(f"路径{root.name}不存在")
        self._root: Path = root.resolve()
        self._now: Path = self._root
        self._trace: list[Path] = [
            self._root
        ]  # 记录路径变更轨迹，初始为根目录, stack结构

    def change_to_child_dir(self, target: Path):
        """切换到当前目录下的子目录，但是不可以是符号链接否则或超出权限范围

        Args:
            target (Path): 目标子目录的 Path 对象（需为 self._now 下的直接子项）
        Raises:
            FileNotFoundError: 目标不在当前目录直接子项中
            NotADirectoryError: 目标存在但不是目录
        """
        # 使用 iterdir() 判断是否为当前目录的直接子项（不跨层）
        # ipdb.set_trace()
        if target not in self._now.iterdir():
            print("不存在这个目录")
            raise FileNotFoundError(f"不存在子目录{target.name}")
        if not target.is_dir():
            raise NotADirectoryError(f"期望是一个目录，但传入的是文件: {target.name}")
        if target.is_symlink():
            raise NotADirectoryError(f"期望是一个目录，但传入的是链接: {target.name}")
        self._now = target  # 更新当前目录
        self._trace.append(self._now)

    def change_to_parent_dir(self):
        if self._now == self._root:
            print("已经是顶层目录")
            return
        self._now = self._now.resolve().parent
        self._trace.pop()

    @property
    def where(self) -> Path:
        """返回当前工作目录路径

        Returns:
            Path: 当前工作目录的路径
        """
        return self._now

    @property
    def trace(self) -> list[Path]:
        """返回当前工作目录的路径变更轨迹

        Returns:
            list[Path]: 路径变更轨迹列表
        """
        return self._trace.copy()

    def walk_dir(self) -> list[FileMetadata]:
        """遍历当前工作目录，返回目录内容的元信息列表

        Returns:
            list[FileMetadata]: 当前目录下所有子项的元信息列表
        """
        msg_list: list[FileMetadata] = []  # 存储文件元信息
        for child in self._now.iterdir():
            # 判断child的类型
            if child.is_file():
                file_type = FileType.FILE.value
                target = None
            elif child.is_dir():
                file_type = FileType.DIRECTORY.value
                target = None
            else:
                file_type = FileType.LINK.value
                target = child.readlink().name
            msg: FileMetadata = {
                "file_name": child.name,
                "full_name": child.resolve().name,
                "file_type": file_type,
                "size": child.stat().st_size,
                "target": target,
            }
            msg_list.append(msg)
        return msg_list
