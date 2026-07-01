import sys
sys.path.insert(0, "src")

from playwright.sync_api import sync_playwright
import time

def test_chinaclear():
    print("\n=== 测试中国结算页面结构 ===")
    url = "http://www.chinaclear.cn/zdjs/gsdtnew/about_gsdt.shtml"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            html = page.content()
            
            import re
            link_count = len(re.findall(r'<a[^>]+href=', html))
            print(f"页面中链接总数: {link_count}")
            
            list_selectors = [
                ".list li a",
                ".news-list li a",
                ".article-list li a",
                ".newslist li a",
                ".list-content li a",
                "ul li a",
                "div.news a",
                "div.list a"
            ]
            
            for selector in list_selectors:
                count = page.locator(selector).count()
                if count > 0:
                    print(f"  选择器 '{selector}' 匹配到 {count} 个元素")
                    
                    texts = page.locator(selector).all_text_contents()
                    for text in texts[:3]:
                        print(f"    - {text[:50]}")
            
            browser.close()
    
    except Exception as e:
        print(f"失败: {e}")

def test_amac():
    print("\n=== 测试基金业协会页面结构 ===")
    url = "https://www.amac.org.cn/xwfb/tzgg/"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            html = page.content()
            
            import re
            link_count = len(re.findall(r'<a[^>]+href=', html))
            print(f"页面中链接总数: {link_count}")
            
            list_selectors = [
                ".list li a",
                ".news-list li a",
                ".article-list li a",
                ".tzgg-list li a",
                "ul li a",
                "div.news a",
                "div.list a",
                ".newsList li a",
                ".news_list li a"
            ]
            
            for selector in list_selectors:
                count = page.locator(selector).count()
                if count > 0:
                    print(f"  选择器 '{selector}' 匹配到 {count} 个元素")
                    
                    texts = page.locator(selector).all_text_contents()
                    for text in texts[:3]:
                        print(f"    - {text[:50]}")
            
            browser.close()
    
    except Exception as e:
        print(f"失败: {e}")

if __name__ == "__main__":
    test_chinaclear()
    test_amac()
