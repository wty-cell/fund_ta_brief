import re
from typing import List, Dict, Any, Optional

from utils.logger import logger
from utils.config_loader import config
from utils.data_saver import data_saver
from utils.material_manager import MaterialManager

material_manager = MaterialManager()


class DataFilter:
    def __init__(self):
        self.filter_config = config.get_filter_config()
        
        self.regulator_keywords = self.filter_config.get("regulator_keywords", [])
        self.regulator_exclude_keywords = self.filter_config.get("regulator_exclude_keywords", [])
        self.news_include_keywords = self.filter_config.get("news_include_keywords", [])
        self.news_exclude_keywords = self.filter_config.get("news_exclude_keywords", [])
        
        self.min_content_length = 100
        self.min_title_length = 8
        
        self.navigation_titles = [
            "English", "首页", "关于我们", "联系我们", "网站地图",
            "证监会要闻", "新闻发布会", "辖区监管动态", "学习贯彻",
        ]
    
    def is_navigation_link(self, title: str) -> bool:
        if not title:
            return True
        title_lower = title.lower().strip()
        for nav in self.navigation_titles:
            if nav.lower() in title_lower:
                return True
        return len(title) <= 3
    
    def contains_any_keyword(self, text: str, keywords: List[str]) -> bool:
        if not text or not keywords:
            return False
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return True
        return False
    
    def matches_keywords(self, text: str, include_keywords: List[str], exclude_keywords: List[str] = None) -> bool:
        if exclude_keywords and self.contains_any_keyword(text, exclude_keywords):
            return False
        
        if not include_keywords:
            return True
        
        return self.contains_any_keyword(text, include_keywords)
    
    def filter_regulator_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered = []
        
        for article in articles:
            try:
                url = article.get("url", "")
                
                if material_manager.is_sent(url, "regulator"):
                    continue
                
                title = article.get("title", "")
                content = article.get("content", "")
                
                if self.is_navigation_link(title):
                    continue
                
                if len(title) < self.min_title_length:
                    continue
                
                if len(content) < self.min_content_length:
                    continue
                
                combined_text = f"{title} {content}"
                
                if self.contains_any_keyword(combined_text, self.regulator_exclude_keywords):
                    continue
                
                article["filter_score"] = self.calculate_score(combined_text, self.regulator_keywords)
                filtered.append(article)
                
            except Exception as e:
                logger.error(f"过滤监管资讯失败 [{article.get('title', '')}]: {e}")
        
        filtered.sort(key=lambda x: x.get("filter_score", 0), reverse=True)
        
        filtered = filtered[:1]
        
        logger.info(f"监管资讯过滤完成: {len(articles)} -> {len(filtered)} 条")
        
        return filtered
    
    def filter_news_flash(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered = []
        
        for article in articles:
            try:
                url = article.get("url", "")
                
                if material_manager.is_sent(url, "news"):
                    continue
                
                title = article.get("title", "")
                content = article.get("content", "")
                
                if len(title) < self.min_title_length:
                    continue
                
                if len(content) < self.min_content_length:
                    continue
                
                combined_text = f"{title} {content}"
                
                if self.matches_keywords(combined_text, self.news_include_keywords, self.news_exclude_keywords):
                    article["filter_score"] = self.calculate_score(combined_text, self.news_include_keywords)
                    filtered.append(article)
                
            except Exception as e:
                logger.error(f"过滤新闻快讯失败 [{article.get('title', '')}]: {e}")
        
        filtered.sort(key=lambda x: x.get("filter_score", 0), reverse=True)
        
        filtered = filtered[:1]
        
        logger.info(f"新闻快讯过滤完成: {len(articles)} -> {len(filtered)} 条")
        
        return filtered
    
    def calculate_score(self, text: str, keywords: List[str]) -> int:
        score = 0
        text_lower = text.lower()
        for keyword in keywords:
            keyword_lower = keyword.lower()
            score += text_lower.count(keyword_lower)
        return score
    
    def filter_all(self, regulator_data: List[Dict[str, Any]], news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info("开始数据过滤")
        
        filtered_regulator = self.filter_regulator_news(regulator_data)
        filtered_news = self.filter_news_flash(news_data)
        
        result = {
            "regulator": filtered_regulator,
            "news": filtered_news,
        }
        
        logger.info(f"数据过滤完成，监管资讯 {len(filtered_regulator)} 条，新闻快讯 {len(filtered_news)} 条")
        
        data_saver.save_processed_data(result, "filtered")
        
        return result


data_filter = DataFilter()