from importlib import resources
from pathlib import Path
from typing import Optional, TypedDict

from pydantic import BaseModel, Field
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool, BaseTool
from langchain.messages import HumanMessage
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver

from ..tools.src.tools_for_agent.static_tools import (
    read_file,
    write_file,
    add_file,
    delete_file,
    rename_file,
    excute_python,
)
from ..tools.src.tools_for_agent.generate_dynamic_tools import generate_working_dir_tool


class FileSystemItem(TypedDict):
    file_name: str
    full_name: str
    file_type: str
    size: int
    target: Optional[str]


class ReplyResponse(BaseModel):
    """生成agent的回复格式"""

    reply: str = Field(..., description="AI的回复内容")
    with_file_system: bool = Field(..., description="是否包含文件系统信息")
    file_system: Optional[list[FileSystemItem]] = Field(
        None,
        description="""如果包含文件系统信息，则为文件系统的内容列表，列表中每一项包含以下字段：
        - file_name: 文件或目录的名称
        - full_name: 文件或目录的完整路径
        - file_type: 文件类型（file 或 directory 或 link）
        - size: 文件大小（字节）
        - target: 可选，如果是链接文件，则为链接目标路径
        如果不包含文件系统信息，则为返回空值。
    """,
    )


prompt_dir: Path = resources.files(__package__) / ".." / "agents" / "prompts"  # type: ignore
model = ChatDeepSeek(model="deepseek-chat", temperature=0)

# 配置工具agent
tool_agent_tools = [
    read_file,
    write_file,
    add_file,
    delete_file,
    rename_file,
    excute_python,
]
with open(prompt_dir / "tool_agent.md", "r", encoding="utf-8") as f:
    TOOL_PROMPT = f.read()
if not TOOL_PROMPT:
    raise ValueError("无法加载tool_agent的提示词模板")
tool_agent = create_agent(
    model=model,
    tools=tool_agent_tools,
    system_prompt=TOOL_PROMPT,
    checkpointer=InMemorySaver(),
)


# 将智能体改造为tool
@tool
def file_expert(task: str) -> str:
    """文件操作专家。负责所有文件相关操作。

    可以执行：
    - 读取文件内容
    - 写入/覆盖文件
    - 创建新文件
    - 删除文件
    - 重命名/移动文件
    - 总结文件内容
    - 回答关于文件内容的问题
    - 执行python文件

    Args:
        task: 描述要执行的文件操作任务，例如：
            - "读取 C:/project/config.json"
            - "总结 E:/data/report.txt 的内容"
            - "将这段代码写入 E:/code/utils.py: [代码内容]"
            - "删除 C:/temp/old.txt"
            - "把 C:/old.txt 重命名为 C:/new.txt"
            - "执行 E:/code/script.py"

    Returns:
        操作结果或文件内容
    """
    try:
        # 调用 tool_agent 处理任务
        config: RunnableConfig = {"configurable": {"thread_id": "file_expert_thread"}}
        result = tool_agent.invoke({"messages": [HumanMessage(content=task)]}, config)

        # 提取最后的响应
        last_message = result["messages"][-1]
        return last_message.content

    except Exception as e:
        return f"文件操作失败: {str(e)}"


# 配置主控agent
with open(prompt_dir / "directory_agent.md", "r", encoding="utf-8") as f:
    CONTROLLER_PROMPT = f.read()
if not CONTROLLER_PROMPT:
    raise ValueError("无法读取directory_agent的提示词")
with open(prompt_dir / "summary_agent.md", "r", encoding="utf-8") as f:
    SUMMARY_PROMPT = f.read()
if not SUMMARY_PROMPT:
    raise ValueError("无法读取summary_agent的提示词")
# 对于CONTROLLER_PROMPT, 需要对内容进行补充说明，提示该智能体需要在提及目录操作时进行格式化输出
_more_prompt = """
# NOTE

额外补充一点，对于你的回复，用户要求进行格式化输出。如果用户提及到这类相似的问题，比如：

- "列出当前目录下的所有文件和文件夹"
- "显示 E:/project 目录的内容"
- "告诉我 D:/data 目录下有什么"

请务必将回复格式的"with_file_system"字段设置为True，并且在"file_system"字段中以列表形式返回目录内容, 具体格式请参考具体的说明。
"""
CONTROLLER_PROMPT += _more_prompt


def create_controller_agent(root_path: str):
    controller_agent_tools: list[BaseTool]
    controller_agent_tools, _ = generate_working_dir_tool(root_path)  # type: ignore
    controller_agent_tools.append(file_expert)
    return create_agent(
        model=model,
        tools=controller_agent_tools,
        checkpointer=InMemorySaver(),
        system_prompt=CONTROLLER_PROMPT,
        response_format=ReplyResponse,
        middleware=[
            SummarizationMiddleware(
                model=model,
                summary_prompt=SUMMARY_PROMPT,
                max_tokens_before_summary=4000,
                messages_to_keep=20,
            )
        ],
    )
