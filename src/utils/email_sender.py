import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import List

from utils.logger import logger
from utils.config_loader import config


class EmailSender:
    def __init__(self):
        self.email_config = config.get_email_config()
        self.sender_address = self.email_config.get("sender", {}).get("address", "")
        self.smtp_server = self.email_config.get("sender", {}).get("smtp_server", "")
        self.smtp_port = self.email_config.get("sender", {}).get("smtp_port", 465)
        self.use_ssl = self.email_config.get("sender", {}).get("use_ssl", True)
        self.subject_prefix = self.email_config.get("subject_prefix", "【基金TA每日简报】")
        self.test_mode = self.email_config.get("test_mode", False)
        self.recipients = self.email_config.get("recipients", [])
        
        self.password = config.get_email_password()
    
    def _is_config_valid(self) -> bool:
        if not self.sender_address:
            logger.error("邮件配置不完整：发件人地址为空")
            return False
        if not self.smtp_server:
            logger.error("邮件配置不完整：SMTP服务器为空")
            return False
        if not self.password:
            logger.error("邮件配置不完整：发件人密码为空")
            return False
        return True
    
    def _get_recipients(self) -> List[str]:
        if self.test_mode:
            logger.info("测试模式：仅发送给发件人")
            return [self.sender_address]
        return self.recipients
    
    def _build_message(self, html_content: str, subject: str) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        
        msg["Subject"] = subject
        msg["From"] = formataddr(("基金TA每日简报", self.sender_address))
        msg["To"] = ", ".join(self._get_recipients())
        
        plain_text = "请使用支持HTML的邮件客户端查看此邮件内容。\n\n简报内容已以HTML格式发送。"
        
        part1 = MIMEText(plain_text, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")
        
        msg.attach(part1)
        msg.attach(part2)
        
        return msg
    
    def send_briefing_email(self, html_content: str) -> bool:
        if not self.email_config.get("enabled", True):
            logger.info("邮件发送功能已禁用")
            return True
        
        if not self._is_config_valid():
            logger.error("邮件配置无效，跳过发送")
            return False
        
        recipients = self._get_recipients()
        if not recipients:
            logger.error("收件人列表为空")
            return False
        
        subject = f"{self.subject_prefix}{time.strftime('%Y-%m-%d')}"
        
        try:
            msg = self._build_message(html_content, subject)
            
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            server.login(self.sender_address, self.password)
            
            success_count = 0
            fail_count = 0
            
            for recipient in recipients:
                try:
                    server.sendmail(self.sender_address, recipient, msg.as_string())
                    logger.info(f"邮件发送成功: {recipient}")
                    success_count += 1
                except Exception as e:
                    logger.error(f"邮件发送失败 [{recipient}]: {e}")
                    fail_count += 1
                
                time.sleep(1)
            
            server.quit()
            
            logger.info(f"邮件发送完成: 成功 {success_count} 封，失败 {fail_count} 封")
            
            return fail_count == 0
        
        except Exception as e:
            logger.error(f"邮件发送异常: {e}")
            return False


email_sender = EmailSender()