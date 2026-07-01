import re
from datetime import datetime
from typing import Dict, Any, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from utils.logger import logger
from utils.config_loader import config

class RegulatorCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.sources = config.get_crawler_config()["regulator"].get("sources", [])
        self.max_articles = config.get_crawler_config()["regulator"].get("max_articles_per_source", 20)
        self.max_days = 14
        self.expired_streak_limit = 5
    
    def _is_date_valid(self, date_str: str) -> bool:
        """检查日期是否在14天内"""
        if not date_str:
            return False
        
        date_patterns = [
            r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日号]?',
            r'(\d{4})-(\d{2})-(\d{2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    publish_date = datetime(year, month, day)
                    days_diff = (datetime.now() - publish_date).days
                    
                    if days_diff <= self.max_days:
                        return True
                    else:
                        logger.info(f"跳过过期资讯[{days_diff}天]: {date_str}")
                        return False
                except Exception:
                    continue
        
        return False
    
    def parse_content(self, content: str, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles = []
        
        try:
            soup = BeautifulSoup(content, "lxml")
            
            if source["name"] == "证监会":
                articles = self._parse_csrc(soup, source)
            elif "中国结算" in source["name"]:
                articles = self._parse_chinaclear(soup, source)
            elif source["name"] == "基金业协会":
                articles = self._parse_amac(soup, source)
            else:
                articles = self._parse_generic(soup, source)
            
            articles = articles[:self.max_articles]
            logger.info(f"从 [{source['name']}] 解析到 {len(articles)} 条有效资讯")
            
        except Exception as e:
            logger.error(f"解析内容失败 [{source['name']}]: {e}")
        
        return articles
    
    def _parse_csrc(self, soup: BeautifulSoup, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles = []
        expired_streak = 0
        
        try:
            date_spans = soup.find_all("span", class_="date")
            logger.info(f"证监会: 找到 {len(date_spans)} 个日期标签")
            
            for date_span in date_spans:
                try:
                    date_str = date_span.get_text(strip=True)
                    
                    if not self._is_date_valid(date_str):
                        expired_streak += 1
                        if expired_streak >= self.expired_streak_limit:
                            logger.info("证监会: 连续5条过期/无日期，停止解析")
                            break
                        continue
                    
                    parent_li = date_span.find_parent("li")
                    if not parent_li:
                        continue
                    
                    link = parent_li.find("a", href=True)
                    if not link:
                        continue
                    
                    title = link.get_text(strip=True)
                    url = link.get("href", "")
                    
                    if not title or len(title) < 8:
                        continue
                    
                    if url.endswith(".pdf"):
                        continue
                    
                    if "/content.shtml" not in url:
                        continue
                    
                    if url.startswith("//"):
                        url = "http:" + url
                    elif url.startswith("/"):
                        url = urljoin("http://www.csrc.gov.cn", url)
                    elif not url.startswith("http"):
                        url = urljoin("http://www.csrc.gov.cn", url)
                    
                    expired_streak = 0
                    
                    articles.append({
                        "title": title,
                        "url": url,
                        "source": source["name"],
                        "publish_date": date_str,
                        "content": "",
                        "category": "监管公告",
                    })
                    
                except Exception as e:
                    expired_streak += 1
                    if expired_streak >= self.expired_streak_limit:
                        break
                    continue
            
        except Exception as e:
            logger.error(f"解析证监会页面失败: {e}")
        
        return articles
    
    def _parse_chinaclear(self, soup: BeautifulSoup, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles = []
        expired_streak = 0
        
        try:
            date_spans = soup.find_all("span", class_="date")
            logger.info(f"中国结算: 找到 {len(date_spans)} 个日期标签")
            
            for date_span in date_spans:
                try:
                    date_str = date_span.get_text(strip=True)
                    
                    if not self._is_date_valid(date_str):
                        expired_streak += 1
                        if expired_streak >= self.expired_streak_limit:
                            logger.info("中国结算: 连续5条过期/无日期，停止解析")
                            break
                        continue
                    
                    parent_li = date_span.find_parent("li")
                    if not parent_li:
                        continue
                    
                    link = parent_li.find("a", href=True)
                    if not link:
                        continue
                    
                    title = link.get_text(strip=True)
                    url = link.get("href", "")
                    
                    if not title or len(title) < 6:
                        continue
                    
                    if url.endswith(".pdf"):
                        continue
                    
                    if not (".shtml" in url or ".html" in url):
                        continue
                    
                    if "/202" not in url and "/2026" not in url and "/2025" not in url:
                        continue
                    
                    if url.startswith("//"):
                        url = "http:" + url
                    elif url.startswith("/"):
                        url = urljoin("http://www.chinaclear.cn", url)
                    elif not url.startswith("http"):
                        url = urljoin("http://www.chinaclear.cn", url)
                    
                    expired_streak = 0
                    
                    articles.append({
                        "title": title,
                        "url": url,
                        "source": source["name"],
                        "publish_date": date_str,
                        "content": "",
                        "category": "业务通知",
                    })
                    
                except Exception as e:
                    expired_streak += 1
                    if expired_streak >= self.expired_streak_limit:
                        break
                    continue
            
        except Exception as e:
            logger.error(f"解析中国结算页面失败: {e}")
        
        return articles
    
    def _parse_amac(self, soup: BeautifulSoup, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles = []
        expired_streak = 0
        
        try:
            all_lis = soup.find_all("li")
            logger.info(f"基金业协会: 找到 {len(all_lis)} 个li元素")
            
            news_candidates = []
            for li in all_lis:
                link = li.find("a", href=True)
                if not link:
                    continue
                title = link.get_text(strip=True)
                url = link.get("href", "")
                if title and len(title) >= 10 and ".html" in url and "/202" in url:
                    if "/hydj/" not in url and "/党建" not in url and "/xxgcdd" not in url:
                        year_match = re.search(r'/(\d{4})\d{2}/', url)
                        date_suffix_match = re.search(r'(\d{2})-(\d{2})$', title)
                        if year_match and date_suffix_match:
                            year = int(year_match.group(1))
                            month = int(date_suffix_match.group(1))
                            day = int(date_suffix_match.group(2))
                            sort_key = (year, month, day)
                        else:
                            sort_key = (0, 0, 0)
                        news_candidates.append({
                            "title": title, 
                            "url": url, 
                            "sort_key": sort_key
                        })
            
            news_candidates.sort(key=lambda x: x["sort_key"], reverse=True)
            
            logger.info(f"基金业协会: 筛选出 {len(news_candidates)} 个新闻候选")
            
            for candidate in news_candidates:
                try:
                    title = candidate["title"]
                    url = candidate["url"]
                    
                    year_match = re.search(r'/(\d{4})\d{2}/', url)
                    date_suffix_match = re.search(r'(\d{2})-(\d{2})$', title)
                    
                    if year_match and date_suffix_match:
                        year = year_match.group(1)
                        month = date_suffix_match.group(1)
                        day = date_suffix_match.group(2)
                        date_str = f"{year}-{month}-{day}"
                    else:
                        date_str = ""
                    
                    if not self._is_date_valid(date_str):
                        expired_streak += 1
                        if expired_streak >= self.expired_streak_limit:
                            logger.info("基金业协会: 连续5条过期/无日期，停止解析")
                            break
                        continue
                    
                    clean_title = title[:-5].strip() if date_suffix_match else title
                    
                    if url.startswith("//"):
                        url = "https:" + url
                    elif url.startswith("/"):
                        url = urljoin("https://www.amac.org.cn", url)
                    elif not url.startswith("http"):
                        url = urljoin("https://www.amac.org.cn/xwfb/tzgg/", url)
                    
                    expired_streak = 0
                    
                    articles.append({
                        "title": clean_title,
                        "url": url,
                        "source": source["name"],
                        "publish_date": date_str,
                        "content": "",
                        "category": "通知公告",
                    })
                    
                except Exception as e:
                    expired_streak += 1
                    if expired_streak >= self.expired_streak_limit:
                        break
                    continue
            
        except Exception as e:
            logger.error(f"解析基金业协会页面失败: {e}")
        
        return articles
    
    def _parse_generic(self, soup: BeautifulSoup, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles = []
        expired_streak = 0
        
        try:
            items = soup.select("a[href]")
            
            for item in items:
                try:
                    title = item.get_text(strip=True)
                    url = item.get("href", "")
                    
                    if not url or not title or len(title) < 5:
                        expired_streak += 1
                        if expired_streak >= self.expired_streak_limit:
                            break
                        continue
                    
                    if not url.startswith("http"):
                        url = urljoin(source["url"], url)
                    
                    date_str = ""
                    parent_li = item.parent
                    if parent_li:
                        span = parent_li.find("span")
                        if span:
                            date_str = span.get_text(strip=True)
                    
                    if not self._is_date_valid(date_str):
                        expired_streak += 1
                        if expired_streak >= self.expired_streak_limit:
                            break
                        continue
                    
                    expired_streak = 0
                    
                    articles.append({
                        "title": title,
                        "url": url,
                        "source": source["name"],
                        "publish_date": date_str,
                        "content": "",
                        "category": "资讯",
                    })
                    
                except Exception as e:
                    expired_streak += 1
                    if expired_streak >= self.expired_streak_limit:
                        break
                    continue
            
        except Exception as e:
            logger.error(f"通用解析失败 [{source['name']}]: {e}")
        
        return articles
    
    def _extract_pdf_text(self, pdf_content: bytes) -> str:
        try:
            import pdfplumber
            with pdfplumber.open(pdf_content) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text[:3000]
        except Exception as e:
            logger.error(f"PDF提取失败: {e}")
            return ""
    
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
            else:
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, "lxml")
                
                content_divs = soup.select(".article-content, .content, .main-content, .detail-content, .text-content, .TRS_Editor, .article-body, .mainContent")
                
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
    
    def crawl_all(self, save_to_file=True, fetch_content=True) -> List[Dict[str, Any]]:
        all_articles = []
        empty_pages_count = {}
        
        for source in self.sources:
            if not source.get("enabled", True):
                continue
            
            try:
                logger.info(f"开始采集 [{source['name']}]")
                articles = self.crawl_source(source)
                
                if articles:
                    empty_pages_count[source["name"]] = 0
                    
                    if fetch_content:
                        for i, article in enumerate(articles):
                            articles[i] = self.fetch_article_content(article)
                    
                    all_articles.extend(articles)
                    logger.info(f"成功采集 [{source['name']}]: {len(articles)} 条")
                    
                    for i, article in enumerate(articles[:5]):
                        logger.info(f"  [{i+1}] {article.get('title', '')[:60]}...")
                        if article.get('content'):
                            logger.info(f"     正文前100字: {article['content'][:100]}...")
                
                else:
                    empty_pages_count[source["name"]] = empty_pages_count.get(source["name"], 0) + 1
                    logger.warning(f"未采集到 [{source['name']}] 的数据")
                    
                    if empty_pages_count[source["name"]] >= 2:
                        logger.info(f"[{source['name']}] 连续2页无有效数据，停止翻页")
                        continue
            
            except Exception as e:
                logger.error(f"采集 [{source['name']}] 异常: {e}")
                continue
        
        logger.info(f"监管资讯采集完成，共 {len(all_articles)} 条")
        
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            url = article.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        if len(unique_articles) < len(all_articles):
            logger.info(f"去重后剩余 {len(unique_articles)} 条")
        
        if save_to_file and unique_articles:
            from utils.data_saver import data_saver
            data_saver.save_raw_data(unique_articles, "regulator")
        
        return unique_articles

regulator_crawler = RegulatorCrawler()