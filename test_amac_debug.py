import sys
import re
sys.path.insert(0, "src")

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

url = "https://www.amac.org.cn/xwfb/tzgg/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, timeout=30000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(5000)
    
    content = page.content()
    soup = BeautifulSoup(content, "lxml")
    
    print("=== 基金业协会页面结构分析 ===\n")
    
    print("1. 查找所有div及其class...")
    divs_with_class = soup.find_all("div", class_=True)
    print(f"   找到 {len(divs_with_class)} 个带class的div")
    for div in divs_with_class[:20]:
        classes = div.get("class", [])
        link_count = len(div.find_all("a", href=True))
        print(f"   class='{classes}' 链接数={link_count}")
    
    print("\n2. 查找新闻列表容器...")
    container_classes = ['news-list', 'article-list', 'list', 'content', 'main', 'news', 'list-container']
    for class_name in container_classes:
        containers = soup.find_all(class_=re.compile(class_name, re.I))
        if containers:
            print(f"   class包含'{class_name}': {len(containers)}个")
    
    print("\n3. 查找包含'/xwfb/'路径的链接...")
    all_as = soup.find_all("a", href=True)
    xwfb_links = []
    for a in all_as:
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if "/xwfb/" in href and len(text) >= 5:
            xwfb_links.append({"text": text, "href": href})
    print(f"   找到 {len(xwfb_links)} 个/xwfb/路径链接")
    for link in xwfb_links[:10]:
        print(f"   text='{link['text'][:60]}' href='{link['href'][:80]}'")
    
    print("\n4. 查找包含'2026'年份的链接...")
    year_links = []
    for a in all_as:
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if "/2026" in href and ".html" in href and len(text) >= 5:
            year_links.append({"text": text, "href": href})
    print(f"   找到 {len(year_links)} 个2026年链接")
    for link in year_links[:10]:
        print(f"   text='{link['text'][:60]}' href='{link['href'][:80]}'")
    
    print("\n5. 查找通知公告链接（不含党建）...")
    notice_links = []
    for a in all_as:
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if (("/tzgg/" in href or "/xhyw/" in href) and ".html" in href and 
            "/hydj/" not in href and "/党建" not in href and len(text) >= 5):
            notice_links.append({"text": text, "href": href})
    print(f"   找到 {len(notice_links)} 个通知公告链接")
    for link in notice_links[:15]:
        print(f"   text='{link['text'][:60]}' href='{link['href'][:80]}'")
    
    print("\n6. 查看通知公告链接的父元素...")
    for i, link in enumerate(notice_links[:5]):
        a_tag = soup.find("a", href=link["href"])
        if a_tag:
            parent = a_tag.parent
            grandparent = parent.parent if parent else None
            print(f"   [{i}] 父元素: {parent.name if parent else None} class={parent.get('class', []) if parent else None}")
            print(f"      祖父元素: {grandparent.name if grandparent else None} class={grandparent.get('class', []) if grandparent else None}")
    
    browser.close()