import sys
sys.path.insert(0, "src")

from utils.material_manager import MaterialManager

def print_usage():
    print("素材池管理工具")
    print("用法: python manage_pool.py <命令> [选项]")
    print()
    print("命令:")
    print("  stats               查看候选池状态")
    print("  clear-pool [类别]   清空候选池 (类别: regulator/news，省略则清空全部)")
    print("  clear-sent [类别]   清空已发送记录 (类别: regulator/news，省略则清空全部)")
    print()
    print("示例:")
    print("  python manage_pool.py stats")
    print("  python manage_pool.py clear-pool")
    print("  python manage_pool.py clear-pool regulator")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    
    mm = MaterialManager()
    
    if command == "stats":
        stats = mm.get_pool_stats()
        print("候选池状态:")
        print()
        for cat, info in stats.items():
            cat_name = "监管资讯" if cat == "regulator" else "新闻快讯"
            print(f"  [{cat_name}]")
            print(f"    总条数: {info['total']}")
            print(f"    已发送: {info['sent_count']}")
            print(f"    最早日期: {info['earliest_date']}")
            print(f"    最新日期: {info['latest_date']}")
            print()
    
    elif command == "clear-pool":
        result = mm.clear_pool(category)
        print(result)
    
    elif command == "clear-sent":
        result = mm.clear_sent_history(category)
        print(result)
    
    else:
        print(f"未知命令: {command}")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()