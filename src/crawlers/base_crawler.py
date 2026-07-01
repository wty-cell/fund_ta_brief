import time
import requests
from typing import Optional, Dict, Any

from utils.logger import logger
from utils.config_loader import config

class BaseCrawler:
    def __init__(self):
        self.request_interval = config.get_crawler_config()["request_interval"]
        self.timeout = config.get_crawler_config()["timeout"]
        self.retry_times = config.get_crawler_config()["retry_times"]
        self.headless = config.get_crawler_config()["headless"]
        self.last_request_time = 0
        self.playwright_browser = None
    
    def wait_interval(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self.last_request_time = time.time()
    
    def request_with_retry(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        self.wait_interval()
        
        for attempt in range(self.retry_times):
            try:
                response = requests.request(method, url, timeout=self.timeout, **kwargs)
                response.raise_for_status()
                logger.info(f"请求成功: {url}")
                return response
            
            except requests.exceptions.RequestException as e:
                logger.error(f"请求失败 (第{attempt+1}/{self.retry_times}次) [{url}]: {e}")
                
                if attempt < self.retry_times - 1:
                    time.sleep(self.request_interval * 2)
                else:
                    logger.warning(f"请求最终失败: {url}")
                    return None
    
    def crawl_with_requests(self, source: Dict[str, Any]) -> Optional[list]:
        try:
            logger.info(f"使用requests采集 [{source['name']}]: {source['url']}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate",
            }
            
            response = self.request_with_retry(source["url"], headers=headers)
            if not response:
                return None
            
            response.encoding = response.apparent_encoding
            
            return self.parse_content(response.text, source)
        
        except Exception as e:
            logger.error(f"requests采集失败 [{source['name']}]: {e}")
            return None
    
    def crawl_with_playwright(self, source: Dict[str, Any]) -> Optional[list]:
        try:
            logger.info(f"使用Playwright采集 [{source['name']}]: {source['url']}")
            
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                
                try:
                    page.goto(source["url"], timeout=self.timeout * 1000)
                    page.wait_for_load_state("networkidle")
                    time.sleep(2)
                    
                    content = page.content()
                    result = self.parse_content(content, source)
                    
                    browser.close()
                    return result
                    
                except Exception as e:
                    logger.error(f"Playwright页面操作失败 [{source['name']}]: {e}")
                    browser.close()
                    return None
        
        except Exception as e:
            logger.error(f"Playwright采集失败 [{source['name']}]: {e}")
            return None
    
    def crawl_source(self, source: Dict[str, Any]) -> Optional[list]:
        preferred = source.get("preferred", "requests")
        fallback = source.get("fallback", None)
        
        if preferred == "requests":
            result = self.crawl_with_requests(source)
            if result is not None:
                return result
            
            if fallback == "playwright":
                logger.info(f"requests失败，降级使用Playwright [{source['name']}]")
                return self.crawl_with_playwright(source)
            
        elif preferred == "playwright":
            result = self.crawl_with_playwright(source)
            if result is not None:
                return result
            
            if fallback == "requests":
                logger.info(f"Playwright失败，降级使用requests [{source['name']}]")
                return self.crawl_with_requests(source)
        
        logger.warning(f"所有采集方式均失败 [{source['name']}]")
        return None
    
    def parse_content(self, content: str, source: Dict[str, Any]) -> list:
        raise NotImplementedError("子类必须实现parse_content方法")
