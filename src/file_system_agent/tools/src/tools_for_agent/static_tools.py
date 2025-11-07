"""提供agent调用的静态工具，没有动态的文件树状态，比如写入，读取操作等等, 路径是字符串但是要求绝对路径"""

from langchain.tools import tool
from pathlib import Path
import os


@tool
def read_file(file_path: str) -> str:
    """读取指定文件的内容

    Args:
        file_path (str): 要读取的文件路径

    Returns:
        str: 文件内容
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"读取文件失败: {e}"


@tool
def write_file(file_path: str, content: str) -> str:
    """将内容写入指定文件

    Args:
        file_path (str): 要写入的文件路径
        content (str): 要写入的内容

    Returns:
        str: 写入结果描述
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"成功写入文件: {file_path}"
    except Exception as e:
        return f"写入文件失败: {e}"


@tool
def add_file(file_path: str) -> str:
    """创建一个空文件

    Args:
        file_path (str): 要创建的文件路径

    Returns:
        str: 创建结果描述
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)  # 确保父目录存在
        path.touch(exist_ok=False)  # 创建新文件，若存在则报错
        return f"成功创建文件: {file_path}"
    except Exception as e:
        return f"创建文件失败: {e}"


@tool
def delete_file(file_path: str) -> str:
    """删除指定文件

    Args:
        file_path (str): 要删除的文件路径

    Returns:
        str: 删除结果描述
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"文件不存在: {file_path}"
        path.unlink()
        return f"成功删除文件: {file_path}"
    except Exception as e:
        return f"删除文件失败: {e}"


@tool
def rename_file(old_path: str, new_path: str) -> str:
    """重命名或移动文件

    Args:
        old_path (str): 旧文件路径
        new_path (str): 新文件路径

    Returns:
        str: 重命名结果描述
    """
    try:
        old = Path(old_path)
        new = Path(new_path)
        if not old.exists():
            return f"源文件不存在: {old_path}"
        new.parent.mkdir(parents=True, exist_ok=True)  # 确保目标父目录存在
        old.rename(new)
        return f"成功重命名/移动文件到: {new_path}"
    except Exception as e:
        return f"重命名/移动文件失败: {e}"


@tool
def excute_python(file: str) -> str:
    """执行指定的Python脚本文件

    Args:
        file (str): 要执行的Python脚本文件路径

    Returns:
        None
    """
    try:
        os.system(f'python "{file}"')
        return f"成功执行Python脚本: {file}"
    except Exception as e:
        return f"执行Python脚本失败: {e}"
