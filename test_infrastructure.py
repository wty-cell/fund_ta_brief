import sys
sys.path.insert(0, "src")

from utils import logger, config, file_cleaner

def test_logger():
    print("\n=== 测试日志工具 ===")
    logger.info("测试日志信息")
    logger.warning("测试日志警告")
    logger.error("测试日志错误")
    print("✓ 日志工具测试完成")

def test_config_loader():
    print("\n=== 测试配置加载工具 ===")
    
    email_config = config.get_email_config()
    print(f"发件人邮箱: {email_config['sender']['address']}")
    print(f"SMTP服务器: {email_config['sender']['smtp_server']}")
    print(f"SMTP端口: {email_config['sender']['smtp_port']}")
    print(f"收件人数量: {len(email_config['recipients'])}")
    
    crawler_config = config.get_crawler_config()
    print(f"请求间隔: {crawler_config['request_interval']}秒")
    print(f"超时时间: {crawler_config['timeout']}秒")
    
    summarizer_config = config.get_summarizer_config()
    print(f"摘要最大字数: {summarizer_config['max_chars']}")
    print(f"摘要方式: {summarizer_config['method']}")
    
    data_config = config.get_data_config()
    print(f"数据保留天数: {data_config['retention_days']}")
    print(f"日志保留天数: {data_config['logs_retention_days']}")
    
    print("✓ 配置加载工具测试完成")

def test_file_cleaner():
    print("\n=== 测试文件清理工具 ===")
    result = file_cleaner.clean_all()
    print(f"数据目录删除文件数: {result['data']}")
    print(f"日志目录删除文件数: {result['logs']}")
    print("✓ 文件清理工具测试完成")

if __name__ == "__main__":
    print("=" * 50)
    print("基础设施模块测试")
    print("=" * 50)
    
    test_logger()
    test_config_loader()
    test_file_cleaner()
    
    print("\n" + "=" * 50)
    print("所有测试完成!")
    print("=" * 50)
