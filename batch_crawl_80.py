#!/usr/bin/env python3
"""
Luna AI 知识库 - 批量爬取80+个URL
"""

import time
import sys
sys.path.insert(0, '/Users/aifunengshangye/Downloads/Luna-AI-Knowledge')

from scraper_unified import UnifiedScraper

# 80+个URL分类配置
URL_CATEGORIES = {
    "01-理论库/AI商业模式": [
        "https://www.aalpha.net/blog/how-to-monetize-ai-agents/",
        "https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/upgrading-software-business-models-to-thrive-in-the-ai-era",
        "https://medium.com/aimonks/10-profitable-ai-agent-business-models-to-launch-in-2025-3bad38ae4bc9",
        "https://www.mckinsey.com/capabilities/business-building/our-insights/intelligence-at-scale-data-monetization-in-the-age-of-gen-ai",
        "https://blog.crossmint.com/monetize-ai-agents/",
        "https://www.withorb.com/blog/ai-monetization",
        "https://userpilot.com/blog/ai-saas-monetization/",
        "https://weezly.com/blog/monetize-ai-agents-automation-in-2025/",
        "https://appinventiv.com/blog/ai-agent-business-ideas/",
        "https://devsquad.com/blog/ai-agent-startups",
        "https://gaper.io/the-10-ai-agents-every-startup-founder-should-know-in-2025/",
        "https://www.thevccorner.com/p/ai-agent-startup-ideas-2025",
        "https://www.cxotalk.com/episode/ai-agents-for-small-business-winning-in-2025",
        "https://www.zealousys.com/blog/ai-agent-business-ideas/",
        "https://medium.com/the-bonsai-labs-dispatch/the-next-10-person-startup-is-actually-a-3-person-team-50-ai-agents-7f6c8b1c4a6a",
    ],
    "02-案例库/AI客服案例": [
        "https://www.freshworks.com/How-AI-is-unlocking-ROI-in-customer-service/",
        "https://www.fullview.io/blog/ai-customer-service-stats",
        "https://www.sprinklr.com/blog/customer-service-roi/",
        "https://www.sobot.io/article/ai-customer-service-case-studies-2025-support-satisfaction-cost",
        "https://medium.com/@devashish_m/roi-of-ai-in-cx-prove-your-spend-bc95383ff702",
        "https://www.fullview.io/blog/ai-chatbot-statistics",
        "https://dialzara.com/blog/measuring-ai-chatbot-roi-case-studies",
        "https://www.nexgencloud.com/blog/case-studies/how-ai-and-rag-chatbots-cut-customer-service-costs-by-millions",
        "https://www.virtasant.com/ai-today/ai-roi-customer-support",
        "https://www.mdpi.com/2078-2489/16/12/1078",
        "https://www.demandsage.com/ai-agents-startups/",
        "https://www.lindy.ai/blog/best-ai-agents-small-business",
    ],
    "01-理论库/AI销售培训": [
        "https://whatfix.com/blog/ai-sales-coaching/",
        "https://www.hyperbound.ai/",
        "https://secondnature.ai/",
        "https://www.retorio.com/blog/top-ai-sales-coaching-software-2025",
        "https://www.spekit.com/blog/ai-sales-training-software",
        "https://www.quantified.ai/",
        "https://www.retorio.com/",
        "https://www.trellus.ai/post/ai-sales-coaching-tools",
        "https://superagi.com/top-10-ai-tools-transforming-sales-coaching-in-2025-a-comprehensive-guide/",
        "https://www.momentum.io/blog/top-ai-driven-sales-coaching-platforms-2025-buyers-guide-for-gtm-teams",
    ],
    "01-理论库/AI数字分身": [
        "https://fortune.com/2025/03/24/ai-avatars-clones-influencers-creator-economy/",
        "https://www.argil.ai/blog/digital-creator-meaning-in-2025-how-ai-is-changing-the-norm",
        "https://dmexco.com/stories/the-creator-economy-trends-for-2025-the-boom-continues/",
        "https://pitchavatar.com/what-is-ai-avatar/",
        "https://techcrunch.com/2025/12/23/lemon-slice-nabs-10-5m-from-yc-and-matrix-to-build-out-its-digital-avatar-tech/",
        "https://www.argil.ai/blog/heygen-real-time-conversational-avatars-complete-2025-review-analysis",
        "https://www.shareloapp.com/blog/ai-avatar-platforms-for-video-creation-free-and-paid",
        "https://navid.me/clone-yourself-with-ai/",
        "https://www.gartner.com/reviews/market/ai-avatars",
        "https://ravatar.com/",
    ],
    "01-理论库/垂直AI": [
        "https://www.superannotate.com/blog/vertical-ai-agents",
        "https://a16z.com/vsaas-vertical-saas-ai-opens-new-markets/",
        "https://www.turing.com/resources/vertical-ai-agents",
        "https://modall.ca/blog/saas-trends",
        "https://www.ishir.com/blog/224961/vertical-saas-micro-saas-why-niche-focused-products-win-in-2025.htm",
        "https://www.allaboutai.com/ai-agents/vertical-agents/",
        "https://entrepreneurloop.com/profitable-saas-startup-ideas-2026/",
        "https://aimmediahouse.com/ai-startups/vertical-ai-agents-will-dominate-2025",
        "https://yazo.ai/blog/the-rise-of-vertical-saas-why-niche-beats-broad-in-2025/",
        "https://www.bain.com/insights/will-agentic-ai-disrupt-saas-technology-report-2025/",
        "https://www.ycombinator.com/companies/industry/ai-assistant",
    ],
    "01-理论库/AI开发平台": [
        "https://www.io404.com/2025/06/06/n8n-vs-make-dify-coze-zipped-ai-agent-micro-business/",
        "https://jimmysong.io/blog/open-source-ai-agent-workflow-comparison/",
        "https://blog.n8n.io/best-ai-agent-builders/",
        "https://go.lightnode.com/tech/n8n-dify-coze",
        "https://www.surfercloud.com/blog/n8n-vs-dify-vs-coze-a-detailed-comparison-of-automation-and-ai-platforms",
        "https://jinlow.medium.com/the-rise-of-low-code-ai-agent-platforms-mastering-dify-n8n-and-coze-in-2025-cbd8aad04ae7",
        "https://medium.com/dataprophet/confused-by-ai-agent-tools-how-i-mastered-n8n-coze-and-dify-d42164cb45ab",
        "https://www.aisharenet.com/en/yiwendudongn8nan/",
        "https://medium.com/generative-ai-revolution-ai-native-transformation/dify-vs-n8n-which-platform-should-power-your-ai-automation-stack-in-2025-e6d971f313a5",
    ],
    "01-理论库/私域AI运营": [
        "https://www.theegg.com/social/china/how-to-leverage-private-domain-traffic/",
        "https://www.oreateai.com/blog/2025-comprehensive-analysis-of-private-domain-live-streaming-systems-and-indepth-industry-solutions-report/255cb34280004941fe8d07adcdb2a986",
        "https://www.marketingfuture.com/brand-marketing/digital-marketing-trends-in-china-february-2025-market-analysis/",
        "https://www.digitalcrew.agency/why-digital-first-strategies-are-now-essential-in-china/",
        "https://techbuzzchina.substack.com/p/the-state-of-chinese-ai-apps-2025",
        "https://www.klover.ai/tencent-ai-strategy-dominate-ai-with-ecosystem-advantage/",
        "https://www.charlesworth-group.com/blog/the-future-of-wechat-e-commerce-in-2025-emerging-trends-and-strategic-insights/",
        "https://blog.applabx.com/the-state-of-seo-in-china-navigating-the-digital-landscape-in-2025/",
    ],
}


def batch_crawl(category_filter=None):
    """批量爬取指定分类"""
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
            time.sleep(3)

    print(f"\n{'='*60}")
    print(f"总计: 成功 {total_success}, 失败 {total_failed}")
    if failed_urls:
        print("失败URL:")
        for url in failed_urls:
            print(f"  - {url}")

    return total_success, total_failed


if __name__ == '__main__':
    category = sys.argv[1] if len(sys.argv) > 1 else None
    batch_crawl(category)
