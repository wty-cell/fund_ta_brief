import sys
sys.path.insert(0, "src")

import json
import time

from crawlers.regulator_crawler import regulator_crawler
from crawlers.market_crawler import market_crawler
from crawlers.news_crawler import news_crawler
from filters.data_filter import data_filter
from briefing.briefing_generator import briefing_generator
from utils.logger import logger
from utils.email_sender import email_sender
from utils.material_manager import MaterialManager

material_manager = MaterialManager()

print("=== 基金TA每日简报完整流程 ===")
print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# 步骤0: 清理过期素材
print("\n" + "="*50)
print("步骤0: 清理过期素材")
print("="*50)
material_manager.cleanup_expired()

# 步骤1: 采集监管资讯
print("\n" + "="*50)
print("步骤1: 采集监管资讯")
print("="*50)
start_time = time.time()
regulator_data = regulator_crawler.crawl_all(save_to_file=True, fetch_content=True)
material_manager.update_pool(regulator_data, "regulator")
elapsed = time.time() - start_time
print(f"监管资讯采集完成: {len(regulator_data)} 条，耗时 {elapsed:.1f}秒")

# 步骤2: 采集行情数据
print("\n" + "="*50)
print("步骤2: 采集行情数据")
print("="*50)
start_time = time.time()
market_data = market_crawler.crawl_all(save_to_file=True)
elapsed = time.time() - start_time
print(f"行情数据采集完成: {len(market_data)} 条，耗时 {elapsed:.1f}秒")

# 步骤3: 采集新闻快讯
print("\n" + "="*50)
print("步骤3: 采集新闻快讯")
print("="*50)
start_time = time.time()
news_data = news_crawler.crawl_all(save_to_file=True, fetch_content=True)
material_manager.update_pool(news_data, "news")
elapsed = time.time() - start_time
print(f"新闻快讯采集完成: {len(news_data)} 条，耗时 {elapsed:.1f}秒")

# 步骤4: 数据过滤
print("\n" + "="*50)
print("步骤4: 数据过滤")
print("="*50)
start_time = time.time()
candidate_regulator = material_manager.get_candidates("regulator")
candidate_news = material_manager.get_candidates("news")
filtered_data = data_filter.filter_all(candidate_regulator, candidate_news)
elapsed = time.time() - start_time
print(f"数据过滤完成，耗时 {elapsed:.1f}秒")
print(f"  - 候选池监管资讯: {len(candidate_regulator)} 条")
print(f"  - 候选池新闻快讯: {len(candidate_news)} 条")
print(f"  - 过滤后监管资讯: {len(filtered_data['regulator'])} 条")
print(f"  - 过滤后新闻快讯: {len(filtered_data['news'])} 条")

# 步骤5: 生成简报
print("\n" + "="*50)
print("步骤5: 生成简报")
print("="*50)
start_time = time.time()
html = briefing_generator.generate(market_data, filtered_data)
report_path = briefing_generator.save(html)
elapsed = time.time() - start_time
print(f"简报生成完成: {report_path}，耗时 {elapsed:.1f}秒")

# 步骤6: 发送邮件
print("\n" + "="*50)
print("步骤6: 发送邮件")
print("="*50)
start_time = time.time()
try:
    success = email_sender.send_briefing_email(html)
    if success:
        print("邮件发送成功")
        regulator_urls = [item["url"] for item in filtered_data["regulator"]]
        news_urls = [item["url"] for item in filtered_data["news"]]
        material_manager.mark_sent(regulator_urls, "regulator")
        material_manager.mark_sent(news_urls, "news")
    else:
        print("邮件发送失败")
except Exception as e:
    print(f"邮件发送异常: {e}")
elapsed = time.time() - start_time
print(f"邮件发送完成，耗时 {elapsed:.1f}秒")

# 输出汇总
print("\n" + "="*50)
print("流程汇总")
print("="*50)
print(f"采集阶段:")
print(f"  - 监管资讯: {len(regulator_data)} 条")
print(f"  - 行情数据: {len(market_data)} 条")
print(f"  - 新闻快讯: {len(news_data)} 条")
print(f"候选池状态:")
print(f"  - 监管资讯: {len(candidate_regulator)} 条")
print(f"  - 新闻快讯: {len(candidate_news)} 条")
print(f"过滤阶段:")
print(f"  - 监管资讯: {len(filtered_data['regulator'])} 条")
print(f"  - 新闻快讯: {len(filtered_data['news'])} 条")
print(f"输出文件:")
print(f"  - 简报: {report_path}")
print(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")