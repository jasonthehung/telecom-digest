"""
電信產業自動摘要系統 - Email 發送模組
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email 設定"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""
    use_tls: bool = True


@dataclass
class EmailResult:
    """Email 發送結果"""
    success: bool
    message: str = ""
    recipients: List[str] = None

    def __post_init__(self):
        if self.recipients is None:
            self.recipients = []


class EmailSender:
    """Email 發送器"""

    def __init__(self, config: EmailConfig):
        """
        初始化 Email 發送器

        Args:
            config: Email 設定
        """
        self.config = config
        logger.info(f"Initialized EmailSender with SMTP: {config.smtp_server}:{config.smtp_port}")

    def send(
        self,
        to: str,
        subject: str,
        html_content: str,
        cc: Optional[List[str]] = None,
        plain_text: Optional[str] = None,
    ) -> EmailResult:
        """
        發送 HTML 郵件

        Args:
            to: 收件人 email
            subject: 郵件主旨
            html_content: HTML 內容
            cc: 副本收件人列表
            plain_text: 純文字內容（備用）

        Returns:
            EmailResult: 發送結果
        """
        try:
            # 建立郵件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.sender_email
            msg['To'] = to
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = ', '.join(cc)

            # 加入純文字版本（作為備用）
            if plain_text:
                part1 = MIMEText(plain_text, 'plain', 'utf-8')
                msg.attach(part1)

            # 加入 HTML 版本
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)

            # 收件人列表
            recipients = [to]
            if cc:
                recipients.extend(cc)

            # 連接 SMTP 伺服器並發送
            logger.info(f"Connecting to SMTP server: {self.config.smtp_server}")

            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()

                logger.info("Logging in to SMTP server...")
                server.login(self.config.sender_email, self.config.sender_password)

                logger.info(f"Sending email to: {recipients}")
                server.sendmail(self.config.sender_email, recipients, msg.as_string())

            logger.info(f"Email sent successfully to {len(recipients)} recipient(s)")

            return EmailResult(
                success=True,
                message="Email sent successfully",
                recipients=recipients,
            )

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed: {e}"
            logger.error(error_msg)
            return EmailResult(success=False, message=error_msg)

        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {e}"
            logger.error(error_msg)
            return EmailResult(success=False, message=error_msg)

        except Exception as e:
            error_msg = f"Failed to send email: {e}"
            logger.error(error_msg)
            return EmailResult(success=False, message=error_msg)

    def send_to_multiple(
        self,
        to_list: List[str],
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None,
    ) -> List[EmailResult]:
        """
        發送郵件給多個收件人（個別發送）

        Args:
            to_list: 收件人 email 列表
            subject: 郵件主旨
            html_content: HTML 內容
            plain_text: 純文字內容（備用）

        Returns:
            List[EmailResult]: 各個發送結果
        """
        results = []

        for to in to_list:
            result = self.send(to, subject, html_content, plain_text=plain_text)
            results.append(result)

        success_count = sum(1 for r in results if r.success)
        logger.info(f"Sent {success_count}/{len(to_list)} emails successfully")

        return results


def create_email_sender(gmail_user: str, gmail_app_password: str) -> EmailSender:
    """
    建立 Gmail Email 發送器

    Args:
        gmail_user: Gmail 帳號
        gmail_app_password: Gmail 應用程式密碼

    Returns:
        EmailSender: Email 發送器實例
    """
    config = EmailConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email=gmail_user,
        sender_password=gmail_app_password,
        use_tls=True,
    )

    return EmailSender(config)


if __name__ == "__main__":
    # 測試用
    import os
    from dotenv import load_dotenv

    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    recipient = os.getenv("RECIPIENT_EMAIL")

    if not all([gmail_user, gmail_password, recipient]):
        print("Error: Missing environment variables")
        print("Required: GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL")
        exit(1)

    sender = create_email_sender(gmail_user, gmail_password)

    # 測試發送
    test_html = """
    <html>
    <body>
        <h1>測試郵件</h1>
        <p>這是一封測試郵件，用於驗證電信產業自動摘要系統的 Email 功能。</p>
        <p>時間：{}</p>
    </body>
    </html>
    """.format(os.popen("date").read().strip())

    result = sender.send(
        to=recipient,
        subject="📡 電信日報系統測試",
        html_content=test_html,
        plain_text="這是一封測試郵件。",
    )

    if result.success:
        print(f"✅ Email sent successfully to: {result.recipients}")
    else:
        print(f"❌ Failed to send email: {result.message}")
