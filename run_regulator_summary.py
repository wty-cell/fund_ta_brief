import sys
sys.path.insert(0, 'src')

from crawlers.regulator_crawler import regulator_crawler
from utils.deepseek_client import deepseek_client
from utils.data_saver import data_saver

print('=== 开始运行监管资讯爬虫 ===')
articles = regulator_crawler.crawl_all(save_to_file=True, fetch_content=True)
print(f'采集完成，共 {len(articles)} 条')

print('\n=== 开始生成摘要 ===')
total_articles = len(articles)
for i, article in enumerate(articles):
    if article.get('content'):
        print(f'\n[{i+1}/{total_articles}] 标题: {article["title"]}')
        print(f'来源: {article["source"]}')
        print(f'原文长度: {len(article["content"])}字')
        
        summary = deepseek_client.generate_summary(article['content'])
        article['summary'] = summary
        print(f'摘要长度: {len(summary)}字')
        print(f'摘要: {summary}')

data_saver.save_processed_data(articles, 'regulator')
print(f'\n=== 处理完成，已保存到 data/processed ===')
