set CFLAGS=-Wno-unused-but-set-variable
D:/pyview_demo/.venv/Scripts/python.exe -m nuitka --standalone --debug --assume-yes-for-downloads --output-filename=send_mail --windows-disable-console --windows-icon-from-ico=D:/descrpypython/main.ico --remove-output --no-pyi-file --assume-yes-for-downloads --output-dir=D:/pyview_demo/nuitka_output --include-module=http_send_mail --plugin-enable=pywebview D:/pyview_demo/http_send_mail_index.py
pause
