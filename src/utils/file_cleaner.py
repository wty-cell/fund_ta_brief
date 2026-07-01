import os
import time
from datetime import datetime, timedelta
from typing import Optional

from .logger import logger

class FileCleaner:
    def __init__(self, data_dir="data", logs_dir="logs"):
        self.data_dir = data_dir
        self.logs_dir = logs_dir
    
    def clean_old_files(self, directory: str, retention_days: int) -> int:
        deleted_count = 0
        
        if not os.path.exists(directory):
            logger.debug(f"目录不存在: {directory}")
            return deleted_count
        
        now = time.time()
        cutoff_time = now - (retention_days * 24 * 60 * 60)
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                
                try:
                    file_mtime = os.path.getmtime(file_path)
                    
                    if file_mtime < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"删除旧文件: {file_path}")
                except Exception as e:
                    logger.error(f"删除文件失败 {file_path}: {e}")
            
            for dirname in dirs:
                dir_path = os.path.join(root, dirname)
                
                try:
                    dir_mtime = os.path.getmtime(dir_path)
                    
                    if dir_mtime < cutoff_time:
                        if not os.listdir(dir_path):
                            os.rmdir(dir_path)
                            logger.info(f"删除空目录: {dir_path}")
                except Exception as e:
                    logger.error(f"删除目录失败 {dir_path}: {e}")
        
        return deleted_count
    
    def clean_data(self, retention_days: Optional[int] = None) -> int:
        if retention_days is None:
            from .config_loader import config
            retention_days = config.get_data_config()["retention_days"]
        
        logger.info(f"开始清理数据目录，保留最近 {retention_days} 天的数据")
        deleted = self.clean_old_files(self.data_dir, retention_days)
        logger.info(f"数据目录清理完成，共删除 {deleted} 个文件")
        
        return deleted
    
    def clean_logs(self, retention_days: Optional[int] = None) -> int:
        if retention_days is None:
            from .config_loader import config
            retention_days = config.get_data_config()["logs_retention_days"]
        
        logger.info(f"开始清理日志目录，保留最近 {retention_days} 天的日志")
        deleted = self.clean_old_files(self.logs_dir, retention_days)
        logger.info(f"日志目录清理完成，共删除 {deleted} 个文件")
        
        return deleted
    
    def clean_all(self) -> dict:
        results = {}
        results["data"] = self.clean_data()
        results["logs"] = self.clean_logs()
        
        return results

file_cleaner = FileCleaner()
