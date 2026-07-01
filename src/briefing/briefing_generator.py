import json
import os
from datetime import datetime
from typing import List, Dict, Any

from utils.logger import logger
from utils.data_saver import data_saver


class BriefingGenerator:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def _format_number(self, num: float) -> str:
        if abs(num) >= 100000000:
            return f"{num / 100000000:.2f}亿"
        elif abs(num) >= 10000:
            return f"{num / 10000:.2f}万"
        else:
            return f"{num:.2f}"
    
    def _generate_market_section(self, market_data: List[Dict[str, Any]]) -> str:
        from utils.deepseek_client import deepseek_client
        
        if not market_data:
            return """
        <section>
            <h2>📈 行情表现</h2>
            <p class="empty">暂无行情数据</p>
        </section>
        """
        
        stock_indices = [m for m in market_data if m.get("type") == "stock"]
        bond_indices = [m for m in market_data if m.get("type") == "bond"]
        
        market_date = market_data[0]["date"] if market_data else ""
        
        try:
            market_summary = deepseek_client.summarize_market(market_data)
        except Exception as e:
            logger.error(f"行情总结生成异常: {e}")
            market_summary = "行情数据已更新。"
        
        html = """
        <section>
            <h2>📈 行情表现</h2>
            <p class="market-summary">📊 """ + market_summary + """</p>
            <p class="market-date">数据日期：""" + market_date + """</p>
            <div class="market-grid">
        """
        
        html += """
                <div class="market-subsection">
                    <h3>股票指数</h3>
                    <table class="market-table">
                        <thead>
                            <tr><th>指数</th><th>收盘</th><th>涨跌额</th><th>涨跌幅</th></tr>
                        </thead>
                        <tbody>
        """
        
        for item in stock_indices:
            change_color = "red" if item["change_pct"] >= 0 else "green"
            change_pct = f"<span class='{change_color}'>{item['change_pct']:+.2f}%</span>"
            change = f"<span class='{change_color}'>{item['change']:+.2f}</span>"
            html += f"""
                            <tr>
                                <td>{item['name']}</td>
                                <td>{item['close']:.2f}</td>
                                <td>{change}</td>
                                <td>{change_pct}</td>
                            </tr>
            """
        
        html += """
                        </tbody>
                    </table>
                </div>
        """
        
        html += """
                <div class="market-subsection">
                    <h3>债券指数</h3>
                    <table class="market-table">
                        <thead>
                            <tr><th>指数</th><th>收盘</th><th>涨跌额</th><th>涨跌幅</th></tr>
                        </thead>
                        <tbody>
        """
        
        for item in bond_indices:
            change_color = "red" if item["change_pct"] >= 0 else "green"
            change_pct = f"<span class='{change_color}'>{item['change_pct']:+.2f}%</span>"
            change = f"<span class='{change_color}'>{item['change']:+.2f}</span>"
            html += f"""
                            <tr>
                                <td>{item['name']}</td>
                                <td>{item['close']:.2f}</td>
                                <td>{change}</td>
                                <td>{change_pct}</td>
                            </tr>
            """
        
        html += """
                        </tbody>
                    </table>
                </div>
        """
        
        html += """
            </div>
        </section>
        """
        
        return html
    
    def _generate_news_section(self, regulator_data: List[Dict[str, Any]], news_data: List[Dict[str, Any]]) -> str:
        def generate_articles(items):
            if not items:
                return '<p class="empty">暂无相关内容</p>'
            
            html = '<div class="article-list">'
            for item in items[:1]:
                date = item.get("publish_date", "")
                source = item.get("source", "")
                content = item.get("content", "")[:200]
                html += f"""
                    <article>
                        <h3><a href="{item['url']}" target="_blank">{item['title']}</a></h3>
                        <div class="meta">
                            <span class="source">{source}</span>
                            <span class="date">{date}</span>
                        </div>
                        <p class="summary">{content}...</p>
                    </article>
                """
            html += '</div>'
            return html
        
        html = """
        <section>
            <h2>📋 资讯速递</h2>
            <div class="news-grid">
                <div class="news-column">
                    <h3>📋 监管资讯</h3>
        """ + generate_articles(regulator_data) + """
                </div>
                <div class="news-column">
                    <h3>📰 新闻快讯</h3>
        """ + generate_articles(news_data) + """
                </div>
            </div>
        </section>
        """
        
        return html
    
    def generate(self, market_data: List[Dict[str, Any]], filtered_data: Dict[str, Any]) -> str:
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>基金TA每日简报 - {self.today}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        header p {{
            font-size: 14px;
            opacity: 0.8;
        }}
        
        main {{
            padding: 30px;
        }}
        
        section {{
            margin-bottom: 30px;
        }}
        
        section h2 {{
            font-size: 20px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .market-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        
        .market-summary {{
            font-size: 16px;
            color: #2d3748;
            padding: 15px 20px;
            background: linear-gradient(135deg, #f6f8fb 0%, #e9ecef 100%);
            border-radius: 8px;
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        
        .market-date {{
            font-size: 12px;
            color: #a0aec0;
            margin-bottom: 20px;
        }}
        
        .market-subsection h3 {{
            font-size: 16px;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 15px;
        }}
        
        .market-table {{
            width: 100%;
            border-collapse: collapse;
            background: #f8fafc;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .market-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-size: 13px;
            font-weight: 600;
        }}
        
        .market-table td {{
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }}
        
        .market-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .market-table tr:hover {{
            background: #f1f5f9;
        }}
        
        .red {{
            color: #e53e3e;
            font-weight: 600;
        }}
        
        .green {{
            color: #38a169;
            font-weight: 600;
        }}
        
        .article-list {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        article {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        article:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        article h3 {{
            font-size: 15px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 10px;
        }}
        
        article h3 a {{
            color: inherit;
            text-decoration: none;
        }}
        
        article h3 a:hover {{
            color: #667eea;
        }}
        
        .meta {{
            display: flex;
            gap: 15px;
            margin-bottom: 10px;
            font-size: 12px;
            color: #718096;
        }}
        
        .summary {{
            font-size: 13px;
            color: #4a5568;
            line-height: 1.6;
        }}
        
        .empty {{
            text-align: center;
            color: #a0aec0;
            padding: 30px;
            background: #f8fafc;
            border-radius: 8px;
        }}
        
        .news-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        
        .news-column {{
            background: #f8fafc;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #e2e8f0;
        }}
        
        .news-column h3 {{
            font-size: 16px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        footer {{
            background: #1a1a2e;
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 12px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>基金TA每日简报</h1>
            <p>{self.today} | 数据来源：证监会、中国结算、基金业协会、新华网、人民网、akshare</p>
        </header>
        <main>
        """
        
        html += self._generate_market_section(market_data)
        html += self._generate_news_section(
            filtered_data.get("regulator", []),
            filtered_data.get("news", [])
        )
        
        html += """
        </main>
        <footer>
            <p>本简报由基金TA资讯工具自动生成</p>
        </footer>
    </div>
</body>
</html>
        """
        
        return html
    
    def save(self, html: str, filename: str = None) -> str:
        if not filename:
            filename = f"{self.today}_briefing.html"
        
        report_dir = os.path.join("data", "reports")
        os.makedirs(report_dir, exist_ok=True)
        
        file_path = os.path.join(report_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        logger.info(f"简报已保存: {file_path}")
        
        return file_path


briefing_generator = BriefingGenerator()