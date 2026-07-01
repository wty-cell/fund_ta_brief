import sys
sys.path.insert(0, "src")

from utils import data_saver, deepseek_client, logger
from crawlers.regulator_crawler import RegulatorCrawler

def test_data_flow():
    print("\n=== 测试数据流程 ===")
    
    test_articles = [
        {
            "title": "中国证监会严肃查处私募基金玖瀛资产、腾创投资违法违规案件",
            "url": "http://www.csrc.gov.cn/csrc/c100028/c7641653/content.shtml",
            "source": "证监会",
            "publish_date": "2026-06-26",
            "content": "近日，中国证监会对深圳前海玖瀛资产管理有限公司（以下简称玖瀛资产）、深圳市前海腾创投资有限公司（以下简称腾创投资）依法作出行政处罚决定。经查，玖瀛资产、腾创投资存在违法违规行为，严重破坏了资本市场秩序，损害了投资者合法权益。证监会决定对玖瀛资产、腾创投资分别处以罚款，并采取监管措施。",
            "category": "监管公告",
        },
        {
            "title": "中国结算发布基金份额登记业务指引",
            "url": "http://www.chinaclear.cn/test",
            "source": "中国结算",
            "publish_date": "2026-06-25",
            "content": "中国证券登记结算有限责任公司今日发布《证券投资基金份额登记业务指引》，进一步规范基金份额登记业务，明确登记机构职责，保障投资者基金份额安全。指引自发布之日起施行。",
            "category": "业务通知",
        },
    ]
    
    print("步骤1: 保存原始数据")
    saved_file = data_saver.save_raw_data(test_articles, "regulator")
    print(f"  保存到: {saved_file}")
    
    print("\n步骤2: 加载保存的数据")
    loaded_data = data_saver.load_raw_data("regulator")
    print(f"  加载到 {len(loaded_data)} 条数据")
    
    print("\n步骤3: 生成摘要")
    for article in loaded_data[:2]:
        print(f"\n  标题: {article['title']}")
        print(f"  原文长度: {len(article['content'])}字")
        summary = deepseek_client.generate_summary(article['content'])
        print(f"  摘要长度: {len(summary)}字")
        print(f"  摘要内容: {summary}")
        
        article['summary'] = summary
    
    print("\n步骤4: 保存处理后数据")
    processed_file = data_saver.save_processed_data(loaded_data, "regulator")
    print(f"  保存到: {processed_file}")
    
    print("\n✓ 数据流程测试完成!")

if __name__ == "__main__":
    test_data_flow()
