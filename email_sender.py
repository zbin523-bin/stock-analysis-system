#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件发送器
用于发送股票分析报告邮件
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from datetime import datetime

class EmailSender:
    def __init__(self):
        # 邮件配置 - 请替换为实际配置
        self.smtp_server = "smtp.163.com"
        self.smtp_port = 465
        self.sender_email = "your_email@163.com"  # 发件人邮箱
        self.sender_password = "your_password"    # 邮箱密码或授权码
        self.recipient_email = "zhangbin19850523@163.com"
    
    def send_stock_report(self, report_content, attachment_path=None):
        """发送股票分析报告邮件"""
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"📊 股票投资组合分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # 添加邮件正文
            msg.attach(MIMEText(report_content, 'plain', 'utf-8'))
            
            # 添加附件
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    part = MIMEApplication(f.read())
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{os.path.basename(attachment_path)}"'
                    )
                    msg.attach(part)
            
            # 发送邮件
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ 邮件已成功发送至 {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False
    
    def configure_email(self, sender_email=None, sender_password=None, recipient_email=None):
        """配置邮件信息"""
        if sender_email:
            self.sender_email = sender_email
        if sender_password:
            self.sender_password = sender_password
        if recipient_email:
            self.recipient_email = recipient_email
    
    def test_connection(self):
        """测试邮件连接"""
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
            print("✅ 邮件连接测试成功")
            return True
        except Exception as e:
            print(f"❌ 邮件连接测试失败: {e}")
            return False

def main():
    """主函数"""
    print("📧 股票分析报告邮件发送器")
    print("=" * 50)
    
    # 创建邮件发送器
    email_sender = EmailSender()
    
    # 获取邮件配置
    print("请配置邮件信息：")
    sender_email = input("发件人邮箱 (例: your_email@163.com): ").strip()
    sender_password = input("邮箱密码/授权码: ").strip()
    
    if sender_email and sender_password:
        email_sender.configure_email(sender_email=sender_email, sender_password=sender_password)
        
        # 测试连接
        print("\n正在测试邮件连接...")
        if email_sender.test_connection():
            print("✅ 邮件配置正确")
            
            # 读取报告内容
            report_path = "/Volumes/Work/SynologyDrive/claude/output/hk_stock_report_20250912_153135.txt"
            if os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                
                # 添加邮件开头
                email_content = f"""
尊敬的用户：

您好！您的股票投资组合分析报告已生成，请查收。

报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{report_content}

如有任何问题，请随时联系我们。

祝您投资顺利！

此致
敬礼

股票分析系统
{datetime.now().strftime('%Y-%m-%d')}
"""
                
                # 发送邮件
                print("\n正在发送邮件...")
                if email_sender.send_stock_report(email_content, report_path):
                    print("✅ 报告已成功发送到您的邮箱！")
                else:
                    print("❌ 邮件发送失败，请检查配置。")
            else:
                print(f"❌ 报告文件不存在：{report_path}")
        else:
            print("❌ 邮件配置错误，请检查邮箱和密码。")
    else:
        print("❌ 邮件配置不完整，发送取消。")

if __name__ == "__main__":
    main()