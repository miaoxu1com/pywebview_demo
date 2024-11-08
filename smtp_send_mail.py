import mimetypes
import os
import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def read_recipients_from_file(file_path):
    """从指定文件中读取收件人列表"""
    with open(file_path, 'r') as file:
        recipients = file.read().splitlines()
    return recipients


def send_email(sender, password, recipient, subject, text_body, html_body, attachment_path,
               smtp_server='p88528v.hulk.bjzdd.qihoo.net', smtp_port=25):
    """发送带 multipart/alternative 正文和附件的电子邮件"""

    # 创建MIMEMultipart对象
    msg = MIMEMultipart('mixed')
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    # 创建multipart/alternative部分
    alternative = MIMEMultipart('alternative')
    msg.attach(alternative)

    # 添加纯文本正文
    part1 = MIMEText(text_body, 'plain', 'utf-8')
    alternative.attach(part1)

    # 添加HTML正文
    part2 = MIMEText(html_body, 'html', 'utf-8')
    alternative.attach(part2)

    # 添加附件
    if os.path.exists(attachment_path):
        with open(attachment_path, "rb") as attachment:
            ctype, encoding = mimetypes.guess_type(attachment_path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'

            maintype, subtype = ctype.split('/', 1) if ctype else ('application', 'octet-stream')

            part = MIMEBase(maintype, subtype)
            part.set_payload(attachment.read())
            encoders.encode_base64(part)

            # 使用Header来编码文件名，并指定utf-8和Quoted-Printable编码
            encoded_filename = Header(os.path.basename(attachment_path), 'utf-8').encode('utf-8')
            part.add_header('Content-Disposition', f'attachment; filename="{encoded_filename}"')

            # 将附件附加到消息中
            msg.attach(part)

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        # 登录SMTP服务器
        server.login(sender, password)
        # 发送邮件
        server.send_message(msg)
        server.quit()
        print(f'邮件已成功发送至: {recipient}')



def main():
    # 发送者的邮箱和密码
    sender = 'CREDIT454ec43994@qifudigitech.com'
    recipient = 'CREDIT454ec43994@qifudigitech.com'
    password = '{9N3aC2AZs'

    # 读取收件人列表
    # recipients = read_recipients_from_file('recipients.txt')

    # 邮件主题
    subject = '测试邮件'

    # 纯文本正文
    text_body = '这是测试邮件的纯文本内容。'

    # HTML正文
    html_body = """
    <html>
      <head></head>
      <body>
        <p>这是测试邮件的HTML内容。</p>
      </body>
    </html>
    """

    # 附件路径
    attachment_path = '1.zip'


    send_email(sender, password, recipient, subject, text_body, html_body, attachment_path)
    # 向所有收件人发送邮件
    # for recipient in recipients:
    #     send_email(sender, password, recipient, subject, text_body, html_body, attachment_path)


if __name__ == '__main__':
    main()
