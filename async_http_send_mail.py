import asyncio
import json
import re
import time
import tomllib
import warnings

import aiohttp

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


async def login_email(_sender=None, queue=None):
    print(symbol_co * "#")
    # 这里不使用with  as session：是因为后面还需要使用不能在这里自动关闭session，否则在sendmail中无法使用
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    # 这里不使用async with   as： 形式是因为当时怕影响sessio的cookie
    response = await session.get(
        email_url,
        headers=headers
    )
    pattern = r'<input\s+type="hidden"\s+name="_token"\s+value="([^"]+)"\s*>'
    html_content = await response.text()
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
        '_user': _sender,
        '_pass': config.get('config').get('email_pass'),
    }
    response = await session.post(
        email_url,
        params=params,
        headers=headers,
        data=data,
        allow_redirects=False
    )
    # 异步登陆不能自动存储响应头的cookie只能手动更新，花了很长时间才定位到
    cookie_dict = {name: cookie.value for name, cookie in response.cookies.items()}
    session.cookie_jar.update_cookies(cookie_dict)
    await queue.put(session)


async def send_mail(receiver_url=None, queue=None, event=None):
    while not event.is_set():
        try:
            session = await queue.get()
            if session is None:
                event.set()
                break
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
            response = await session.get(
                email_url,
                params=params,
                headers=headers
            )

            response_json = await response.text()
            email_info = json.loads(response_json, strict=False)['exec'].encode('utf8').decode('unicode-escape')
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
            response = await session.get(
                email_url,
                params=params,
                headers=headers,
                allow_redirects=False)
            _id = response.headers.get('Location').split("=")[-1]
            _to = receiver_url or ','.join(_to_list)
            print(f"接收者邮箱:{_to}")

            params = {
                '_task': 'mail',
                '_action': 'compose',
                '_id': f'{_id}',
            }
            async with session.get(
                    email_url,
                    params=params,
                    headers=headers
            ) as response:
                pattern = r'<input\s+type="hidden"\s+name="_token"\s+value="([^"]+)"\s*>'
                html_content = await response.text()
                match = re.search(pattern, html_content)
                if match:
                    # 提取 value 属性的值
                    _token = match.group(1)
                    print(f"发送邮箱_token Value: {_token}")
                else:
                    print("No match found")

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
            params = {
                '_task': 'mail',
                '_unlock': f'loading{time_p}',
                '_framed': '1',
                '_lang': 'en',
            }
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
            async with session.post(
                    email_url,
                    params=params,
                    headers=headers,
                    data=data
            ) as response:
                print(symbol_co * "*")
            await session.close()
        except Exception as e:
            print(f"发送邮件时出现错误: {e}")
        finally:
            queue.task_done()


async def send_mail_all(re_url=None):
    queue = asyncio.Queue()
    event = asyncio.Event()
    producer_tasks = [login_email(em, queue) for em in _sender]
    # 并发执行所有任务
    await asyncio.gather(*producer_tasks)
    await queue.put(None)
    consumer_tasks = [send_mail(re_url, queue, event) for _ in _sender]
    print(f"创建的发送邮件任务数量: {len(consumer_tasks)}")
    await asyncio.gather(*consumer_tasks)
    await queue.join()


# 运行主函数


if __name__ == '__main__':
    asyncio.run(send_mail_all("CREDITff4b7db561@qifudigitech.com"))
