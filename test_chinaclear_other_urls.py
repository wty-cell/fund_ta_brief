from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re

urls = [
    ("资讯中心", "http://www.chinaclear.cn/zdjs/xxzx/"),
    ("资讯中心动态", "http://www.chinaclear.cn/zdjs/xxzx/gsdt/"),
    ("新闻动态", "http://www.chinaclear.cn/zdjs/gsdt/"),
    ("要闻动态2", "http://www.chinaclear.cn/zdjs/gsdtnew/index.shtml"),
    ("通知公告2", "http://www.chinaclear.cn/zdjs/tzgg/index.shtml"),
    ("业务通知", "http://www.chinaclear.cn/zdjs/ywtz/index.shtml"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    for name, url in urls:
        print(f"\n{'='*60}")
        print(f"{name}: {url}")
        print(f"{'='*60}")
        
        page = browser.new_page()
        try:
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            content = page.content()
            soup = BeautifulSoup(content, "lxml")
            
            title = soup.title.get_text() if soup.title else "无标题"
            print("页面标题:", title)
            
            if "维护" in title or "维护中" in title:
                print("⚠️ 页面正在维护")
                page.close()
                continue
            
            news_links = []
            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                text = a.get_text(strip=True)
                
                if not href or not text or len(text) < 6:
                    continue
                
                if ("/202" in href or "/2026" in href or "/2025" in href) and (".shtml" in href or ".html" in href):
                    full_url = urljoin("http://www.chinaclear.cn", href) if not href.startswith("http") else href
                    news_links.append((text, full_url))
            
            print(f"找到 {len(news_links)} 个新闻链接:")
            for i, (text, full_url) in enumerate(news_links[:10]):
                print(f"  [{i+1}] {text[:50]} - {full_url[:70]}")
                
        except Exception as e:
            print(f"获取页面失败: {e}")
        finally:
            page.close()
    
    browser.close()
