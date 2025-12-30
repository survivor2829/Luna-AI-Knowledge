#!/usr/bin/env python3
"""
使用 Jina Reader API 和 DeepSeek 的智能爬虫
- Jina Reader: 自动提取干净的内容（免费，无需API密钥）
- DeepSeek: 智能处理（清洗、翻译、摘要、概念提取）
"""

import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
import config
from translator_deepseek import DeepSeekTranslator


class JinaReaderScraper:
    """基于Jina Reader的智能爬虫"""

    def __init__(self):
        self.jina_api_base = "https://r.jina.ai"
        self.translator = DeepSeekTranslator()
        self.output_dir = Path.home() / 'Downloads' / 'Luna-AI-Knowledge'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_clean_content(self, url: str) -> Tuple[str, str]:
        """
        使用 Jina Reader API 获取干净的 Markdown 内容
        返回: (内容, 标题)
        """
        print(f"\n{'='*70}")
        print(f"获取内容: {url}")
        print(f"{'='*70}")

        # 构建 Jina Reader URL
        jina_url = f"{self.jina_api_base}/{url}"

        # 添加重试机制
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"  通过 Jina Reader 获取内容 (尝试 {attempt}/{max_attempts})...")

                # 使用 curl 避免 Python SSL 问题
                # -L: 跟随重定向, -s: 静默模式, --max-time: 超时, --retry: 重试次数
                result = subprocess.run(
                    ['curl', '-L', '-s', '--max-time', '30', '--retry', '3', '--retry-delay', '2', jina_url],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                # curl 错误代码: 35 = SSL连接错误, 可以重试
                if result.returncode == 35 and attempt < max_attempts:
                    print(f"  ⚠️  SSL连接失败 (错误码 35)，{2}秒后重试...")
                    import time
                    time.sleep(2)
                    continue

                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else f"curl error code {result.returncode}"
                    raise Exception(f"curl failed: {error_msg}")

                content = result.stdout

                if not content or len(content) < 100:
                    if attempt < max_attempts:
                        print(f"  ⚠️  内容为空或太短，2秒后重试...")
                        import time
                        time.sleep(2)
                        continue
                    raise Exception("内容为空或太短")

                # 提取标题（通常是第一个 # 标题或 "Title:" 行）
                title_match = re.search(r'^Title:\s*(.+)$', content, re.MULTILINE)
                if not title_match:
                    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)

                title = title_match.group(1) if title_match else self._extract_title_from_url(url)

                print(f"  ✓ 获取成功")
                print(f"  标题: {title}")
                print(f"  内容长度: {len(content)} 字符")

                return content, title

            except subprocess.TimeoutExpired:
                if attempt < max_attempts:
                    print(f"  ⚠️  请求超时，2秒后重试...")
                    import time
                    time.sleep(2)
                    continue
                print(f"  ✗ 请求超时")
                raise

            except Exception as e:
                if attempt < max_attempts:
                    print(f"  ⚠️  错误: {e}，2秒后重试...")
                    import time
                    time.sleep(2)
                    continue
                print(f"  ✗ 获取失败: {e}")
                raise

    def _extract_title_from_url(self, url: str) -> str:
        """从URL中提取标题"""
        # 获取URL路径的最后一部分
        path = url.rstrip('/').split('/')[-1]
        # 转换为标题格式
        title = path.replace('-', ' ').replace('_', ' ').title()
        return title

    def process_with_deepseek(self, content: str, title: str, source_url: str) -> Tuple[str, Dict]:
        """
        使用 DeepSeek 进行智能处理
        返回: (处理后的内容, 元数据)
        """
        print("\n处理内容...")

        # 使用 DeepSeek 进行综合处理
        system_prompt = """你是一个专业的技术文档处理助手。请对用户提供的技术文档进行以下处理：

1. **内容清洗**：移除无关内容，保留核心技术内容
2. **中文翻译**：将英文内容翻译成流畅、专业的中文
3. **保持格式**：严格保持所有 Markdown 格式、代码块、链接
4. **术语处理**：保留 API、SDK、LLM 等专业术语的英文

只输出处理后的中文内容，不要输出任何其他说明。"""

        try:
            # 1. 翻译主要内容（处理大文件）
            print("  1/4 翻译内容...")
            if len(content) > 10000:
                print(f"     内容较长 ({len(content)} 字符)，分块处理...")
                translated_content = self._translate_large_content(system_prompt, content)
            else:
                translated_content = self._call_deepseek(system_prompt, content, timeout=120)

            # 2. 生成摘要
            print("  2/4 生成摘要...")
            summary = self.translator.generate_summary(translated_content)

            # 3. 提取关键概念（带解释）
            print("  3/4 提取关键概念...")
            key_concepts = self._extract_concepts_with_explanation(translated_content)

            # 4. 生成适合人群
            print("  4/4 生成适合人群...")
            target_audience = self.translator.generate_target_audience(translated_content)

            metadata = {
                'title': title,
                'source_url': source_url,
                'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'summary': summary,
                'key_concepts': key_concepts,
                'target_audience': target_audience
            }

            return translated_content, metadata

        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
            raise

    def _translate_large_content(self, system_prompt: str, content: str) -> str:
        """分块翻译大文件"""
        import time

        # 按段落分割
        paragraphs = content.split('\n\n')
        translated_parts = []
        current_chunk = []
        current_size = 0
        chunk_limit = 8000  # 每块最多8000字符

        total_chunks = len(paragraphs)
        processed_paras = 0

        for para in paragraphs:
            para_size = len(para)

            if current_size + para_size > chunk_limit and current_chunk:
                # 翻译当前块
                chunk_content = '\n\n'.join(current_chunk)
                print(f"     处理进度: {processed_paras}/{total_chunks} 段落...")

                translated = self._call_deepseek(
                    system_prompt,
                    chunk_content,
                    timeout=120
                )
                translated_parts.append(translated)

                # 重置
                current_chunk = [para]
                current_size = para_size
                processed_paras += len(current_chunk)

                time.sleep(1)  # 避免API限流
            else:
                current_chunk.append(para)
                current_size += para_size

        # 翻译最后一块
        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            print(f"     处理进度: {total_chunks}/{total_chunks} 段落...")
            translated = self._call_deepseek(
                system_prompt,
                chunk_content,
                timeout=120
            )
            translated_parts.append(translated)

        return '\n\n'.join(translated_parts)

    def _call_deepseek(self, system_prompt: str, user_content: str, max_tokens: int = 8000, timeout: int = 60) -> str:
        """调用 DeepSeek API"""
        # 临时创建一个新client实例以使用自定义timeout
        from openai import OpenAI
        client = OpenAI(
            api_key=self.translator.api_key,
            base_url=self.translator.api_url,
            timeout=timeout
        )

        response = client.chat.completions.create(
            model=self.translator.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=max_tokens,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    def _extract_concepts_with_explanation(self, content: str) -> list:
        """提取关键概念并生成解释"""
        sample = content[:5000]

        system_prompt = f"""你是一个技术概念提取专家。请从文章中提取 {config.KEY_CONCEPTS_COUNT} 个最重要的关键概念。

对每个概念，请按以下格式输出：
概念名称 | 简短解释（不超过20字）

示例：
AI Agent | 使用大语言模型进行决策和行动的智能系统
Prompt Engineering | 优化提示词以提高AI输出质量的技术

只输出概念列表，每行一个，不要输出其他内容。"""

        try:
            response = self._call_deepseek(system_prompt, f"请从以下文章中提取关键概念：\n\n{sample}", max_tokens=500)

            # 解析概念列表
            concepts = []
            for line in response.split('\n'):
                line = line.strip()
                if '|' in line and line:
                    concepts.append(line)

            return concepts[:config.KEY_CONCEPTS_COUNT]

        except Exception as e:
            print(f"  ✗ 提取概念失败: {e}")
            return ["概念提取失败"]

    def format_output(self, content: str, metadata: Dict) -> str:
        """格式化最终输出"""

        # 格式化关键概念
        concepts_formatted = []
        for concept in metadata['key_concepts']:
            if '|' in concept:
                name, explanation = concept.split('|', 1)
                concepts_formatted.append(f"- **{name.strip()}**: {explanation.strip()}")
            else:
                concepts_formatted.append(f"- {concept}")

        output = f"""# {metadata['title']}

> **原文链接：** {metadata['source_url']}
> **处理时间：** {metadata['scraped_date']}
> **处理方式：** Jina Reader + DeepSeek AI

## 📝 内容摘要

{metadata['summary']}

## 🔑 关键概念

{chr(10).join(concepts_formatted)}

## 👥 适合人群

{metadata['target_audience']}

---

## 📄 正文内容

{content}
"""
        return output

    def save_document(self, content: str, title: str) -> Path:
        """保存文档"""
        # 生成安全的文件名
        safe_filename = re.sub(r'[<>:"/\\|?*]', '', title)
        safe_filename = safe_filename.replace(' ', '_')[:100]  # 限制长度
        filename = f"{safe_filename}.md"

        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def scrape_and_process(self, url: str) -> Path:
        """
        完整流程：抓取 -> 处理 -> 保存
        """
        print(f"\n{'='*70}")
        print(f"开始处理URL: {url}")
        print(f"{'='*70}")

        try:
            # 1. 使用 Jina Reader 获取干净内容
            raw_content, title = self.fetch_clean_content(url)

            # 2. 使用 DeepSeek 智能处理
            processed_content, metadata = self.process_with_deepseek(raw_content, title, url)

            # 3. 格式化输出
            final_content = self.format_output(processed_content, metadata)

            # 4. 保存文档
            output_path = self.save_document(final_content, metadata['title'])

            print(f"\n✅ 处理完成！")
            print(f"保存位置: {output_path}")

            return output_path

        except Exception as e:
            print(f"\n❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            raise


def test_scraper():
    """测试爬虫"""
    # 验证配置
    issues = config.validate_config()
    if issues:
        print("\n配置问题:")
        for issue in issues:
            print(issue)
        print("\n请先配置 DeepSeek API 密钥")
        return

    print(f"\n{'='*70}")
    print("Jina Reader + DeepSeek 智能爬虫测试")
    print(f"{'='*70}")
    print(f"API提供商: {config.API_PROVIDER}")
    print(f"模型: {config.DEEPSEEK_MODEL}")
    print(f"{'='*70}")

    # 测试URL
    test_url = "https://www.anthropic.com/research/building-effective-agents"

    # 创建爬虫并处理
    scraper = JinaReaderScraper()
    scraper.scrape_and_process(test_url)


if __name__ == '__main__':
    test_scraper()
