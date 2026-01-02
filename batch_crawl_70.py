#!/usr/bin/env python3
"""
Luna AI 知识库 - 批量爬取70个URL
"""

import time
import sys
sys.path.insert(0, '/Users/aifunengshangye/Downloads/Luna-AI-Knowledge')

from scraper_unified import UnifiedScraper

# 70个URL分类配置
URL_CATEGORIES = {
    "01-理论库/客户成功": [
        "https://www.custify.com/blog/14-customer-retention-strategies-for-saas-you-can-implement-today/",
        "https://www.trantorinc.com/blog/customer-retention-strategies",
        "https://www.worknet.ai/blog/saas-customer-retention-strategies",
        "https://paywithflash.com/saas-customer-retention-strategies/",
        "https://hiverhq.com/blog/customer-success-saas",
        "https://userpilot.com/blog/saas-customer-retention/",
        "https://blockbee.io/blog/post/saas-customer-retention-strategies",
        "https://www.onsaas.me/blog/saas-retention",
        "https://churnzero.com/blog/the-ultimate-guide-customer-success-in-saas/",
        "https://www.custify.com/blog/saas-retention-customer-success-transforms-subscription-growth/",
    ],
    "01-理论库/对话设计": [
        "https://botpress.com/blog/chatbot-design",
        "https://botpress.com/blog/conversation-design",
        "https://www.parallelhq.com/blog/chatbot-ux-design",
        "https://www.toptal.com/designers/ui/chatbot-ux-design",
        "https://www.gptbots.ai/blog/chatbot-design",
        "https://raw.studio/blog/conversational-ux-from-chatbots-to-ux-design/",
        "https://www.ibm.com/think/topics/chatbot-design",
        "https://lollypop-studio.medium.com/ui-ux-design-for-chatbot-best-practices-and-examples-5d69ff2840f5",
        "https://www.netguru.com/blog/chatbot-ux-tips",
        "https://www.interaction-design.org/literature/topics/chatbots",
    ],
    "01-理论库/提示词工程": [
        "https://www.lakera.ai/blog/prompt-engineering-guide",
        "https://www.news.aakashg.com/p/prompt-engineering",
        "https://www.digitalocean.com/resources/articles/prompt-engineering-best-practices",
        "https://www.ibm.com/think/prompt-engineering",
        "https://codesignal.com/blog/prompt-engineering-best-practices-2025/",
        "https://claude.com/blog/best-practices-for-prompt-engineering",
        "https://www.godofprompt.ai/blog/prompt-engineering-evolution-adapting-to-2025-changes",
        "https://orq.ai/blog/what-is-the-best-way-to-think-of-prompt-engineering",
        "https://medium.com/@hamzamaq96/2025-beginners-guide-to-prompt-engineering-step-by-step-roadmap-2b3435eac54a",
        "https://profiletree.com/prompt-engineering-in-2025-trends-best-practices-profiletrees-expertise/",
    ],
    "01-理论库/工作流自动化": [
        "https://www.digidop.com/blog/n8n-vs-make-vs-zapier",
        "https://medium.com/@aminsiddique95/the-top-15-n8n-use-cases-that-are-revolutionizing-workflow-automation-in-2025-cbe08df08702",
        "https://blog.n8n.io/ai-workflow-automation/",
        "https://humansai.io/blog/make-vs-zapier-vs-n8n-comparison-2025/",
        "https://hatchworks.com/blog/ai-agents/n8n-vs-zapier/",
        "https://www.lleverage.ai/blog/n8n-vs-lleverage-vs-make-vs-zapier-what-is-the-best-automation-tool",
        "https://blog.promptlayer.com/n8n-vs-zapier/",
        "https://blog.n8n.io/best-ai-workflow-automation-tools/",
        "https://max-productive.ai/ai-tools/n8n/",
    ],
    "01-理论库/MCP协议": [
        "https://en.wikipedia.org/wiki/Model_Context_Protocol",
        "https://www.anthropic.com/news/model-context-protocol",
        "https://modelcontextprotocol.io/specification/2025-11-25",
        "https://www.descope.com/learn/post/mcp",
        "https://www.thoughtworks.com/en-us/insights/blog/generative-ai/model-context-protocol-mcp-impact-2025",
        "http://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/",
        "https://developers.openai.com/apps-sdk/concepts/mcp-server/",
        "https://datasciencedojo.com/blog/guide-to-model-context-protocol/",
        "https://blog.equinix.com/blog/2025/08/06/what-is-the-model-context-protocol-mcp-how-will-it-enable-the-future-of-agentic-ai/",
    ],
    "01-理论库/知识图谱": [
        "https://www.gend.co/blog/knowledge-graphs-enterprise-ai",
        "https://www.glean.com/blog/knowledge-graph-agentic-engine",
        "https://blog.metaphacts.com/from-data-to-decisions-how-enterprise-ai-powered-by-knowledge-graphs-is-redefining-business-intelligence",
        "https://www.cio.com/article/3808569/knowledge-graphs-the-missing-link-in-enterprise-ai.html",
        "https://www.pingcap.com/article/knowledge-graph-tools-ai-development-2025/",
        "https://www.superblocks.com/blog/enterprise-knowledge-graph",
        "https://enterprise-knowledge.com/how-a-knowledge-graph-supports-ai-technical-considerations/",
        "https://medium.com/@adnanmasood/the-knowledge-graph-advantage-how-smart-companies-are-using-knowledge-graphs-to-power-ai-and-drive-59f285602683",
    ],
    "02-案例库/AI个性化案例": [
        "https://ecomposer.io/blogs/ecommerce/ai-personalization-ecommerce",
        "https://emarsys.com/learn/blog/e-commerce-personalization-trends/",
        "https://stackinfluence.com/hyper-personalization-e-commerce-roi-2025/",
        "https://www.ibm.com/think/topics/ai-personalization",
        "https://www.dynamicyield.com/personalization-maturity/",
        "https://www.bigcommerce.com/articles/ecommerce/ecommerce-ai/",
        "https://www.bloomreach.com/en/blog/why-ai-is-the-future-of-e-commerce",
        "https://www.envive.ai/post/personalized-shopping-experience-statistics",
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
