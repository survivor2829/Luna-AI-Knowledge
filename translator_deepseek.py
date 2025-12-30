#!/usr/bin/env python3
"""
DeepSeek翻译和内容增强模块
使用DeepSeek API（OpenAI兼容格式）进行翻译和生成摘要
"""

import re
import time
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from langdetect import detect, LangDetectException
import config


class DeepSeekTranslator:
    """DeepSeek内容翻译和增强器"""

    def __init__(self, api_key: str = None, api_url: str = None):
        """初始化翻译器"""
        self.api_key = api_key or config.DEEPSEEK_API_KEY
        self.api_url = api_url or config.DEEPSEEK_API_URL
        self.model = config.DEEPSEEK_MODEL

        if not self.api_key:
            raise ValueError("需要提供 DEEPSEEK_API_KEY")

        # 初始化OpenAI客户端（DeepSeek API兼容OpenAI格式）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url,
            timeout=60.0  # 增加超时时间到60秒
        )

    def detect_language(self, text: str) -> str:
        """检测文本语言"""
        try:
            sample = text[:1000]
            lang = detect(sample)
            return lang
        except LangDetectException:
            return 'unknown'

    def translate_to_chinese(self, content: str, preserve_code: bool = True) -> str:
        """将英文内容翻译成中文，保留Markdown格式"""

        # 检测语言
        lang = self.detect_language(content)
        if lang == 'zh-cn' or lang == 'zh-tw':
            print("  内容已是中文，跳过翻译")
            return content

        print(f"  检测到语言: {lang}，开始翻译...")

        # 分块翻译（如果内容太长）
        max_chunk_size = 15000
        if len(content) > max_chunk_size:
            return self._translate_in_chunks(content, max_chunk_size)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的技术文档翻译助手。请将用户提供的英文Markdown文档翻译成中文，保持所有Markdown格式、代码块和链接不变，保留API、SDK等专业术语的英文。只输出翻译结果，不要输出其他内容。"
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE
            )

            translated = response.choices[0].message.content
            return translated.strip()

        except Exception as e:
            print(f"  ✗ 翻译失败: {e}")
            return content

    def _translate_in_chunks(self, content: str, chunk_size: int) -> str:
        """分块翻译长文本"""
        print(f"  内容较长，分块翻译...")

        # 按段落分割
        paragraphs = content.split('\n\n')
        translated_parts = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            if current_size + para_size > chunk_size and current_chunk:
                # 翻译当前块
                chunk_content = '\n\n'.join(current_chunk)
                translated = self.translate_to_chinese(chunk_content, preserve_code=True)
                translated_parts.append(translated)

                # 重置
                current_chunk = [para]
                current_size = para_size
                time.sleep(1)  # 避免API限流
            else:
                current_chunk.append(para)
                current_size += para_size

        # 翻译最后一块
        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            translated = self.translate_to_chinese(chunk_content, preserve_code=True)
            translated_parts.append(translated)

        return '\n\n'.join(translated_parts)

    def generate_summary(self, content: str, language: str = 'zh') -> str:
        """生成内容摘要"""
        print("  生成内容摘要...")

        # 取前5000字符用于生成摘要
        sample = content[:5000]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"你是一个擅长总结技术文档的助手。请用{config.SUMMARY_SENTENCES}句话生成文章摘要，每句话一行，不要使用'本文'、'这篇文章'等开头。"
                    },
                    {
                        "role": "user",
                        "content": f"请为以下文章生成摘要：\n\n{sample}"
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )

            summary = response.choices[0].message.content.strip()
            return summary

        except Exception as e:
            print(f"  ✗ 生成摘要失败: {e}")
            return "摘要生成失败"

    def extract_key_concepts(self, content: str) -> List[str]:
        """提取关键概念"""
        print("  提取关键概念...")

        # 取前5000字符
        sample = content[:5000]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"你是一个擅长提取技术概念的助手。请提取{config.KEY_CONCEPTS_COUNT}个最重要的关键概念，每个不超过10个字，按重要性排序，每行一个。"
                    },
                    {
                        "role": "user",
                        "content": f"请从以下文章中提取关键概念：\n\n{sample}"
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )

            concepts_text = response.choices[0].message.content.strip()
            # 解析概念列表
            concepts = [
                line.strip().lstrip('1234567890.-* ')
                for line in concepts_text.split('\n')
                if line.strip()
            ]

            return concepts[:config.KEY_CONCEPTS_COUNT]

        except Exception as e:
            print(f"  ✗ 提取概念失败: {e}")
            return ["概念提取失败"]

    def generate_target_audience(self, content: str) -> str:
        """生成适合人群说明"""
        print("  生成适合人群...")

        # 取前3000字符
        sample = content[:3000]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个技术文档分析助手。请用1-2句话说明文章适合什么人群阅读，包括技术背景和经验水平。"
                    },
                    {
                        "role": "user",
                        "content": f"请说明以下文章适合什么人群：\n\n{sample}"
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )

            audience = response.choices[0].message.content.strip()
            return audience

        except Exception as e:
            print(f"  ✗ 生成适合人群失败: {e}")
            return "适合所有对此主题感兴趣的读者"

    def translate_filename(self, filename: str) -> str:
        """翻译文件名为中文"""
        # 移除.md后缀
        name = filename.replace('.md', '')

        # 使用预定义的翻译映射
        for en, zh in config.FILENAME_TRANSLATIONS.items():
            name = name.replace(en, zh)

        # 如果没有匹配到翻译，使用DeepSeek翻译
        if not any(zh in name for zh in config.FILENAME_TRANSLATIONS.values()):
            prompt = f"""请将以下英文标题翻译成简洁的中文，保持专业性：

{name}

只输出翻译结果，不要解释：
"""
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个翻译助手。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100,
                    temperature=0.3
                )
                name = response.choices[0].message.content.strip()
            except Exception:
                pass  # 如果失败，保持原名

        # 清理文件名（移除特殊字符）
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = name.replace(' ', '_')

        return name + '.md'

    def enhance_content(
        self,
        content: str,
        title: str,
        source_url: str,
        category: str,
        scraped_date: str
    ) -> Tuple[str, str]:
        """
        增强内容：翻译、生成摘要、提取概念
        返回：(增强后的内容, 中文文件名)
        """

        # 1. 翻译内容
        print(f"\n处理: {title}")
        if config.ENABLE_TRANSLATION:
            translated_content = self.translate_to_chinese(content)
        else:
            translated_content = content

        # 2. 翻译标题
        translated_title = self.translate_to_chinese(title) if config.ENABLE_TRANSLATION else title

        # 3. 生成摘要
        summary = self.generate_summary(translated_content)

        # 4. 提取关键概念
        key_concepts = self.extract_key_concepts(translated_content)

        # 5. 生成适合人群
        target_audience = self.generate_target_audience(translated_content)

        # 6. 生成中文文件名
        chinese_filename = self.translate_filename(title)

        # 7. 组装最终内容
        enhanced_content = self._format_final_content(
            title=translated_title,
            source_url=source_url,
            scraped_date=scraped_date,
            category=category,
            summary=summary,
            key_concepts=key_concepts,
            target_audience=target_audience,
            content=translated_content
        )

        return enhanced_content, chinese_filename

    def _format_final_content(
        self,
        title: str,
        source_url: str,
        scraped_date: str,
        category: str,
        summary: str,
        key_concepts: List[str],
        target_audience: str,
        content: str
    ) -> str:
        """格式化最终输出内容"""

        formatted = f"""# {title}

> **原文链接：** {source_url}
> **爬取时间：** {scraped_date}
> **分类：** {category}

## 📝 内容摘要

{summary}

## 🔑 关键概念

{chr(10).join(f'- {concept}' for concept in key_concepts)}

## 👥 适合人群

{target_audience}

---

## 📄 正文内容

{content}
"""

        return formatted


def test_translator():
    """测试DeepSeek翻译器"""
    try:
        translator = DeepSeekTranslator()

        sample_text = """
# Building Effective Agents

Agents are systems that use LLMs to interact with the world.
They can make decisions, take actions, and learn from experience.

Key concepts:
- Agent architecture
- Tool use
- Memory systems
"""

        print("原文:")
        print(sample_text)
        print("\n" + "="*50 + "\n")

        translated = translator.translate_to_chinese(sample_text)
        print("译文:")
        print(translated)

    except ValueError as e:
        print(f"错误: {e}")
        print("请设置 DEEPSEEK_API_KEY")


if __name__ == '__main__':
    test_translator()
