---
整理：Mr.Chen
原文日期：2024年
更新日期：2025-12-30
原文链接：https://docs.anthropic.com/en/docs/build-with-claude/tool-use
---

# Claude Tool Use：工具使用的设计哲学

> 类型：AI工程
> 难度：进阶

## 核心问题

**如何让LLM安全、可控地调用外部工具？**

Tool Use要解决的根本问题是：在给予LLM强大能力的同时，保持人类对系统的最终控制权。

## 设计哲学

### 控制权分离原则

Claude的Tool Use设计核心是**请求-执行分离**：

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│    Claude    │ ──→   │   Developer   │ ──→   │  外部系统     │
│   请求使用    │        │   决定执行    │        │  实际执行     │
└──────────────┘        └──────────────┘        └──────────────┘
      ↑                        │
      └────────── 返回结果 ─────┘
```

- Claude可以**请求**使用工具，但**不能直接执行**
- 开发者拥有最终控制权
- 这确保了安全性和可预测性

### 四大设计原则

1. **显式意图表达**
   - Claude明确说明需要哪个工具、什么参数
   - 非隐式或自动执行
   - 增强可观测性和调试能力

2. **灵活的结果处理**
   - 开发者可以拦截工具请求
   - 可以修改参数或拒绝调用
   - 可以返回模拟结果或真实结果

3. **上下文保持**
   - 工具结果返回给Claude，形成完整对话上下文
   - Claude可以基于结果进行推理和下一步操作

4. **安全边界**
   - 所有工具调用经过开发者验证
   - 敏感操作需要额外确认
   - 完整的审计日志

## 底层原理

### 原理1：工具定义是API契约

工具通过JSON Schema定义，本质是**Claude与开发者之间的契约**：

```json
{
  "name": "get_weather",
  "description": "Get the current weather for a location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The city and state, e.g. San Francisco, CA"
      }
    },
    "required": ["location"]
  }
}
```

**契约要素**：
- `name`：唯一标识符
- `description`：帮助Claude理解**何时**使用
- `input_schema`：定义**如何**使用

### 原理2：Description是Prompt工程

工具的`description`不只是文档，它是**影响Claude决策的Prompt**：

| 描述质量 | Claude行为 |
|----------|-----------|
| 模糊描述 | 不确定何时使用，可能误用 |
| 过度描述 | 过于依赖该工具 |
| 精确描述 | 在正确场景正确使用 |

**最佳实践**：
- 描述工具的**用途**，而非实现
- 说明**何时应该使用**
- 列出**限制和边界条件**

### 原理3：循环调用模式

Tool Use不是一次性的，而是可能多轮：

```python
while response.stop_reason == "tool_use":
    # 1. Claude请求使用工具
    tool_request = extract_tool_use(response)

    # 2. 开发者执行工具
    result = execute_tool(tool_request)

    # 3. 返回结果给Claude
    response = claude.continue_with_result(result)

# 4. Claude给出最终回答
return response.text
```

## 关键实现

```python
import anthropic

client = anthropic.Anthropic()

# 定义工具
tools = [
    {
        "name": "calculate",
        "description": "Perform basic math. Use for ANY calculation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression, e.g., '2 + 2'"
                }
            },
            "required": ["expression"]
        }
    }
]

# 调用Claude
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What is 25 * 4?"}]
)

# 处理工具调用请求
if response.stop_reason == "tool_use":
    tool_use = response.content[0]
    # 开发者控制：验证、执行、返回
    result = eval(tool_use.input["expression"])  # 实际应用需要安全处理
```

## 实践要点

### 工具设计最佳实践

| 原则 | 做法 |
|------|------|
| 单一职责 | 每个工具做一件事 |
| 清晰命名 | 名称准确反映功能 |
| 详细描述 | 帮助Claude理解何时使用 |
| 明确参数 | 类型和必需性要清楚 |

### 安全性检查清单

- ✅ 验证所有输入参数
- ✅ 检查权限和访问控制
- ✅ 处理异常和错误
- ✅ 记录调用以供审计
- ✅ 敏感操作需二次确认

## 设计权衡

| 选择 | 获得 | 牺牲 |
|------|------|------|
| 请求-执行分离 | 安全性、可控性 | 延迟增加 |
| JSON Schema定义 | 标准化、类型安全 | 灵活性略降 |
| 开发者中介 | 审计、干预能力 | 实现复杂度 |

## 关联资源

**📚 相关文档**：
- [构建有效Agent系统](./构建有效Agent系统.md) - 工具定义是契约设计
- [MCP协议](./MCP协议-AI的USB-C接口.md) - Tool Use的标准化扩展
