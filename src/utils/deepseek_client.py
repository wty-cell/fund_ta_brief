import json
import time
import requests
from typing import Optional, Dict, Any

from .logger import logger
from .config_loader import config

class DeepSeekClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.get_summarizer_config()["llm"]["api_key"]
        self.base_url = base_url or config.get_summarizer_config()["llm"]["base_url"]
        self.model = model or config.get_summarizer_config()["llm"]["model"]
        self.max_chars = config.get_summarizer_config()["max_chars"]
        self.timeout = 30
        self.retry_times = 3
        self.retry_delay = 2
    
    def _build_url(self) -> str:
        return f"{self.base_url}/chat/completions"
    
    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _build_payload(self, content: str) -> Dict[str, Any]:
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": f"你是一个专业的金融资讯摘要助手。请将以下内容压缩成不超过{self.max_chars}个汉字的简洁摘要，保留核心信息和关键数据，语言通顺专业。"
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            "temperature": 0.3,
            "max_tokens": 100,
        }
    
    def generate_summary(self, content: str, max_chars: Optional[int] = None) -> str:
        if not content or not content.strip():
            logger.warning("内容为空，跳过摘要生成")
            return ""
        
        if not self.api_key:
            logger.error("DeepSeek API Key未配置")
            return content[:max_chars or self.max_chars]
        
        chars_limit = max_chars or self.max_chars
        
        logger.info(f"开始生成摘要，原文长度: {len(content)}字")
        logger.info(f"原文前150字: {content[:150]}...")
        
        for attempt in range(self.retry_times):
            try:
                url = self._build_url()
                headers = self._build_headers()
                payload = self._build_payload(content)
                
                response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
                response.raise_for_status()
                
                result = response.json()
                summary = result["choices"][0]["message"]["content"].strip()
                
                if len(summary) > chars_limit:
                    summary = summary[:chars_limit]
                
                logger.info(f"摘要生成成功，长度: {len(summary)}字")
                logger.info(f"摘要内容: {summary}")
                return summary
            
            except requests.exceptions.RequestException as e:
                logger.error(f"DeepSeek API调用失败 (第{attempt+1}/{self.retry_times}次): {e}")
                
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.warning("API调用失败，使用本地截取作为备用")
                    fallback = content[:chars_limit]
                    logger.info(f"备用摘要: {fallback}")
                    return fallback
            
            except Exception as e:
                logger.error(f"摘要生成异常: {e}")
                fallback = content[:chars_limit]
                logger.info(f"备用摘要: {fallback}")
                return fallback
    
    def batch_generate(self, contents: list, max_chars: Optional[int] = None) -> list:
        results = []
        
        for i, content in enumerate(contents):
            logger.info(f"正在处理第 {i+1}/{len(contents)} 条内容")
            
            try:
                summary = self.generate_summary(content, max_chars)
                results.append(summary)
            except Exception as e:
                logger.error(f"处理第 {i+1} 条内容失败: {e}")
                results.append(content[:max_chars or self.max_chars])
            
            time.sleep(1)
        
        return results
    
    def summarize_market(self, market_data: list) -> str:
        """使用API生成行情智能总结"""
        if not market_data:
            logger.warning("行情数据为空，跳过总结生成")
            return "今日行情数据暂无。"
        
        if not self.api_key:
            logger.warning("DeepSeek API Key未配置，使用本地规则生成行情总结")
            return self._fallback_market_summary(market_data)
        
        # 构造行情数据文本
        data_text = ""
        for item in market_data:
            change_symbol = "涨" if item["change_pct"] >= 0 else "跌"
            data_text += f"{item['name']}：收盘{item['close']:.2f}点，{change_symbol}{abs(item['change_pct']):.2f}%\n"
        
        prompt = f"请用一句话（50字以内）总结以下股市债市行情，给出简明判断，不要列出具体数据：\n\n{data_text}\n\n总结："
        
        logger.info(f"开始生成行情总结，数据: {len(market_data)}个指数")
        
        try:
            url = self._build_url()
            headers = self._build_headers()
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 100,
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            summary = result["choices"][0]["message"]["content"].strip()
            
            # 限制50字以内
            if len(summary) > 50:
                summary = summary[:50]
            
            logger.info(f"行情总结生成成功: {summary}")
            return summary
        
        except Exception as e:
            logger.error(f"行情总结生成失败: {e}")
            return self._fallback_market_summary(market_data)
    
    def _fallback_market_summary(self, market_data: list) -> str:
        """本地规则生成行情总结（API失败时的降级方案）"""
        stock_indices = [m for m in market_data if m.get("type") == "stock"]
        
        if not stock_indices:
            return "今日行情数据暂无。"
        
        avg_change = sum(m["change_pct"] for m in stock_indices) / len(stock_indices)
        
        if avg_change >= 1:
            return "📈 今日股市整体走强，市场情绪积极。"
        elif avg_change >= 0:
            return "📊 今日股市小幅震荡，整体平稳。"
        elif avg_change >= -1:
            return "📉 今日股市小幅调整，观望情绪较浓。"
        else:
            return "💥 今日股市大幅下跌，市场承压明显。"


deepseek_client = DeepSeekClient()
