# URL分类说明

> 用于自动分类爬取的URL到对应目录

---

## AI技术类 → `01-理论库/AI工程/`

| 域名 | 子目录 | 说明 |
|------|--------|------|
| anthropic.com, docs.anthropic.com | Anthropic官方/ | Claude、Agent、MCP |
| modelcontextprotocol.io | MCP协议/ | Model Context Protocol |
| python.langchain.com, langchain.com | LangChain/ | LangChain生态 |
| platform.openai.com, openai.com | OpenAI/ | GPT、Assistant API |
| docs.crewai.com | CrewAI/ | 多Agent协作框架 |
| docs.llamaindex.ai | LlamaIndex/ | RAG框架 |
| promptingguide.ai | Prompt工程/ | 提示词工程 |
| huggingface.co/docs/smolagents | 新兴框架/ | HuggingFace smolagents |
| google.github.io/adk-docs | 新兴框架/ | Google ADK |

---

## 案例类 → `02-案例库/`

| 域名 | 子目录 | 说明 |
|------|--------|------|
| growth.design/case-studies | 用户转化案例/ | 顶级UX心理学案例 |
| hubspot.com/case-studies | 销售成交案例/ | HubSpot客户案例 |
| gong.io/case-studies | 销售成交案例/ | Gong销售智能案例 |
| salesforce.com/customer-success-stories | 销售成交案例/ | Salesforce案例 |
| casestudy.club | 产品设计案例/ | 产品案例合集 |
| builtformars.com | 产品设计案例/ | UX拆解 |

---

## 方法论类 → `01-理论库/`

| 域名 | 子目录 | 说明 |
|------|--------|------|
| blog.hubspot.com/sales | 沟通说服/ | 销售方法论 |
| gong.io/blog | 沟通说服/ | 基于数据的销售洞察 |
| behavioraleconomics.com | 认知决策/ | 行为经济学 |
| thedecisionlab.com | 认知决策/ | 决策科学 |
| fs.blog | 系统思维/ | Farnam Street思维模型 |
| lawsofux.com | 产品设计/ | UX设计原则 |
| goodui.org | 增长运营/ | A/B测试最佳实践 |

---

## 自动分类规则

```python
def classify_url(url):
    domain = extract_domain(url)

    # AI技术类
    if any(d in domain for d in ['anthropic', 'openai', 'langchain',
                                   'crewai', 'llamaindex', 'modelcontextprotocol']):
        return '01-理论库/AI工程/'

    # 案例类
    if '/case-studies' in url or '/case-study' in url:
        return '02-案例库/'
    if 'customer-success' in url or 'customer-stories' in url:
        return '02-案例库/销售成交案例/'

    # 方法论类
    if 'blog' in url and any(d in domain for d in ['hubspot', 'gong']):
        return '01-理论库/沟通说服/'
    if any(d in domain for d in ['behavioraleconomics', 'thedecisionlab']):
        return '01-理论库/认知决策/'
    if 'fs.blog' in domain:
        return '01-理论库/系统思维/'

    return '01-理论库/其他/'
```

---

## URL统计

| 分类 | 数量 | 优先级 |
|------|------|--------|
| AI技术类 | 32 | 高 |
| 案例类 | 12 | 高 |
| 方法论类 | 11 | 中 |
| **总计** | **55** | - |
