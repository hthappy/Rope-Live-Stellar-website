import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import logging

class EmailSender:
    def __init__(self):
        # QQ邮箱配置
        self.smtp_server = "smtp.qq.com"
        self.smtp_port = 587  # QQ邮箱的SSL端口
        self.sender_email = "your_qq_email@qq.com"  # 发件人邮箱
        self.password = "your_smtp_password"  # QQ邮箱的SMTP授权码（不是QQ密码）
        
    def send_activation_email(self, to_email, activation_code, plan_info):
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = Header(f"AI换脸直播 <{self.sender_email}>")
            msg['To'] = Header(to_email)
            msg['Subject'] = Header("您的软件激活码", 'utf-8')
            
            # 邮件正文
            body = f"""
            <html>
            <body>
                <div style="padding: 20px; font-family: Arial, sans-serif;">
                    <h2 style="color: #333;">感谢您购买我们的软件！</h2>
                    
                    <p>您的订阅信息如下：</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>订阅计划：</strong>{plan_info['duration']}</p>
                        <p><strong>激活码：</strong><span style="color: #e74c3c; font-size: 16px;">{activation_code}</span></p>
                    </div>
                    
                    <p>使用说明：</p>
                    <ol>
                        <li>打开软件</li>
                        <li>点击"已有激活码"按钮</li>
                        <li>输入上方的激活码</li>
                        <li>点击"激活"按钮完成激活</li>
                    </ol>
                    
                    <p style="color: #666; margin-top: 30px;">
                        如有任何问题，请联系客服：<br>
                        QQ：123456789<br>
                        微信：your_wechat<br>
                        邮箱：support@example.com
                    </p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999;">
                        <p>此邮件由系统自动发送，请勿直接回复。</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # 启用TLS加密
                server.login(self.sender_email, self.password)
                server.send_message(msg)
                
            logging.info(f"Activation email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send activation email: {str(e)}")
            return False
    
    def send_test_email(self):
        """测试邮件发送功能"""
        try:
            test_email = "test@example.com"
            test_plan = {"duration": "测试计划"}
            test_code = "TEST-CODE-123"
            
            return self.send_activation_email(test_email, test_code, test_plan)
            
        except Exception as e:
            logging.error(f"Email test failed: {str(e)}")
            return False

# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试邮件发送
    email_sender = EmailSender()
    
    # 发送测试邮件
    if email_sender.send_test_email():
        print("测试邮件发送成功！")
    else:
        print("测试邮件发送失败！")
