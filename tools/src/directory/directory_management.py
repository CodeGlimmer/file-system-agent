from pathlib import Path


class DirManagement:
    """
    目录管理类：在给定根目录下进行目录切换与文件增删操作。
    
    Attributes:
        _root: 根目录路径（不可越界到其父级）
        _now: 当前工作目录路径
    """

    def __init__(self, root: Path):
        """
        初始化目录管理对象。
        
        Args:
            root: 作为工作范围的根目录路径
            
        Raises:
            FileNotFoundError: 根路径不存在
            NotADirectoryError: 传入的路径不是目录
        """
        if not root.exists():
            raise FileNotFoundError(f"路径{root}不存在")
        if not root.is_dir():
            raise NotADirectoryError(f"期望是一个目录，但传入的是文件: {root}")
        self._root: Path = root
        self._now: Path = root  # 当前工作目录初始化为根目录

    def change_to_child_dir(self, target: Path):
        """
        切换到当前目录下的子目录。
        
        Args:
            target: 目标子目录的 Path 对象（需为 self._now 下的直接子项）
            
        Raises:
            FileNotFoundError: 目标不在当前目录直接子项中
            NotADirectoryError: 目标存在但不是目录
        """
        # 使用 iterdir() 判断是否为当前目录的直接子项（不跨层）
        if target not in self._now.iterdir():
            raise FileNotFoundError(f"不存在子目录{target.name}")
        if not target.is_dir():
            raise NotADirectoryError(f"期望是一个目录，但传入的是文件: {target.name}")
        self._now = target  # 更新当前目录

    def change_to_parent_dir(self):
        """
        切换到父目录。若已在根目录则提示并保持不变。
        """
        if self._now == self._root:
            print("已经是顶层目录")
            return
        # resolve() 规范化路径，避免出现相对路径残留
        self._now = self._now.resolve().parent

    @property
    def where(self) -> Path:
        """
        获取当前工作目录。
        
        Returns:
            当前目录 Path 对象
        """
        return self._now

    def add_file(self, name: str) -> bool:
        """
        在当前目录创建一个文件（已存在则忽略）。
        
        Args:
            name: 文件名（不含路径）
            
        Returns:
            True 创建/存在成功；False 操作失败（异常已打印）
        """
        try:
            target_file = self._now / name
            # touch(exist_ok=True) 若文件存在不会报错
            target_file.touch(exist_ok=True)
            return True
        except Exception as e:
            print(e)
            return False

    def delete_file(self, name: str) -> bool:
        """
        删除当前目录下的指定文件（仅删除文件，不处理目录）。
        
        Args:
            name: 文件名
            
        Returns:
            True 删除成功；False 文件不存在
        """
        target_file = self._now / name
        # 使用迭代判断是否存在于当前目录（可避免误删其他路径）
        if target_file not in self._now.iterdir():
            print("文件不存在")
            return False
        target_file.unlink()  # 删除文件
        return True
    
    def rename_file(self, old_name: str, new_name: str) -> bool:
        """
        重命名当前目录下的指定文件。
        
        Args:
            old_name: 旧文件名
            new_name: 新文件名
            
        Returns:
            True 重命名成功；False 文件不存在或操作失败
        """
        old_file = self._now / old_name
        new_file = self._now / new_name
        if old_file not in self._now.iterdir():
            print("文件不存在")
            return False
        try:
            old_file.rename(new_file)
            return True
        except Exception as e:
            print(e)
            return False