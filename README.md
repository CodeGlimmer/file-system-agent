# File System Agent

一个基于 LangChain 的文件系统智能代理工具，支持多种 AI 模型后端。

## 功能特性

- 🤖 集成多种 AI 模型（DeepSeek、Ollama）
- 📁 智能文件系统操作
- 🔧 命令行界面
- 📚 完整的文档支持

## 安装

### 使用 pip 安装

```bash
pip install file-system-agent
```

### 从源码安装

```bash
git clone <repository-url>
cd file-system-agent
pip install -e .
```

## 快速开始

### 环境配置

创建 `.env` 文件并配置必要的环境变量：

```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_deepseek_api_key

# Ollama 配置（如果使用本地模型）
OLLAMA_BASE_URL=http://localhost:11434
```

### 基本使用

```bash
# 启动文件系统代理
file-system-agent
```

## 依赖项

- Python >= 3.13
- LangChain >= 1.0.4
- LangChain-DeepSeek >= 1.0.0
- LangChain-Ollama >= 1.0.0
- python-dotenv >= 0.9.9

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 构建文档

```bash
mkdocs serve
```

## 项目结构

```
file-system-agent/
├── src/file_system_agent/    # 主要源码
├── docs/                     # 文档
├── tests/                    # 测试文件
├── pyproject.toml           # 项目配置
└── README.md               # 项目说明
```

## 许可证

请查看 LICENSE 文件了解详细信息。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 作者

- **Code Glimmer** - m15073691589@163.com
