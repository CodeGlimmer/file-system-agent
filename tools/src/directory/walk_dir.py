from pathlib import Path
from typing import TypedDict, Literal


class ChildMetadata(TypedDict):
    file_name: str
    full_name: str
    file_type: Literal['file', 'directory', 'link']
    size: int
    target: str | None


def walk_dir(p: Path) -> None | list[ChildMetadata]:
    """遍历目录，以结构化的形式返回目录中的内容

    Args:
        p (Path): 需要遍历的目录
    """
    if not p.exists():
        return
    if not p.is_dir():
        return
    msg_list: list[ChildMetadata] = [] # 存储文件元信息
    for child in p.iterdir():
        # 判断child的类型
        if child.is_file():
            file_type = 'file'
            target = None
        elif child.is_dir():
            file_type = 'directory'
            target = None
        else:
            file_type = 'link'
            target = child.readlink().name
        msg: ChildMetadata = {
            'file_name': child.name,
            'full_name': child.resolve().name,
            'file_type': file_type,
            'size': child.stat().st_size,
            'target': target
        }
        msg_list.append(msg)
    return msg_list