import os
import smtplib
import markdown2
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Dict

from config import Config


class Notifier:
    """
    用户名/帐户： 你的QQ邮箱完整的地址
    密码： 生成的授权码
    电子邮件地址： 你的QQ邮箱的完整邮件地址
    接收邮件服务器： imap.qq.com，使用SSL，端口号993
    发送邮件服务器： smtp.qq.com，使用SSL，端口号465或587
    """

    def __init__(self, settings: Dict):
        # 第三方 SMTP 服务
        self.mail_host = settings.get('mail_host')  # 设置服务器
        self.mail_user = settings.get('mail_user')   # 用户名
        self.mail_port = settings.get('mail_port')   # 用户名
        self.mail_pass = os.getenv("QQ_MAIL_TOKEN")  # 口令

        self.receivers = ["17343100344@163.com"]

    def notify(self, subject, report) -> str:
        # Implement notification logic, e.g., send email or Slack message
        self.send_email(subject, report)
        return "ok"

    def send_email(self, subject, content):
        """
        :param subject: 邮件标题
        :param content: 内容
        :return: 结果
        """
        ret = True
        try:
            html_report = markdown2.markdown(content)

            msg = MIMEText(html_report, 'plain', 'utf-8')
            msg['From'] = formataddr(("damoon30", self.mail_user))  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(("客户1", self.receivers[0]))  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = subject  # 邮件的主题，也可以说是标题

            server = smtplib.SMTP_SSL(self.mail_host, self.mail_port)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login(self.mail_user, self.mail_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.mail_user, self.receivers, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
        except Exception as exp:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            print({exp})
            ret = False

        print(f"----{ret}--")
        return ret


if __name__ == "__main__":
    config = Config()
    notifier = Notifier(settings=config.notification_settings)
    notifier.notify("测试邮件----辅导费地方")
