---
整理：Mr.Chen
原文日期：2024年
更新日期：2025-12-30
原文链接：https://huggingface.co/docs/smolagents/
---

# smolagents：极简主义的Agent设计

> 类型：AI工程
> 难度：入门

## 核心问题

**如何用最少的代码构建功能完备的Agent？**

许多Agent框架过度抽象，smolagents的设计目标是：**几行代码就能构建和运行Agent**，同时保持足够的灵活性。

## 设计哲学

### 极简主义

> "The logic for agents fits in ~thousand lines of code. We kept abstractions to their minimal shape above raw code!"

smolagents的核心约束：
- 整个Agent逻辑 < 1000行代码
- 抽象层级最小化
- 直接接近原始代码

### Code Agent优先

**关键洞察**：Agent用代码表达动作，比JSON/文本描述更强大。

```python
# 传统方式：JSON描述动作
{"action": "search", "query": "weather paris"}
{"action": "calculate", "expression": "32 * 1.8 + 32"}

# smolagents方式：直接写代码
weather = search("weather paris")
celsius = 32
fahrenheit = celsius * 1.8 + 32
```

**代码表达的优势**：
- 天然支持**组合**（函数嵌套）
- 天然支持**循环**和**条件**
- 更容易调试和理解

## 底层原理

### 原理1：两种Agent类型

| 类型 | 动作表达 | 适用场景 |
|------|----------|----------|
| **CodeAgent** | Python代码 | 需要计算、组合、循环 |
| **ToolCallingAgent** | JSON/文本 | 简单工具调用 |

### 原理2：工具抽象统一

smolagents可以使用来自多个来源的工具：

```python
# MCP Server的工具
from smolagents import ToolCollection
tools = ToolCollection.from_mcp(server_url)

# LangChain的工具
from smolagents import Tool
tool = Tool.from_langchain(langchain_tool)

# Gradio Space作为工具
tool = Tool.from_space("username/space_name")

# 自定义工具
@tool
def my_custom_tool(query: str) -> str:
    """Search for information."""
    return search_api(query)
```

### 原理3：模型无关设计

```python
# HuggingFace Inference API
model = InferenceClientModel()

# OpenAI/Anthropic via LiteLLM
model = LiteLLMModel(model_id="gpt-4")

# 本地模型
model = TransformersModel(model_id="llama-2-7b")

# 统一的Agent接口
agent = CodeAgent(tools=tools, model=model)
```

## 关键实现

### 最简Agent（3行代码）

```python
from smolagents import CodeAgent, InferenceClientModel

agent = CodeAgent(tools=[], model=InferenceClientModel())
result = agent.run("Calculate the sum of 1 to 10")
```

### 带工具的Agent

```python
from smolagents import CodeAgent, InferenceClientModel, DuckDuckGoSearchTool

agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=InferenceClientModel()
)

result = agent.run("What is the weather in Paris today?")
```

### 安全的代码执行

```python
from smolagents import CodeAgent, InferenceClientModel
from smolagents.sandbox import E2BSandbox

# 在沙箱中执行Agent生成的代码
agent = CodeAgent(
    tools=[],
    model=InferenceClientModel(),
    sandbox=E2BSandbox()  # 或 Modal, Docker
)
```

## 实践要点

1. **从CodeAgent开始**
   - 大多数场景下CodeAgent更强大
   - 只有特定原因才用ToolCallingAgent

2. **沙箱执行**
   - 生产环境必须使用沙箱
   - 支持E2B、Modal、Docker等

3. **工具复用**
   - 优先使用现有工具（MCP、LangChain）
   - 自定义工具使用`@tool`装饰器

4. **模型选择**
   - 能力强的模型效果更好
   - 小模型可能不可靠

## 设计权衡

| 选择 | 获得 | 牺牲 |
|------|------|------|
| 极简代码 | 易于理解和定制 | 功能可能不如大框架全 |
| Code Agent | 表达力强、可组合 | 需要代码执行安全措施 |
| 模型无关 | 灵活性高 | 不同模型效果差异大 |

## 与其他框架对比

| 特性 | smolagents | LangChain | CrewAI |
|------|------------|-----------|--------|
| 代码量 | ~1000行 | 大型框架 | 中等 |
| 学习曲线 | 低 | 陡峭 | 中等 |
| Code Agent | 一等公民 | 支持 | 不支持 |
| 多Agent | 支持 | 支持 | 核心特性 |

## 关联资源

**📚 相关文档**：
- [构建有效Agent系统](./构建有效Agent系统.md) - Anthropic的Agent设计原则
- [CrewAI](./CrewAI-多Agent协作框架.md) - 多Agent协作框架
