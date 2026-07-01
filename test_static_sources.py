import sys
sys.path.insert(0, "src")

import requests
from bs4 import BeautifulSoup

def test_url(url, name):
    print(f"\n=== 测试 {name}: {url} ===")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "lxml")
        
        print(f"状态码: {response.status_code}")
        print(f"页面标题: {soup.title.string if soup.title else '无'}")
        
        all_links = soup.select("a")
        article_links = []
        
        for link in all_links:
            href = link.get("href", "")
            title = link.get_text(strip=True)
            
            if href and title and len(title) > 5:
                if "/content.shtml" in href or "/article/" in href or "/detail/" in href:
                    article_links.append((title, href))
        
        print(f"找到文章链接: {len(article_links)}")
        for title, href in article_links[:5]:
            if not href.startswith("http"):
                href = url.split("/")[0] + "//" + url.split("/")[2] + href
            print(f"  {title[:50]} -> {href[:80]}")
        
        return len(article_links) > 0
    
    except Exception as e:
        print(f"失败: {e}")
        return False

if __name__ == "__main__":
    static_urls = [
        ("http://www.csrc.gov.cn/csrc/c100028/c7641653/content.shtml", "证监会示例详情页"),
        ("http://www.chinaclear.cn/zdjs/gsdtnew/202606/t20260629_33853.html", "中国结算示例详情页"),
        ("https://www.amac.org.cn/xwfb/tzgg/202606/t20260628_19564.html", "基金业协会示例详情页"),
    ]
    
    for url, name in static_urls:
        test_url(url, name)
