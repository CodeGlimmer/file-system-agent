from langchain.agents import create_agent
from tools.src.tools_for_agent.static_tools import (
    read_file,
    write_file,
    add_file,
    delete_file,
    rename_file,
)
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage

load_dotenv()

tools = [read_file, write_file, add_file, delete_file, rename_file]

model = ChatDeepSeek(model="deepseek-chat", temperature=0)

# 读取提示词
with open("agents/prompts/file_agent.md", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

agent = create_agent(
    model=model, tools=tools, system_prompt=SYSTEM_PROMPT, checkpointer=InMemorySaver()
)


if __name__ == "__main__":
    # 测试文件管理agent
    while True:
        user_input = input("user> ")
        if user_input.lower() == "exit":
            break
        res = agent.invoke(
            {"messages": [HumanMessage(content=user_input)]}, {"thread_id": "1"}
        )
        print("agent> ", end="")
        print(res["messages"][-1].content)
