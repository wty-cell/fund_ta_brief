from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re

urls = [
    ("要闻动态", "http://www.chinaclear.cn/zdjs/gsdtnew/about_gsdt.shtml"),
    ("要闻动态目录", "http://www.chinaclear.cn/zdjs/gsdtnew/"),
    ("通知公告", "http://www.chinaclear.cn/zdjs/tzgg/"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    for name, url in urls:
        print(f"\n{'='*70}")
        print(f"{name}: {url}")
        print(f"{'='*70}")
        
        page = browser.new_page()
        try:
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            content = page.content()
            soup = BeautifulSoup(content, "lxml")
            
            print("页面标题:", soup.title.get_text() if soup.title else "无标题")
            
            html_length = len(content)
            print(f"HTML长度: {html_length}")
            
            if html_length < 5000:
                print("\n⚠️ 页面内容过短，可能被重定向或需要JS渲染")
                print("页面前500字符:", content[:500])
            
            print("\n=== 查找页面中的所有列表结构 ===")
            for tag in ["ul", "ol", "div"]:
                elements = soup.find_all(tag)
                for elem in elements:
                    classes = elem.get("class", [])
                    ids = elem.get("id", "")
                    children = elem.find_all(["li", "a"])
                    
                    if len(children) >= 3:
                        text_preview = elem.get_text(strip=True)[:100]
                        print(f"\n{tag} class={classes} id={ids}")
                        print(f"  子元素数: {len(children)}")
                        print(f"  文本预览: {text_preview}")
            
            print("\n=== 查找所有包含日期的元素 ===")
            all_elements = soup.find_all(text=True)
            date_pattern = re.compile(r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日号]?')
            for elem in all_elements:
                text = elem.strip()
                if date_pattern.search(text) and len(text) >= 8:
                    parent = elem.parent
                    print(f"日期文本: '{text[:50]}'")
                    print(f"  父标签: {parent.name} class={parent.get('class', [])}")
            
            print("\n=== 查找所有可能的新闻链接 ===")
            news_links = []
            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                text = a.get_text(strip=True)
                
                if not href or not text or len(text) < 6:
                    continue
                
                if ("/202" in href or "/2026" in href or "/2025" in href) and (".shtml" in href or ".html" in href):
                    full_url = urljoin("http://www.chinaclear.cn", href) if not href.startswith("http") else href
                    news_links.append((text, full_url))
            
            print(f"找到 {len(news_links)} 个包含日期路径的链接:")
            for i, (text, full_url) in enumerate(news_links[:15]):
                print(f"  [{i+1}] {text[:50]} - {full_url}")
                
        except Exception as e:
            print(f"获取页面失败: {e}")
        finally:
            page.close()
    
    browser.close()
