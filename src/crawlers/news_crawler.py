import re
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from utils.logger import logger
from utils.config_loader import config
from utils.data_saver import data_saver

class NewsCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.sources = config.get_crawler_config()["news"].get("sources", [])
        self.max_articles = config.get_crawler_config()["news"].get("max_articles_per_source", 30)
    
    def parse_content(self, content: str, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles = []
        
        try:
            soup = BeautifulSoup(content, "lxml")
            
            if "新华网" in source["name"]:
                articles = self._parse_xinhua(soup, source)
            elif "人民网" in source["name"]:
                articles = self._parse_people(soup, source)
            else:
                articles = self._parse_general(soup, source)
            
            articles = articles[:self.max_articles]
            
        except Exception as e:
            logger.error(f"解析新闻页面失败 [{source['name']}]: {e}")
        
        return articles
    
    def _parse_xinhua(self, soup: BeautifulSoup, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles = []
        
        try:
            items = soup.find_all("a", href=True)
            
            for item in items:
                try:
                    title = item.get_text(strip=True)
                    url = item.get("href", "")
                    
                    if not url or not title or len(title) < 8:
                        continue
                    
                    if url.endswith(".pdf"):
                        continue
                    
                    if "/fortune/" not in url.lower():
                        continue
                    
                    date_match = re.search(r'/fortune/(\d{8})/', url, re.IGNORECASE)
                    if not date_match:
                        continue
                    
                    date_str = f"{date_match.group(1)[:4]}-{date_match.group(1)[4:6]}-{date_match.group(1)[6:]}"
                    
                    if url.startswith("//"):
                        url = "https:" + url
                    elif url.startswith("/"):
                        url = urljoin("http://www.xinhuanet.com", url)
                    elif not url.startswith("http"):
                        url = urljoin(source["url"], url)
                    
                    articles.append({
                        "title": title,
                        "url": url,
                        "source": source["name"],
                        "publish_date": date_str,
                        "content": "",
                        "category": "新闻快讯",
                    })
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            logger.error(f"解析新华网页面失败: {e}")
        
        return articles
    
    def _parse_people(self, soup: BeautifulSoup, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles = []
        
        try:
            items = soup.select(".list a, .news-list a, .content a, .article-list a, .list-item a, .focus a")
            
            for item in items:
                try:
                    title = item.get_text(strip=True)
                    url = item.get("href", "")
                    
                    if not url or not title or len(title) < 8:
                        continue
                    
                    if url.endswith(".pdf"):
                        continue
                    
                    if url.startswith("//"):
                        url = "http:" + url
                    elif url.startswith("/"):
                        url = urljoin("http://finance.people.com.cn", url)
                    elif not url.startswith("http"):
                        url = urljoin(source["url"], url)
                    
                    date_str = ""
                    parent_li = item.parent
                    if parent_li:
                        span = parent_li.find("span", class_="time") or parent_li.find("span")
                        if span:
                            date_str = span.get_text(strip=True)
                    
                    articles.append({
                        "title": title,
                        "url": url,
                        "source": source["name"],
                        "publish_date": date_str,
                        "content": "",
                        "category": "新闻快讯",
                    })
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            logger.error(f"解析人民网页面失败: {e}")
        
        return articles
    
    def _parse_general(self, soup: BeautifulSoup, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles = []
        
        try:
            items = soup.find_all("a", href=True)
            
            for item in items:
                try:
                    title = item.get_text(strip=True)
                    url = item.get("href", "")
                    
                    if not url or not title or len(title) < 8:
                        continue
                    
                    if url.endswith(".pdf"):
                        continue
                    
                    if not any(ext in url.lower() for ext in [".html", ".htm", ".shtml"]):
                        continue
                    
                    if url.startswith("//"):
                        url = "http:" + url
                    elif url.startswith("/"):
                        url = urljoin(source["url"], url)
                    elif not url.startswith("http"):
                        url = urljoin(source["url"], url)
                    
                    date_str = ""
                    parent_li = item.parent
                    if parent_li:
                        span = parent_li.find("span")
                        if span:
                            date_str = span.get_text(strip=True)
                    
                    articles.append({
                        "title": title,
                        "url": url,
                        "source": source["name"],
                        "publish_date": date_str,
                        "content": "",
                        "category": "新闻快讯",
                    })
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            logger.error(f"解析通用新闻页面失败: {e}")
        
        return articles
    
    def fetch_article_content(self, article: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"获取详情页内容: {article['url']}")
            
            if article["url"].endswith(".pdf"):
                logger.info("跳过PDF文件")
                return article
            
            response = self.request_with_retry(article["url"])
            if not response:
                return article
            
            content_type = response.headers.get("Content-Type", "")
            
            if "application/pdf" in content_type:
                logger.info("跳过PDF文件")
                return article
            
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, "lxml")
            
            content_divs = soup.select(
                ".article-content, .content, .main-content, .detail-content, .text-content, "
                ".TRS_Editor, .article-body, .mainContent, .articleText, .left_zw, .art_box"
            )
            
            if content_divs:
                content = content_divs[0].get_text(strip=True)
            else:
                content = soup.get_text(strip=True)[:3000]
            
            article["content"] = content[:3000]
            
            date_patterns = [
                r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日号]?',
                r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            ]
            
            if not article.get("publish_date"):
                for pattern in date_patterns:
                    match = re.search(pattern, article["content"])
                    if match:
                        article["publish_date"] = f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
                        break
            
            logger.info(f"获取成功，正文长度: {len(article['content'])}字")
            
        except Exception as e:
            logger.error(f"获取详情页失败 [{article['title']}]: {e}")
        
        return article
    
    def crawl_all(self, save_to_file: bool = True, fetch_content: bool = False) -> List[Dict[str, Any]]:
        all_articles = []
        
        logger.info("开始采集新闻快讯")
        
        for source in self.sources:
            articles = self.crawl_source(source)
            
            if articles:
                logger.info(f"成功采集 [{source['name']}]: {len(articles)} 条")
                
                for i, article in enumerate(articles[:5]):
                    logger.info(f"  [{i+1}] {article['title'][:50]}")
                
                all_articles.extend(articles)
        
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            url = article.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        if len(unique_articles) < len(all_articles):
            logger.info(f"去重后剩余 {len(unique_articles)} 条")
        
        if fetch_content:
            for article in unique_articles:
                self.fetch_article_content(article)
        
        logger.info(f"新闻快讯采集完成，共 {len(unique_articles)} 条")
        
        if save_to_file and unique_articles:
            data_saver.save_raw_data(unique_articles, "news")
        
        return unique_articles

news_crawler = NewsCrawler()