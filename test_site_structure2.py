import sys
sys.path.insert(0, "src")

from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup

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
            soup = BeautifulSoup(html, "lxml")
            
            print("\n--- 查找所有包含新闻列表的容器 ---")
            for tag in soup.find_all(['div', 'ul', 'table']):
                if tag.has_attr('class'):
                    class_name = ' '.join(tag['class'])
                    if any(keyword in class_name.lower() for keyword in ['list', 'news', 'article', 'content', 'item']):
                        links = tag.find_all('a')
                        if links:
                            titles = [a.get_text(strip=True) for a in links[:5] if a.get_text(strip=True) and len(a.get_text(strip=True)) > 5]
                            if titles:
                                print(f"\n容器: <{tag.name} class=\"{class_name}\">")
                                print(f"  包含 {len(links)} 个链接")
                                for t in titles[:3]:
                                    print(f"    - {t[:60]}")
            
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
            soup = BeautifulSoup(html, "lxml")
            
            print("\n--- 查找所有包含新闻列表的容器 ---")
            for tag in soup.find_all(['div', 'ul', 'table']):
                if tag.has_attr('class'):
                    class_name = ' '.join(tag['class'])
                    if any(keyword in class_name.lower() for keyword in ['list', 'news', 'article', 'content', 'item', 'tzgg']):
                        links = tag.find_all('a')
                        if links:
                            titles = [a.get_text(strip=True) for a in links[:5] if a.get_text(strip=True) and len(a.get_text(strip=True)) > 5]
                            if titles:
                                print(f"\n容器: <{tag.name} class=\"{class_name}\">")
                                print(f"  包含 {len(links)} 个链接")
                                for t in titles[:3]:
                                    print(f"    - {t[:60]}")
            
            browser.close()
    
    except Exception as e:
        print(f"失败: {e}")

if __name__ == "__main__":
    test_chinaclear()
    test_amac()
