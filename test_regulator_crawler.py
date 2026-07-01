import sys
sys.path.insert(0, "src")

from crawlers import regulator_crawler, RegulatorCrawler

def test_crawler():
    print("\n=== 测试监管资讯爬虫 ===")
    
    crawler = RegulatorCrawler()
    
    articles = crawler.crawl_all()
    
    print(f"\n共采集到 {len(articles)} 条监管资讯")
    
    if articles:
        print("\n前5条资讯：")
        for i, article in enumerate(articles[:5]):
            print(f"\n第{i+1}条:")
            print(f"  标题: {article.get('title', '')[:50]}...")
            print(f"  来源: {article.get('source', '')}")
            print(f"  分类: {article.get('category', '')}")
            print(f"  日期: {article.get('publish_date', '')}")
            print(f"  链接: {article.get('url', '')[:60]}...")
    
    print("\n✓ 监管资讯爬虫测试完成")

if __name__ == "__main__":
    print("=" * 50)
    print("监管资讯爬虫测试")
    print("=" * 50)
    
    test_crawler()
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)
