#!/usr/bin/env python3
"""
配置文件
存储API密钥和系统设置
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# ========== API提供商选择 ==========
# 可选: 'deepseek', 'anthropic'
API_PROVIDER = os.getenv('API_PROVIDER', 'deepseek')

# ========== DeepSeek API配置 ==========
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

# ========== Anthropic API配置 ==========
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"  # 或 "claude-3-haiku-20240307"

# ========== 通用配置 ==========
MAX_TOKENS = 8000
TEMPERATURE = 0.3  # 较低的温度使翻译更稳定

# ========== 路径配置 ==========
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = Path.home() / 'Downloads'
KNOWLEDGE_BASE_DIR = DOWNLOADS_DIR / 'AI-Knowledge-Base'
KNOWLEDGE_BASE_CN_DIR = DOWNLOADS_DIR / 'AI-Knowledge-Base-CN'

# ========== 内容清洗配置 ==========
# 要移除的导航关键词
REMOVE_KEYWORDS = [
    'Skip to main content',
    'Skip to footer',
    'Skip to content',
    'Loading...',
    'Cookie Policy',
    'Privacy Policy',
    'Terms of Service',
    'Sign up',
    'Sign in',
    'Log in',
    'Log out',
    'Subscribe',
    'Newsletter',
    '© 2024',
    '© 2025',
]

# 要移除的导航部分（通过关键词识别）
NAVIGATION_PATTERNS = [
    r'Products\s*Solutions\s*Company',
    r'Home\s*About\s*Contact',
    r'Twitter\s*LinkedIn\s*GitHub',
    r'Documentation\s*API\s*Blog',
]

# ========== 翻译配置 ==========
# 是否启用翻译
ENABLE_TRANSLATION = True

# 翻译时保留的格式标记
PRESERVE_FORMATS = [
    '```',  # 代码块
    '`',    # 行内代码
    '#',    # 标题
    '-',    # 列表
    '*',    # 列表/强调
    '[',    # 链接
    ']',
    '(',
    ')',
]

# ========== 内容增强配置 ==========
# 摘要句子数量
SUMMARY_SENTENCES = 5

# 关键概念数量
KEY_CONCEPTS_COUNT = 5

# ========== 输出格式配置 ==========
# 文件名翻译映射（常见术语）
FILENAME_TRANSLATIONS = {
    'Building Effective Agents': '构建有效的AI代理',
    'Model Context Protocol': '模型上下文协议',
    'Anthropic': 'Anthropic',
    'OpenAI': 'OpenAI',
    'Documentation': '文档',
    'Tutorial': '教程',
    'Guide': '指南',
    'Introduction': '介绍',
    'Getting Started': '快速开始',
    'Agents': '智能体',
    'AI Agents': 'AI智能体',
    'LangChain': 'LangChain',
    'LlamaIndex': 'LlamaIndex',
    'CrewAI': 'CrewAI',
    'DeepLearning': 'DeepLearning',
}

# ========== 日志配置 ==========
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# ========== 爬虫配置 ==========
# 请求超时（秒）
REQUEST_TIMEOUT = 30

# 重试次数
MAX_RETRIES = 3

# 请求间隔（秒）
REQUEST_DELAY = 1

# User-Agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'


def validate_config():
    """验证配置"""
    issues = []

    if API_PROVIDER == 'deepseek':
        if not DEEPSEEK_API_KEY:
            issues.append("⚠️  DEEPSEEK_API_KEY 未设置")
            issues.append("   请在 .env 文件中设置:")
            issues.append("   DEEPSEEK_API_KEY='your-api-key'")
    elif API_PROVIDER == 'anthropic':
        if not ANTHROPIC_API_KEY:
            issues.append("⚠️  ANTHROPIC_API_KEY 未设置")
            issues.append("   请在 .env 文件中设置:")
            issues.append("   ANTHROPIC_API_KEY='your-api-key'")
    else:
        issues.append(f"⚠️  未知的API提供商: {API_PROVIDER}")
        issues.append("   支持的提供商: deepseek, anthropic")

    return issues


if __name__ == '__main__':
    print("配置验证:")
    print("="*50)

    issues = validate_config()
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✓ 所有配置正常")

    print("\n当前配置:")
    print(f"  API提供商: {API_PROVIDER}")
    if API_PROVIDER == 'deepseek':
        print(f"  DeepSeek模型: {DEEPSEEK_MODEL}")
        print(f"  API URL: {DEEPSEEK_API_URL}")
        print(f"  API Key: {DEEPSEEK_API_KEY[:20]}..." if DEEPSEEK_API_KEY else "  API Key: 未设置")
    elif API_PROVIDER == 'anthropic':
        print(f"  Claude模型: {CLAUDE_MODEL}")
        print(f"  API Key: {ANTHROPIC_API_KEY[:20]}..." if ANTHROPIC_API_KEY else "  API Key: 未设置")
    print(f"  输入目录: {KNOWLEDGE_BASE_DIR}")
    print(f"  输出目录: {KNOWLEDGE_BASE_CN_DIR}")
    print(f"  翻译功能: {'启用' if ENABLE_TRANSLATION else '禁用'}")
