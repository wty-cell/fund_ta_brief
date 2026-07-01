import sys
sys.path.insert(0, "src")

from utils import deepseek_client, logger

def test_single_summary():
    print("\n=== 测试单条摘要生成 ===")
    
    test_content = """证监会发布《公开募集证券投资基金注册登记业务管理规定》，明确了基金注册登记机构的准入条件、业务规范和监督管理要求。新规要求注册登记机构应当建立健全内部控制制度，严格执行基金份额登记、清算交收、账户管理等业务规则，保障投资者合法权益。同时，新规还强化了对注册登记机构的监督检查，明确了违规行为的处罚措施。"""
    
    print(f"原始内容长度: {len(test_content)}字")
    
    summary = deepseek_client.generate_summary(test_content)
    
    print(f"生成摘要长度: {len(summary)}字")
    print(f"摘要内容:\n{summary}")
    print("✓ 单条摘要生成测试完成")

def test_batch_summary():
    print("\n=== 测试批量摘要生成 ===")
    
    test_contents = [
        "央行宣布下调存款准备金率0.25个百分点，释放长期资金约5000亿元。此次降准旨在支持实体经济发展，降低企业融资成本。",
        "沪深300指数今日收盘报3850点，上涨0.8%。市场情绪回暖，科技板块领涨，新能源、半导体等板块表现活跃。",
        "基金业协会发布最新数据，截至上月末，公募基金规模突破28万亿元，较年初增长12%。权益类基金和债券基金均实现正增长。"
    ]
    
    summaries = deepseek_client.batch_generate(test_contents)
    
    for i, (content, summary) in enumerate(zip(test_contents, summaries)):
        print(f"\n第{i+1}条:")
        print(f"  原始长度: {len(content)}字")
        print(f"  摘要长度: {len(summary)}字")
        print(f"  摘要: {summary}")
    
    print("✓ 批量摘要生成测试完成")

if __name__ == "__main__":
    print("=" * 50)
    print("DeepSeek API 调用测试")
    print("=" * 50)
    
    test_single_summary()
    test_batch_summary()
    
    print("\n" + "=" * 50)
    print("所有测试完成!")
    print("=" * 50)
