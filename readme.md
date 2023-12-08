# LogWatcherWithWechat

## 功能介绍

- 支持vivado软件/安路fpga软件的log，当检测到bit文件生成时结束，并微信提醒
- 支持自定义检测关键词
- 支持wechat，wechat business
- 支持发送给不同的好友
- 支持超时时间和轮询间隔时间自定义

## 软件使用流程图

![image-20231208134319973](doc/image-20231208134319973.png)

## 软件界面

![image-20231208134337116](doc/image-20231208134337116.png)

## 开发人员使用指南

```python
pipenv shell #创建pipenv环境
pipenv install -r requirements.txt #还原本工程pipenv环境
pipenv list #查询库是否安装成功
python LogWatcherWithWechat.py #运行程序 
pipenv run pyinstaller --onefile --ico=.\doc\LogWatcherWithWechat.ico docLogWatcherWithWechat.py
```

