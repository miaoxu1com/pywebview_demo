import os
import sys

import webview

from http_send_mail import send_mail_all


def get_data_file_path(filename):
    if getattr(sys, 'frozen', False):
        # 运行在打包后的可执行文件中
        base_path = sys._MEIPASS
    else:
        # 运行在源代码中
        base_path = os.path.abspath(".")

    return os.path.join(base_path, filename)


class API:
    email_url = ""

    def send_email(self, send_email_url):
        self.email_url = send_email_url
        send_mail_all(self.email_url)
        return 'true'

    def open_email(self):
        pass
        # session = login_email(receiver=self.email_url)
        # session_cookie = session.cookies.get_dict()
        # cookies_str = '; '.join([f'{k}={v}' for k, v in cookies.items()])
        # print(cookies_str)
        # window.evaluate_js("window.location.href = 'https://p88528v.hulk.bjzdd.qihoo.net/mail/';")

        # for cookie in session.cookies:
        #     cookie_strings = []
        #     cookie_string = f"{cookie.name}={cookie.value}; domain={cookie.domain}; path={cookie.path}; secure;"
        #     if cookie.has_nonstandard_attr('HttpOnly'):
        #         cookie_string += ' HttpOnly;'
        #     cookie_strings.append(cookie_string)
        #     cooks = '; '.join(cookie_strings)
        #     print(cooks)
        #     window.evaluate_js(f"document.cookie='{cooks}';")

        # window.evaluate_js("window.location.href = 'https://p88528v.hulk.bjzdd.qihoo.net/mail/';")
        # return cooks


def main():
    api = API()
    window = webview.create_window('邮箱发送', 'static/index.html', width=800, height=350, resizable=False,
                                   js_api=api)
    webview.start(private_mode=False, http_server=True, http_port=13377)


main()
