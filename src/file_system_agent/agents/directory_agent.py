# type: ignore
import importlib
import importlib.resources

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import BaseTool
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import InMemorySaver

from ..tools.src.file_system_tools.working_dir import WorkingDir
from ..tools.src.tools_for_agent.generate_dynamic_tools import generate_working_dir_tool

load_dotenv()

tools: list[BaseTool] | None
wd: WorkingDir | None
tools, wd = generate_working_dir_tool(root_path="E:/code")
model = ChatDeepSeek(model="deepseek-chat", temperature=0)

# 读取提示词
with (
    importlib.resources.files(f"{__package__}.prompts")
    .joinpath("directory_agent.md")
    .open("r", encoding="utf-8") as f
):
    SYSTEM_PROMPT = f.read()
    print(SYSTEM_PROMPT)

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver(),
)

if __name__ == "__main__":
    while True:
        user_input = input("user> ")
        if user_input.lower() in ["exit", "q", "quit"]:
            break
        res = agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            {"hread_id": "1"},  # type: ignore
        )
        print("agent> ", end="")
        print(res["messages"][-1].content)
