#!/usr/bin/env python3
"""
Luna AI 知识库 - 批量爬取脚本
按分类批量爬取所有URL
"""

import time
import sys
sys.path.insert(0, '/Users/aifunengshangye/Downloads/Luna-AI-Knowledge')

from scraper_unified import UnifiedScraper

# URL分类配置
URL_CATEGORIES = {
    "02-案例库/销售成交案例": [
        "https://www.nayaai.io/blog/ai-sales-automation-roi-case-study",
        "https://superagi.com/from-hype-to-reality-real-world-case-studies-of-ai-agents-in-sales-success-stories-2025/",
        "https://superagi.com/ai-powered-marketing-automation-case-studies-on-how-ai-agents-boost-efficiency-and-roi-in-2025/",
        "https://superagi.com/2025-sales-automation-trends-how-ai-is-redefining-b2b-sales-engagements-and-roi/",
        "https://superagi.com/ai-in-sales-2025-top-10-case-studies-of-companies-that-doubled-their-pipeline-growth/",
        "https://www.cirrusinsight.com/blog/sales-automation-statistics",
        "https://martal.ca/ai-sales-automation-lb/",
        "https://persana.ai/blogs/ai-sales-agent-case-studies",
        "https://www.demandgenreport.com/industry-news/feature/ai-agents-revolutionize-b2b-marketing-in-2025-from-automation-to-strategy/51106/",
    ],
    "02-案例库/私域运营案例": [
        "https://www.theegg.com/social/china/how-to-leverage-private-domain-traffic/",
        "https://sekkeidigitalgroup.com/building-private-traffic-in-china/",
        "https://pltfrm.com.cn/solutions/china-social-media/social-media-marketing-kol-promotion-pr/2025-china-social-commerce-5-strategies-every-overseas-brand-must-master/60389/",
        "https://sekkeidigitalgroup.com/new-digital-marketing-trends-in-china/",
        "https://www.digitalcrew.agency/why-digital-first-strategies-are-now-essential-in-china/",
        "https://www.azoyagroup.com/blog/view/private-traffic-why-its-a-china-marketing-buzzword/",
        "https://www.ecinnovations.com/blog/digital-marketing-in-china/",
    ],
    "01-理论库/SaaS增长": [
        "https://www.userflow.com/blog/best-saas-customer-acquisition-strategies",
        "https://www.poweredbysearch.com/learn/saas-growth-strategy/",
        "https://www.amraandelma.com/saas-customer-acquisition-statistics/",
        "https://useshiny.com/blog/saas-growth-strategies/",
        "https://qubstudio.com/blog/saas-growth-strategies/",
        "https://www.paddle.com/resources/growth-strategies-for-saas",
        "https://www.surva.ai/blog/saas-growth-strategies",
    ],
    "02-案例库/直播电商案例": [
        "https://www.bigcommerce.com/articles/ecommerce/livestream-shopping/",
        "https://firework.com/blog/2025-short-form-video-stats",
        "https://www.shopify.com/blog/video-marketing-trends",
        "https://www.buywith.com/article/the-future-of-video-marketing/",
        "https://www.insivia.com/video-marketing-statistics-you-must-know-in-2025/",
        "https://www.vidjet.com/blog/video-marketing-trends-for-e-commerce-in-2025",
        "https://www.shopify.com/enterprise/blog/live-shopping",
    ],
}


def batch_crawl(category_filter=None):
    """批量爬取所有分类"""
    scraper = UnifiedScraper()
    total_success = 0
    total_failed = 0
    failed_urls = []

    for category, urls in URL_CATEGORIES.items():
        if category_filter and category != category_filter:
            continue

        print(f"\n{'='*60}")
        print(f"分类: {category} ({len(urls)}个)")
        print(f"{'='*60}")

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] {url[:60]}...")
            try:
                scraper.scrape(url, category)
                total_success += 1
            except Exception as e:
                print(f"❌ 失败: {str(e)[:50]}")
                total_failed += 1
                failed_urls.append(url)
            time.sleep(3)  # 避免请求过快

    print(f"\n{'='*60}")
    print(f"总计: 成功 {total_success}, 失败 {total_failed}")
    if failed_urls:
        print("失败URL:")
        for url in failed_urls:
            print(f"  - {url}")

    return total_success, total_failed


if __name__ == '__main__':
    import sys
    category = sys.argv[1] if len(sys.argv) > 1 else None
    batch_crawl(category)
