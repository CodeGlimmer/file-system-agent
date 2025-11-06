from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langchain.tools import BaseTool, tool
from langchain.messages import HumanMessage
from dotenv import load_dotenv
from tools.src.tools_for_agent.static_tools import (
    read_file,
    write_file,
    add_file,
    delete_file,
    rename_file,
    excute_python,
)
from tools.src.tools_for_agent.generate_dynamic_tools import generate_working_dir_tool
from langgraph.checkpoint.memory import InMemorySaver
from tools.src.file_system_tools.working_dir import WorkingDir


# 设置环境变量，定义模型
load_dotenv()
controller_model = ChatDeepSeek(model="deepseek-reasoner", temperature=0)
tool_model = ChatDeepSeek(model="deepseek-chat", temperature=0)

# 配置tool_agent
static_tools = [read_file, write_file, add_file, delete_file, rename_file, excute_python]
with open("agents/prompts/tool_agent.md", 'r', encoding="utf-8") as f:
    TOOL_PROMPT = f.read()
tool_agent = create_agent(
    model=tool_model,
    tools=static_tools,
    system_prompt=TOOL_PROMPT,
    checkpointer=InMemorySaver(),
)

# 配置主控agent的tools
dynamic_tools: list[BaseTool] | None
working_dir: WorkingDir | None
dynamic_tools, working_dir = generate_working_dir_tool(root_path="E:/code")
if dynamic_tools is None or working_dir is None:
    raise ValueError("无法创建WorkingDir工具")
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
        config = {"configurable": {"thread_id": "file_expert_thread"}}
        result = tool_agent.invoke(
            {"messages": [HumanMessage(content=task)]},
            config
        )
        
        # 提取最后的响应
        last_message = result["messages"][-1]
        return last_message.content
        
    except Exception as e:
        return f"文件操作失败: {str(e)}"
dynamic_tools.append(file_expert)
with open('agents/prompts/directory_agent.md', 'r', encoding='utf-8') as f:
    CONTROLLER_PROMPT = f.read()
if not CONTROLLER_PROMPT:
    raise ValueError("无法读取directory_agent的提示词")
# 构建controller_agent
controller_agent = create_agent(
    model=controller_model,
    tools=dynamic_tools,
    system_prompt=CONTROLLER_PROMPT,
    checkpointer=InMemorySaver(),
)

if __name__ == "__main__":
    while True:
        user_input = input("user> ")
        if user_input.lower() == "exit":
            break
        res = controller_agent.invoke(
            {"messages": [HumanMessage(content=user_input)]}, {"thread_id": "1"}
        )
        print("agent> ", end="")
        print(res["messages"][-1].content)