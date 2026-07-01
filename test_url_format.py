import sys
sys.path.insert(0, "src")

from playwright.sync_api import sync_playwright

def test_url_format():
    print("\n=== 测试Playwright返回的URL格式 ===")
    
    url = "http://www.csrc.gov.cn/csrc/c100028/common_xq_list.shtml"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            links = page.eval_on_selector_all(".list li a, .common-list li a", "elements => elements.map(el => ({title: el.textContent.trim(), href: el.href}))")
            
            print(f"找到 {len(links)} 个链接")
            for link in links[:5]:
                print(f"  标题: {link['title'][:50]}")
                print(f"  URL: {link['href']}")
                print(f"  URL是否已完整: {link['href'].startswith('http')}")
            
            browser.close()
    
    except Exception as e:
        print(f"失败: {e}")

if __name__ == "__main__":
    import time
    test_url_format()
