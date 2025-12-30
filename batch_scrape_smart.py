#!/usr/bin/env python3
"""
智能批量爬虫
自动发现和筛选子链接，然后批量处理
"""

import time
from pathlib import Path
from typing import List, Set
from scraper_jina import JinaReaderScraper
from link_filter import LinkFilter
import config


class SmartBatchScraper:
    """智能批量爬虫"""

    def __init__(self, output_dir: Path, delay: int = 3):
        self.scraper = JinaReaderScraper()
        self.output_dir = output_dir
        self.delay = delay
        self.processed_urls: Set[str] = set()
        self.failed_urls = []

        # 统计
        self.stats = {
            'total_parent_urls': 0,
            'total_discovered': 0,
            'total_filtered': 0,
            'total_processed': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

    def read_parent_urls(self, file_path: str) -> List[str]:
        """读取母链接列表"""
        urls = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
        return urls

    def discover_and_filter(self, parent_url: str) -> List[str]:
        """
        发现并筛选子链接
        返回: 筛选后的URL列表
        """
        print(f"\n{'='*70}")
        print(f"处理母链接: {parent_url}")
        print(f"{'='*70}")

        # 创建筛选器
        link_filter = LinkFilter(parent_url)

        # 智能筛选
        result = link_filter.smart_filter(parent_url)

        # 显示结果
        link_filter.display_results(result)

        # 提取保留的URL
        filtered_urls = [link['url'] for link in result['keep']]

        # 更新统计
        self.stats['total_discovered'] += result['stats']['total']
        self.stats['total_filtered'] += len(filtered_urls)

        return filtered_urls

    def process_url(self, url: str, index: int, total: int) -> bool:
        """处理单个URL"""
        print(f"\n{'='*70}")
        print(f"进度: [{index}/{total}] ({index/total*100:.1f}%)")
        print(f"{'='*70}")

        # 检查是否已处理
        if url in self.processed_urls:
            print(f"⏭️  已处理，跳过")
            self.stats['skipped'] += 1
            return True

        try:
            # 处理URL
            output_path = self.scraper.scrape_and_process(url)
            self.processed_urls.add(url)
            self.stats['success'] += 1

            print(f"\n✅ 成功 [{self.stats['success']}/{self.stats['total_processed']}]")

            return True

        except Exception as e:
            self.stats['failed'] += 1
            self.failed_urls.append({
                'url': url,
                'error': str(e)
            })

            print(f"\n❌ 失败 [{self.stats['failed']}/{self.stats['total_processed']}]")
            print(f"原因: {e}")

            return False

    def smart_batch_process(
        self,
        parent_urls_file: str,
        auto_crawl_children: bool = True,
        limit: int = None,
        ask_confirmation: bool = True
    ):
        """
        智能批量处理

        参数:
            parent_urls_file: 母链接文件
            auto_crawl_children: 是否自动爬取筛选后的子链接
            limit: 限制处理数量
            ask_confirmation: 是否在爬取前询问确认
        """
        print("="*70)
        print("智能批量爬虫")
        print("="*70)

        # 验证配置
        issues = config.validate_config()
        if issues:
            print("\n配置问题:")
            for issue in issues:
                print(issue)
            return

        print(f"API提供商: {config.API_PROVIDER}")
        print(f"模型: {config.DEEPSEEK_MODEL}")
        print(f"输出目录: {self.output_dir}")
        print(f"自动爬取子链接: {'是' if auto_crawl_children else '否'}")
        print("="*70)

        # 读取母链接
        try:
            parent_urls = self.read_parent_urls(parent_urls_file)
            self.stats['total_parent_urls'] = len(parent_urls)
            print(f"\n✓ 读取到 {len(parent_urls)} 个母链接")
        except Exception as e:
            print(f"\n✗ 读取失败: {e}")
            return

        # 测试模式限制
        if limit:
            parent_urls = parent_urls[:limit]
            print(f"✓ 测试模式：处理前 {limit} 个母链接")

        # 收集所有需要处理的URL
        all_urls_to_process = []

        # 第一阶段：发现和筛选
        for i, parent_url in enumerate(parent_urls, 1):
            print(f"\n{'#'*70}")
            print(f"母链接 [{i}/{len(parent_urls)}]: {parent_url}")
            print(f"{'#'*70}")

            # 1. 处理母链接本身
            all_urls_to_process.append(parent_url)

            # 2. 发现并筛选子链接
            if auto_crawl_children:
                try:
                    child_urls = self.discover_and_filter(parent_url)

                    if child_urls:
                        all_urls_to_process.extend(child_urls)
                        print(f"\n✓ 从此母链接发现 {len(child_urls)} 个有价值的子链接")
                    else:
                        print(f"\n⚠️  未发现有价值的子链接")

                except Exception as e:
                    print(f"\n✗ 链接筛选失败: {e}")

            # 延迟
            if i < len(parent_urls):
                time.sleep(2)

        # 去重
        unique_urls = list(dict.fromkeys(all_urls_to_process))
        self.stats['total_processed'] = len(unique_urls)

        # 显示摘要
        print(f"\n{'='*70}")
        print(f"发现和筛选完成")
        print(f"{'='*70}")
        print(f"母链接数: {len(parent_urls)}")
        print(f"发现的链接总数: {self.stats['total_discovered']}")
        print(f"筛选后保留: {self.stats['total_filtered']}")
        print(f"待处理总数: {len(unique_urls)} (含母链接)")
        print(f"{'='*70}")

        # 保存发现的链接
        discovered_file = 'discovered_links.txt'
        with open(discovered_file, 'w', encoding='utf-8') as f:
            f.write(f"# 发现和筛选的链接\n")
            f.write(f"# 母链接: {len(parent_urls)}\n")
            f.write(f"# 子链接: {len(unique_urls) - len(parent_urls)}\n")
            f.write(f"# 总计: {len(unique_urls)}\n\n")

            for url in unique_urls:
                f.write(f"{url}\n")

        print(f"\n✓ 链接列表已保存到: {discovered_file}")

        # 询问确认
        if ask_confirmation and len(unique_urls) > 10:
            print(f"\n{'='*70}")
            print(f"⚠️  即将处理 {len(unique_urls)} 个URL")
            print(f"预计时间: ~{len(unique_urls) * 2.5:.0f} 分钟")
            print(f"预计成本: ~￥{len(unique_urls) * 0.012:.2f}")
            print(f"{'='*70}")

            response = input("\n是否继续? (yes/no): ").strip().lower()
            if response not in ['yes', 'y', '是']:
                print("\n✗ 用户取消")
                print(f"提示: 可以直接处理 {discovered_file} 中的链接:")
                print(f"  python3 batch_scrape.py --urls {discovered_file}")
                return

        # 第二阶段：批量处理
        print(f"\n{'='*70}")
        print(f"开始批量处理 {len(unique_urls)} 个URL")
        print(f"{'='*70}")

        for i, url in enumerate(unique_urls, 1):
            self.process_url(url, i, len(unique_urls))

            # 延迟
            if i < len(unique_urls):
                print(f"\n⏱️  等待 {self.delay} 秒后继续...")
                time.sleep(self.delay)

        # 保存失败记录
        if self.failed_urls:
            failed_file = 'failed_urls.txt'
            with open(failed_file, 'w', encoding='utf-8') as f:
                f.write(f"# 失败的URL - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 共 {len(self.failed_urls)} 个\n\n")

                for item in self.failed_urls:
                    f.write(f"{item['url']}\n")
                    f.write(f"# 错误: {item['error']}\n\n")

            print(f"\n✓ 失败记录保存到: {failed_file}")

        # 最终统计
        self.print_final_stats()

    def print_final_stats(self):
        """打印最终统计"""
        print(f"\n{'='*70}")
        print(f"处理完成")
        print(f"{'='*70}")
        print(f"母链接数: {self.stats['total_parent_urls']}")
        print(f"发现链接总数: {self.stats['total_discovered']}")
        print(f"筛选后保留: {self.stats['total_filtered']}")
        print(f"实际处理: {self.stats['total_processed']}")
        print(f"")
        print(f"成功: {self.stats['success']} ({self.stats['success']/self.stats['total_processed']*100:.1f}%)")
        print(f"失败: {self.stats['failed']} ({self.stats['failed']/self.stats['total_processed']*100:.1f}%)")
        print(f"跳过: {self.stats['skipped']}")
        print(f"")
        print(f"输出目录: {self.output_dir}")
        print(f"{'='*70}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='智能批量爬虫（自动发现子链接）')
    parser.add_argument(
        '--urls',
        default=str(Path.home() / 'Downloads' / 'Luna-AI-Knowledge' / 'ai_learning_urls.txt'),
        help='母链接列表文件'
    )
    parser.add_argument(
        '--output',
        default=str(Path.home() / 'Downloads' / 'Luna-AI-Knowledge'),
        help='输出目录'
    )
    parser.add_argument(
        '--delay',
        type=int,
        default=3,
        help='每个URL处理后的延迟（秒）'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='限制母链接数量（测试模式）'
    )
    parser.add_argument(
        '--no-children',
        action='store_true',
        help='不自动爬取子链接'
    )
    parser.add_argument(
        '--yes',
        action='store_true',
        help='跳过确认，直接开始'
    )

    args = parser.parse_args()

    # 确保输出目录存在
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建智能爬虫
    scraper = SmartBatchScraper(
        output_dir=output_dir,
        delay=args.delay
    )

    # 开始处理
    scraper.smart_batch_process(
        parent_urls_file=args.urls,
        auto_crawl_children=not args.no_children,
        limit=args.limit,
        ask_confirmation=not args.yes
    )


if __name__ == '__main__':
    main()
