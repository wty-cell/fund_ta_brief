import os
import json
from datetime import datetime
from typing import Dict, Any, List

from .logger import logger

class DataSaver:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def ensure_dir(self, sub_dir: str):
        dir_path = os.path.join(self.data_dir, sub_dir)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path
    
    def save_raw_data(self, data: List[Dict[str, Any]], data_type: str):
        raw_dir = self.ensure_dir(f"raw/{self.today}")
        file_path = os.path.join(raw_dir, f"{data_type}.json")
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"原始数据已保存: {file_path} ({len(data)}条)")
            return file_path
        
        except Exception as e:
            logger.error(f"保存原始数据失败 {file_path}: {e}")
            return None
    
    def save_processed_data(self, data: List[Dict[str, Any]], data_type: str):
        processed_dir = self.ensure_dir("processed")
        file_path = os.path.join(processed_dir, f"{self.today}_{data_type}.json")
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"处理后数据已保存: {file_path} ({len(data)}条)")
            return file_path
        
        except Exception as e:
            logger.error(f"保存处理后数据失败 {file_path}: {e}")
            return None
    
    def save_report(self, content: str, report_type: str = "daily"):
        reports_dir = self.ensure_dir("reports")
        file_path = os.path.join(reports_dir, f"{self.today}_{report_type}_report.html")
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"简报已保存: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"保存简报失败 {file_path}: {e}")
            return None
    
    def load_raw_data(self, data_type: str, date: str = None) -> List[Dict[str, Any]]:
        date = date or self.today
        file_path = os.path.join(self.data_dir, "raw", date, f"{data_type}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载原始数据失败 {file_path}: {e}")
        
        return []

data_saver = DataSaver()
