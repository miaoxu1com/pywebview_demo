import re
import time
import tomllib
import warnings

import requests

warnings.filterwarnings("ignore")


def get_config(file_path="http_send_mail.toml"):
    with open(file_path, mode="rb") as fp:
        config = tomllib.load(fp)
    return config


config = get_config()
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
}
email_url = config.get('config').get('email_url')
_sender = config.get('config').get('_sender')
_to_list = config.get('config').get('_to')
symbol_co = 40


def login_email(receiver=None, _sender=None):
    print(symbol_co * "#")
    if receiver is not None:
        print(f"邮箱接收者登陆:{receiver}")

    session = requests.Session()
    response = session.get(email_url, headers=headers, verify=False)
    pattern = r'<input\s+type="hidden"\s+name="_token"\s+value="([^"]+)"\s*>'
    html_content = response.text
    match = re.search(pattern, html_content)
    if match:
        # 提取 value 属性的值
        token_value = match.group(1)
        print(f"登陆Token Value: {token_value}")
    else:
        print("No match found")

    params = {
        '_task': 'login',
    }

    data = {
        '_token': f'{token_value}',
        '_task': 'login',
        '_action': 'login',
        '_timezone': 'Asia/Shanghai',
        '_url': '',
        '_user': receiver or _sender,
        '_pass': config.get('config').get('email_pass'),
    }

    session.post(
        email_url,
        params=params,
        headers=headers,
        data=data,
        verify=False,
    )
    return session


def send_mail(session, receiver_url=None):
    time_p = int(time.time() * 1000)
    params = {
        '_task': 'mail',
        '_action': 'list',
        '_refresh': '1',
        '_layout': 'widescreen',
        '_mbox': 'INBOX',
        '_remote': '1',
        '_unlock': f'loading{time_p}',
        '_': f'{time_p}',
    }

    response = session.get(email_url, params=params, headers=headers, verify=False)

    email_info = response.json()['exec'].encode('utf8').decode('unicode-escape')
    pattern = r'this\.add_message_row\((\d+),{"subject":(.*?),(.*?),false\);'
    matches = re.findall(pattern, email_info, re.DOTALL)
    for match in matches:
        if match:

            email_id, subject, _ = match
            print(f"邮箱id{email_id},邮箱主题{subject}")
        else:
            print("No match found")

        params = {
            '_task': 'mail',
            '_forward_uid': int(email_id),
            '_mbox': 'INBOX',
            '_action': 'compose',
        }
        response = session.get(email_url, params=params, headers=headers, verify=False,
                               allow_redirects=False)
        _id = response.headers["Location"].split("=")[-1]
        _to = receiver_url or ','.join(_to_list)
        print(f"接收者邮箱:{_to}")

        params = {
            '_task': 'mail',
            '_action': 'compose',
            '_id': f'{_id}',
        }

        response = session.get(email_url, params=params, headers=headers, verify=False)
        pattern = r'<input\s+type="hidden"\s+name="_token"\s+value="([^"]+)"\s*>'
        html_content = response.text
        match = re.search(pattern, html_content)
        if match:
            # 提取 value 属性的值
            _token = match.group(1)
            print(f"发送邮箱_token Value: {_token}")
        else:
            print("No match found")

        params = {
            '_task': 'mail',
            '_unlock': f'loading{time_p}',
            '_framed': '1',
            '_lang': 'en',
        }
        pattern = r'<li\s+id="([^"]+)"'
        matches = re.findall(pattern, html_content)
        if matches:
            pass
            # 打印所有匹配的 id 值
            # for match in matches:
            #     print(f"附件ID: {match}")
        else:
            print("No match found")

        attachment_id = matches[0].split("rcmfile")[1]

        # 正则表达式模式
        pattern = r'"(\d+)"\s*:\s*\{.*?"email"\s*:\s*"([^"]+)"'

        matches = re.findall(pattern, html_content, re.DOTALL)

        if matches:
            # 打印所有匹配的键和 email 值
            for key, email in matches:
                print(f"发送者id: {key}, 发送者Email: {email}")
                identity = key
        else:
            print("No match found")

        # 正则表达式模式
        pattern = r'<textarea\s+name="_message"\s+id="composebody".*?>(.*?)</textarea>'

        # 使用 re.search 查找匹配
        match = re.search(pattern, html_content, re.DOTALL)

        if match:
            # 提取 textarea 标签的内容
            message_content = match.group(1)
            # print(f"邮箱正文Message Content: {message_content}")
        else:
            print("No match found")

        data = {
            '_token': f'{_token}',
            '_task': 'mail',
            '_action': 'send',
            '_id': f'{_id}',
            '_attachments': f'{attachment_id}',
            '_from': f'{identity}',
            '_to': _to,
            '_cc': '',
            '_bcc': '',
            '_replyto': '',
            '_followupto': '',
            '_subject': f'{subject}',
            '_draft_saveid': '',
            '_draft': '',
            '_is_html': '0',
            '_framed': '1',
            '_message': f'{message_content}',
            'editorSelector': 'plain',
            '_mdn': '',
            '_dsn': '',
            '_priority': '0',
            '_store_target': 'Sent',
        }
        response = session.post(
            email_url,
            params=params,
            headers=headers,
            data=data,
            verify=False,
        )
        print(symbol_co * "*")


def send_mail_all(re_url=None):
    for em in _sender:
        _session = login_email(_sender=em)
        send_mail(session=_session, receiver_url=re_url)


if __name__ == '__main__':
    for em in _sender:
        _session = login_email(_sender=em)
        send_mail(session=_session)
        break
