import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from utils.logger import logger
from utils.config_loader import config
from utils.data_saver import data_saver

class MarketCrawler:
    def __init__(self):
        self.config = config.get_crawler_config()["market"]
        self.stock_indices = self.config.get("stock_indices", [])
        self.bond_indices = self.config.get("bond_indices", [])
        self.use_akshare = self.config.get("use_akshare", True)
        self.request_interval = config.get_crawler_config().get("request_interval", 3)
        self.last_request_time = 0
    
    def wait_interval(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self.last_request_time = time.time()
    
    def get_index_data(self, index_info: Dict[str, Any], index_type: str) -> Optional[Dict[str, Any]]:
        try:
            self.wait_interval()
            code = index_info.get("akshare_code", index_info.get("code", ""))
            logger.info(f"获取{index_type}指数: {index_info['name']} ({code})")
            
            import akshare as ak
            df = ak.stock_zh_index_daily(symbol=code)
            
            if df.empty:
                logger.warning(f"未获取到 {index_info['name']} 的数据")
                return None
            
            latest = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else latest
            
            change = float(latest["close"]) - float(previous["close"])
            change_pct = (change / float(previous["close"])) * 100
            
            return {
                "name": index_info["name"],
                "code": code,
                "type": index_type,
                "date": str(latest["date"]),
                "open": round(float(latest["open"]), 2),
                "close": round(float(latest["close"]), 2),
                "high": round(float(latest["high"]), 2),
                "low": round(float(latest["low"]), 2),
                "volume": int(latest["volume"]),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "source": "akshare",
            }
        
        except Exception as e:
            logger.error(f"获取{index_type}指数失败 [{index_info['name']}]: {e}")
            return None
    
    def get_stock_index_data(self, index_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.get_index_data(index_info, "stock")
    
    def get_bond_index_data(self, index_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.get_index_data(index_info, "bond")
    
    def crawl_all(self, save_to_file: bool = True) -> List[Dict[str, Any]]:
        all_data = []
        logger.info("开始采集行情数据")
        
        if not self.use_akshare:
            logger.warning("akshare未启用，跳过行情采集")
            return all_data
        
        for index_info in self.stock_indices:
            data = self.get_stock_index_data(index_info)
            if data:
                all_data.append(data)
        
        for index_info in self.bond_indices:
            data = self.get_bond_index_data(index_info)
            if data:
                all_data.append(data)
        
        logger.info(f"行情数据采集完成，共 {len(all_data)} 条")
        
        if save_to_file and all_data:
            data_saver.save_raw_data(all_data, "market")
        
        return all_data

market_crawler = MarketCrawler()