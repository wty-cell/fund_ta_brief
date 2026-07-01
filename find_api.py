import sys
sys.path.insert(0, "src")

import requests
from bs4 import BeautifulSoup
import re

def find_api(url, name):
    print(f"\n=== 查找 {name} 的API接口 ===")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "lxml")
        
        all_text = response.text
        
        patterns = [
            r'url\s*[:=]\s*["\']([^"\']+?\.json[^"\']*)["\']',
            r'["\']([^"\']+?list[^"\']*\.json)["\']',
            r'["\']([^"\']+?data[^"\']*\.json)["\']',
            r'["\']([^"\']+?api[^"\']*)["\']',
            r'(https?://[^\s"\'<>]+?\.json)',
            r'(https?://[^\s"\'<>]+?/list[^"\'<>]*)',
        ]
        
        found_apis = []
        for pattern in patterns:
            matches = re.findall(pattern, all_text)
            for match in matches:
                if match not in found_apis and len(match) > 10:
                    found_apis.append(match)
        
        print(f"找到 {len(found_apis)} 个可能的API接口:")
        for api in found_apis[:10]:
            print(f"  {api}")
        
        if found_apis:
            print("\n尝试调用第一个API:")
            try:
                test_url = found_apis[0]
                if not test_url.startswith("http"):
                    if test_url.startswith("//"):
                        test_url = "https:" + test_url
                    elif test_url.startswith("/"):
                        test_url = url.split("/")[0] + "//" + url.split("/")[2] + test_url
                
                print(f"  URL: {test_url}")
                resp = requests.get(test_url, headers=headers, timeout=10)
                print(f"  状态码: {resp.status_code}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"  响应类型: {type(data).__name__}")
                    if isinstance(data, dict):
                        print(f"  键: {list(data.keys())[:10]}")
                    elif isinstance(data, list):
                        print(f"  列表长度: {len(data)}")
                        if data:
                            print(f"  第一条: {str(data[0])[:200]}")
                
            except Exception as e:
                print(f"  调用失败: {e}")
    
    except Exception as e:
        print(f"分析失败: {e}")

if __name__ == "__main__":
    sites = [
        ("http://www.csrc.gov.cn/csrc/c100028/common_xq_list.shtml", "证监会"),
        ("http://www.chinaclear.cn/zdjs/gsdtnew/about_gsdt.shtml", "中国结算"),
        ("https://www.amac.org.cn/xwfb/tzgg/", "基金业协会"),
    ]
    
    for url, name in sites:
        find_api(url, name)
