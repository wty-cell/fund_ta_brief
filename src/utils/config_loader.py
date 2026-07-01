import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self.yaml_config: Dict[str, Any] = {}
        self.env_config: Dict[str, str] = {}
    
    def load(self):
        self._load_env()
        self._load_yaml()
        self._merge_configs()
    
    def _load_env(self):
        env_path = os.path.join(self.config_dir, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
        self.env_config = {
            "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", ""),
            "EMAIL_ADDRESS": os.getenv("EMAIL_ADDRESS", ""),
            "EMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD", ""),
            "SMTP_SERVER": os.getenv("SMTP_SERVER", ""),
            "SMTP_PORT": int(os.getenv("SMTP_PORT", "465")),
        }
    
    def _load_yaml(self):
        yaml_path = os.path.join(self.config_dir, "config.yaml")
        if os.path.exists(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                self.yaml_config = yaml.safe_load(f)
    
    def _merge_configs(self):
        if "email" in self.yaml_config and "sender" in self.yaml_config["email"]:
            if not self.yaml_config["email"]["sender"]["address"]:
                self.yaml_config["email"]["sender"]["address"] = self.env_config.get("EMAIL_ADDRESS", "")
            if not self.yaml_config["email"]["sender"]["smtp_server"]:
                self.yaml_config["email"]["sender"]["smtp_server"] = self.env_config.get("SMTP_SERVER", "")
            if "smtp_port" not in self.yaml_config["email"]["sender"] or not self.yaml_config["email"]["sender"]["smtp_port"]:
                self.yaml_config["email"]["sender"]["smtp_port"] = self.env_config.get("SMTP_PORT", 465)
    
    def get(self, key: str, default=None):
        keys = key.split(".")
        value = self.yaml_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_env(self, key: str, default=None):
        return self.env_config.get(key, default)
    
    def get_email_config(self):
        return {
            "enabled": self.get("email.enabled", True),
            "subject_prefix": self.get("email.subject_prefix", "【基金TA每日简报】"),
            "test_mode": self.get("email.test_mode", False),
            "sender": {
                "type": self.get("email.sender.type", "smtp"),
                "address": self.get("email.sender.address", ""),
                "smtp_server": self.get("email.sender.smtp_server", ""),
                "smtp_port": self.get("email.sender.smtp_port", 465),
                "use_ssl": self.get("email.sender.use_ssl", True),
                "password": self.env_config.get("EMAIL_PASSWORD", ""),
            },
            "recipients": self.get("email.recipients", []),
        }
    
    def get_crawler_config(self):
        return {
            "request_interval": self.get("crawler.request_interval", 3),
            "timeout": self.get("crawler.timeout", 30),
            "retry_times": self.get("crawler.retry_times", 3),
            "headless": self.get("crawler.headless", True),
            "regulator": self.get("crawler.regulator", {}),
            "market": self.get("crawler.market", {}),
            "news": self.get("crawler.news", {}),
        }
    
    def get_filter_config(self):
        return {
            "regulator_keywords": self.get("filter.regulator_keywords", []),
            "regulator_exclude_keywords": self.get("filter.regulator_exclude_keywords", []),
            "news_include_keywords": self.get("filter.news_flash_include_keywords", []),
            "news_exclude_keywords": self.get("filter.news_flash_exclude_keywords", []),
        }
    
    def get_summarizer_config(self):
        return {
            "max_chars": self.get("summarizer.max_chars", 150),
            "method": self.get("summarizer.method", "rule"),
            "llm": {
                "provider": self.get("summarizer.llm.provider", "deepseek"),
                "model": self.get("summarizer.llm.model", "deepseek-chat"),
                "base_url": self.get("summarizer.llm.base_url", "https://api.deepseek.com"),
                "api_key": self.env_config.get("DEEPSEEK_API_KEY", ""),
            },
        }
    
    def get_data_config(self):
        return {
            "retention_days": self.get("data.retention_days", 7),
            "logs_retention_days": self.get("data.logs_retention_days", 30),
        }
    
    def get_email_password(self):
        return self.env_config.get("EMAIL_PASSWORD", "")

config = ConfigLoader()
config.load()
