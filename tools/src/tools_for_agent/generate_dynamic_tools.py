"""为file_system_tools.working_dir.WorkingDir生成有状态的实例，
并将生成的实例的方法包装为LangChain工具，以便agent使用。
"""

from tools.src.file_system_tools.working_dir import WorkingDir
from langchain.tools import tool, BaseTool
from pathlib import Path
import ipdb


def generate_working_dir_tool(
    root_path: str,
) -> tuple[list[BaseTool] | None, WorkingDir | None]:
    """生成一个有状态的WorkingDir实例，并将其方法包装为LangChain工具。"""
    try:
        working_dir: WorkingDir = WorkingDir(root=Path(root_path))
    except Exception as e:
        print(f"无法创建WorkingDir实例: {e}")
        return None, None
    tools: list[BaseTool] = []

    # 下面定义agent工具
    @tool
    def change_to_child_dir(target: str) -> str:
        """切换到当前目录下的子目录，但是不可以是符号链接否则或超出权限范围

        Args:
            target (str): 目标子目录的路径字符串（需为当前工作目录下的直接子项）

        Returns:
            str: 切换结果的描述信息
        """
        try:
            working_dir.change_to_child_dir(working_dir.where / target)
            return f"已切换到子目录: {working_dir.where.name}"
        except Exception as e:
            return f"切换子目录失败: {e}"

    tools.append(change_to_child_dir)

    @tool
    def change_to_parent_dir() -> str:
        """切换成当前目录的父目录, 如果已经达到顶层目录则不会改变位置

        Returns:
            str: 切换结果的描述
        """
        try:
            working_dir.change_to_parent_dir()
            return f"已切换到父目录: {working_dir.where.name}"
        except Exception as e:
            return f"切换父目录失败: {e}"

    tools.append(change_to_parent_dir)

    @tool
    def get_current_directory() -> str:
        """获取从项目根目录到当前目录的路径，字符串形式

        Returns:
            str: 从项目根目录到当前目录的路径的字符串
        """
        return " -> ".join([dir.name for dir in working_dir.trace])

    tools.append(get_current_directory)

    @tool
    def list_directory_contents() -> str:
        """列出当前工作目录下的所有文件和子目录

        Returns:
            str: 当前目录内容的描述字符串
        """
        ipdb.set_trace()
        try:
            contents = working_dir.walk_dir()
            if not contents:
                return "当前目录为空"
            result_lines = []
            for item in contents:
                line = f"{item['file_type'].upper()}: {item['file_name']} (大小: {item['size']} bytes)"
                if item["file_type"] == "link" and item["target"]:
                    line += f" -> 指向: {item['target']}"
                result_lines.append(line)
            return "\n".join(result_lines)
        except Exception as e:
            return f"列出目录内容失败: {e}"

    tools.append(list_directory_contents)

    return tools, working_dir
