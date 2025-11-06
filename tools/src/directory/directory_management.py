from pathlib import Path

from regex import F


class DirManagement:
    
    def __init__(self, root: Path):
        if not root.exists():
            raise FileNotFoundError(f'路径{root}不存在')
        if not root.is_dir():
            raise NotADirectoryError(f"期望是一个目录，但传入的是文件: {root}")
        self._root: Path = root
        self._now: Path = root
        
    def change_to_child_dir(self, target: Path):
        if target not in self._now.iterdir():
            raise FileNotFoundError(f'不存在子目录{target.name}')
        if not target.is_dir():
            raise NotADirectoryError(f"期望是一个目录，但传入的是文件: {target.name}")
        self._now = target
        
    def change_to_parent_dir(self):
        if self._now == self._root:
            print('已经是顶层目录')
            return
        self._now = self._now.resolve().parent
        
    @property
    def where(self) -> Path:
        return self._now
    
    # 下面为文件的增删改操作
    def add_file(self, name: str) -> bool:
        try:
            target_file = self._now/name
            target_file.touch(exist_ok=True)
            return True
        except Exception as e:
            print(e)
            return False
                        
        
    def delete_file(self, name: str) -> bool:
        target_file = self._now/name
        if target_file not in self._now.iterdir():
            print('文件不存在')
            return False
        target_file.unlink()
        return True