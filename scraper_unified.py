#!/usr/bin/env python3
"""
Luna AI 知识库爬虫 - 统一格式版
输出格式：本质 + 原理 + 案例 + 行动 + 边界
"""

import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
import config
from translator_deepseek import DeepSeekTranslator


class UnifiedScraper:
    """统一格式爬虫 - 输出五合一格式"""

    def __init__(self):
        self.jina_api_base = "https://r.jina.ai"
        self.translator = DeepSeekTranslator()
        self.output_dir = Path.home() / 'Downloads' / 'Luna-AI-Knowledge'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_clean_content(self, url: str) -> Tuple[str, str]:
        """使用 Jina Reader API 获取干净的 Markdown 内容"""
        print(f"\n{'='*60}")
        print(f"获取: {url}")
        print(f"{'='*60}")

        jina_url = f"{self.jina_api_base}/{url}"

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"  Jina Reader (尝试 {attempt}/{max_attempts})...")
                result = subprocess.run(
                    ['curl', '-L', '-s', '--max-time', '60', '--retry', '2', jina_url],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode != 0:
                    raise Exception(f"curl error: {result.returncode}")

                content = result.stdout
                if not content or len(content) < 100:
                    raise Exception("内容为空或太短")

                # 提取标题
                title_match = re.search(r'^Title:\s*(.+)$', content, re.MULTILINE)
                if not title_match:
                    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else self._title_from_url(url)

                print(f"  ✓ 获取成功 ({len(content)} 字符)")
                return content, title

            except Exception as e:
                if attempt < max_attempts:
                    print(f"  ⚠️ {e}，重试...")
                    import time
                    time.sleep(2)
                else:
                    raise

    def _title_from_url(self, url: str) -> str:
        path = url.rstrip('/').split('/')[-1]
        return path.replace('-', ' ').replace('_', ' ').title()

    def process_unified_format(self, content: str, title: str, url: str) -> str:
        """使用 DeepSeek 处理成统一的五合一格式"""
        print("\n处理成统一格式...")

        # 截取内容（避免太长）
        content_sample = content[:15000] if len(content) > 15000 else content

        system_prompt = """你是一个专业的知识整理专家。请将用户提供的内容整理成以下统一格式：

# [主题标题]

## 本质
[用一句话说清楚这是什么，解决什么问题。要求：简洁有力，3秒能懂]

## 原理
[解释底层逻辑/心理学/商业原理，说明为什么有效。要求：
- 挖掘深层机制
- 如果原文没有原理，根据内容推断并标注"推断原理"
- 可以引用心理学、行为经济学、商业理论]

## 案例
[提供具体案例证明有效性。要求：
- 背景：公司/场景/规模
- 做法：具体怎么做的
- 结果：量化数据
- 如果原文没有案例，生成一个参考案例并标注"参考案例"]

## 行动
[提供可立即执行的步骤。要求：
1. 第一步（今天就能做）
2. 第二步
3. 第三步
每一步都要具体、可操作]

## 边界
[说明适用范围和限制。要求：
- ✅ 适用场景
- ❌ 不适用场景
- ⚠️ 注意事项]

---
> 来源：[原文URL]
> 整理：Mr.Chen
> 日期：[当前日期]

请用中文输出，保持专业但易懂的风格。只输出整理后的内容，不要其他说明。"""

        user_prompt = f"""请将以下内容整理成统一格式：

标题：{title}
来源：{url}

原文内容：
{content_sample}
"""

        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.translator.api_key,
                base_url=self.translator.api_url,
                timeout=180
            )

            print("  调用 DeepSeek 整理...")
            response = client.chat.completions.create(
                model=self.translator.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4000,
                temperature=0.3
            )

            result = response.choices[0].message.content.strip()

            # 补充元信息
            today = datetime.now().strftime('%Y-%m-%d')
            if f"> 日期：{today}" not in result:
                result = result.replace("> 日期：[当前日期]", f"> 日期：{today}")
            if url not in result:
                result = result.replace("> 来源：[原文URL]", f"> 来源：{url}")

            print("  ✓ 整理完成")
            return result

        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
            raise

    def save_document(self, content: str, title: str, category: str = None) -> Path:
        """保存文档"""
        # 生成安全文件名
        safe_name = re.sub(r'[<>:"/\\|?*]', '', title)
        safe_name = safe_name.replace(' ', '_')[:80]
        filename = f"{safe_name}.md"

        # 确定保存目录
        if category:
            save_dir = self.output_dir / category
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            save_dir = self.output_dir

        output_path = save_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def scrape(self, url: str, category: str = None) -> Path:
        """完整流程：抓取 -> 处理 -> 保存"""
        try:
            # 1. 获取内容
            raw_content, title = self.fetch_clean_content(url)

            # 2. 处理成统一格式
            unified_content = self.process_unified_format(raw_content, title, url)

            # 3. 保存
            output_path = self.save_document(unified_content, title, category)

            print(f"\n✅ 完成: {output_path}")
            return output_path

        except Exception as e:
            print(f"\n❌ 失败: {e}")
            raise


def batch_scrape(urls: list, category: str = None):
    """批量爬取"""
    import time

    scraper = UnifiedScraper()
    success = 0
    failed = []

    print(f"\n{'='*60}")
    print(f"批量爬取 {len(urls)} 个URL")
    print(f"输出格式：本质 + 原理 + 案例 + 行动 + 边界")
    print(f"{'='*60}")

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]")
        try:
            scraper.scrape(url, category)
            success += 1
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            failed.append(url)
        time.sleep(3)

    print(f"\n{'='*60}")
    print(f"完成！成功: {success}, 失败: {len(failed)}")
    if failed:
        print("失败URL:")
        for url in failed:
            print(f"  - {url}")

    return success, failed


def test():
    """测试"""
    issues = config.validate_config()
    if issues:
        print("配置问题:", issues)
        return

    # 测试URL
    test_url = "https://amplitude.com/blog/the-hook-model"

    scraper = UnifiedScraper()
    scraper.scrape(test_url, "01-理论库/产品设计")


if __name__ == '__main__':
    test()
