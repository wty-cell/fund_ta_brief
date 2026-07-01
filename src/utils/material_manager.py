import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MaterialManager:
    def __init__(self):
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "cache")
        self.pool_file = os.path.join(self.cache_dir, "candidate_pool.json")
        self.sent_file = os.path.join(self.cache_dir, "sent_history.json")
        self.max_pool_days = 30
        
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _load_json(self, file_path: str) -> Dict:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载文件失败 {file_path}: {e}")
        return {}
    
    def _save_json(self, file_path: str, data: Dict):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_pool(self) -> Dict[str, Dict[str, Any]]:
        return self._load_json(self.pool_file)
    
    def save_pool(self, pool: Dict[str, Dict[str, Any]]):
        self._save_json(self.pool_file, pool)
    
    def load_sent_history(self) -> Dict[str, List[str]]:
        data = self._load_json(self.sent_file)
        return data.get("regulator", []), data.get("news", [])
    
    def save_sent_history(self, regulator_sent: List[str], news_sent: List[str]):
        data = {
            "regulator": regulator_sent,
            "news": news_sent,
            "updated_at": datetime.now().isoformat()
        }
        self._save_json(self.sent_file, data)
    
    def cleanup_expired(self):
        pool = self.load_pool()
        expired_threshold = datetime.now() - timedelta(days=self.max_pool_days)
        
        for category in ["regulator", "news"]:
            if category not in pool:
                continue
            
            expired_count = 0
            remaining = {}
            
            for url, article in pool[category].items():
                publish_date_str = article.get("publish_date", "")
                if publish_date_str:
                    try:
                        publish_date = datetime.strptime(publish_date_str, "%Y-%m-%d")
                        if publish_date >= expired_threshold:
                            remaining[url] = article
                        else:
                            expired_count += 1
                    except Exception:
                        remaining[url] = article
                else:
                    remaining[url] = article
            
            pool[category] = remaining
            
            if expired_count > 0:
                logger.info(f"清理过期素材 [{category}]: 移除 {expired_count} 条")
        
        self.save_pool(pool)
    
    def update_pool(self, new_articles: List[Dict[str, Any]], category: str):
        pool = self.load_pool()
        
        if category not in pool:
            pool[category] = {}
        
        added_count = 0
        updated_count = 0
        
        for article in new_articles:
            url = article.get("url", "")
            if not url:
                continue
            
            if url not in pool[category]:
                pool[category][url] = article
                added_count += 1
            else:
                existing = pool[category][url]
                existing_content = existing.get("content", "")
                new_content = article.get("content", "")
                
                if len(new_content) > len(existing_content):
                    pool[category][url] = article
                    updated_count += 1
        
        self.save_pool(pool)
        
        if added_count > 0 or updated_count > 0:
            logger.info(f"更新候选池 [{category}]: 新增 {added_count} 条，更新 {updated_count} 条，总计 {len(pool[category])} 条")
    
    def get_candidates(self, category: str) -> List[Dict[str, Any]]:
        pool = self.load_pool()
        if category not in pool:
            return []
        return list(pool[category].values())
    
    def mark_sent(self, urls: List[str], category: str):
        regulator_sent, news_sent = self.load_sent_history()
        
        if category == "regulator":
            for url in urls:
                if url not in regulator_sent:
                    regulator_sent.append(url)
        elif category == "news":
            for url in urls:
                if url not in news_sent:
                    news_sent.append(url)
        
        self.save_sent_history(regulator_sent, news_sent)
        logger.info(f"标记已发送 [{category}]: {len(urls)} 条")
    
    def is_sent(self, url: str, category: str) -> bool:
        regulator_sent, news_sent = self.load_sent_history()
        
        if category == "regulator":
            return url in regulator_sent
        elif category == "news":
            return url in news_sent
        
        return False
    
    def get_pool_stats(self) -> Dict[str, Any]:
        pool = self.load_pool()
        regulator_sent, news_sent = self.load_sent_history()
        
        stats = {}
        
        for category in ["regulator", "news"]:
            total = len(pool.get(category, {}))
            sent_count = len(regulator_sent) if category == "regulator" else len(news_sent)
            
            dates = []
            for article in pool.get(category, {}).values():
                date_str = article.get("publish_date", "")
                if date_str:
                    dates.append(date_str)
            
            earliest_date = min(dates) if dates else "N/A"
            latest_date = max(dates) if dates else "N/A"
            
            stats[category] = {
                "total": total,
                "sent_count": sent_count,
                "earliest_date": earliest_date,
                "latest_date": latest_date
            }
        
        return stats
    
    def clear_pool(self, category: Optional[str] = None):
        pool = self.load_pool()
        
        if category:
            if category in pool:
                count = len(pool[category])
                pool[category] = {}
                self.save_pool(pool)
                logger.info(f"清空候选池 [{category}]: 移除 {count} 条")
                return f"已清空 [{category}] 候选池，共 {count} 条"
            else:
                return f"类别 [{category}] 不存在"
        else:
            regulator_count = len(pool.get("regulator", {}))
            news_count = len(pool.get("news", {}))
            pool = {}
            self.save_pool(pool)
            logger.info(f"清空全部候选池: 监管资讯 {regulator_count} 条，新闻快讯 {news_count} 条")
            return f"已清空全部候选池，监管资讯 {regulator_count} 条，新闻快讯 {news_count} 条"
    
    def clear_sent_history(self, category: Optional[str] = None):
        regulator_sent, news_sent = self.load_sent_history()
        
        if category == "regulator":
            count = len(regulator_sent)
            regulator_sent = []
        elif category == "news":
            count = len(news_sent)
            news_sent = []
        else:
            count_reg = len(regulator_sent)
            count_news = len(news_sent)
            regulator_sent = []
            news_sent = []
            self.save_sent_history(regulator_sent, news_sent)
            logger.info(f"清空全部已发送记录: 监管资讯 {count_reg} 条，新闻快讯 {count_news} 条")
            return f"已清空全部已发送记录，监管资讯 {count_reg} 条，新闻快讯 {count_news} 条"
        
        self.save_sent_history(regulator_sent, news_sent)
        logger.info(f"清空已发送记录 [{category}]: {count} 条")
        return f"已清空 [{category}] 已发送记录，共 {count} 条"