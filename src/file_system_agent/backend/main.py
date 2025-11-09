import importlib.resources
from typing import Optional, TypedDict
import importlib
import argparse

from fastapi import FastAPI, staticfiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from pydantic_core import ArgsKwargs
import uvicorn

from .generate_agent import create_controller_agent

def generate_parser():
    parser = argparse.ArgumentParser(description="文件系统管理智能体CLI")
    parser.add_argument("-r", "--root", type=str, required=True)
    return parser

args = generate_parser().parse_args()
html_file = importlib.resources.files(__package__) / 'html'

class MessageRequest(BaseModel):
    content: str

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
    file_system: Optional[list[FileSystemItem]] = Field(None, description="""如果包含文件系统信息，则为文件系统的内容列表，列表中每一项包含以下字段：
        - file_name: 文件或目录的名称
        - full_name: 文件或目录的完整路径
        - file_type: 文件类型（file 或 directory 或 link）
        - size: 文件大小（字节）
        - target: 可选，如果是链接文件，则为链接目标路径
        如果不包含文件系统信息，则为返回空值。
    """)

agent = create_controller_agent(args.root)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

@app.post('/api/reply')
async def reply(message: MessageRequest) -> ReplyResponse:
    print(message.content)
    res = agent.invoke({'messages': [HumanMessage(content=message.content)]}, config) # type: ignore
    print(res['structured_response'])
    return res['structured_response']

app.mount('/', staticfiles.StaticFiles(directory=str(html_file), html=True), name='static')

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
if __name__ == "__main__":
    main()