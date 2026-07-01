import sys
sys.path.insert(0, "src")

from crawlers.regulator_crawler import regulator_crawler
from crawlers.market_crawler import market_crawler
from crawlers.news_crawler import news_crawler

print("=== 开始采集所有数据 ===")

print("\n--- 1. 采集监管资讯 ---")
regulator_data = regulator_crawler.crawl_all(save_to_file=True, fetch_content=True)
print(f"监管资讯采集完成: {len(regulator_data)} 条")

print("\n--- 2. 采集行情数据 ---")
market_data = market_crawler.crawl_all(save_to_file=True)
print(f"行情数据采集完成: {len(market_data)} 条")

print("\n--- 3. 采集新闻快讯 ---")
news_data = news_crawler.crawl_all(save_to_file=True, fetch_content=True)
print(f"新闻快讯采集完成: {len(news_data)} 条")

print("\n=== 所有数据采集完成！===")
print(f"总计: {len(regulator_data) + len(market_data) + len(news_data)} 条")