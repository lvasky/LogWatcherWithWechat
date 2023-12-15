# LogWatcherWithWechat

## 功能介绍

- 支持vivado软件/安路fpga软件的log，当检测到bit文件生成时结束，并微信提醒
- 支持ini文件或命令行提示词来输入参数
  - 支持自定义检测关键词
  - 支持wechat，wechat business
  - 支持发送给不同的好友
  - 支持超时时间和轮询间隔时间自定义


# "info.ini"文件格式
> 文件编码gb2312
```ini
[info]
logapp = 0	
apptype = 0 
friend = 任务传输助手
timeout = 6
```

## 软件使用流程图


![image-LogWatcherWithWechat流程图](doc/LogWatcherWithWechat流程图.png)

## 软件界面

![image-app_screenshot](doc/app_screenshot.png)

## 开发人员使用指南

```python
pipenv shell #创建pipenv环境
pipenv install -r requirements.txt #还原本工程pipenv环境
pipenv list #查询库是否安装成功
python LogWatcherWithWechat.py #运行程序 
pipenv run pyinstaller --onefile --ico=.\doc\LogWatcherWithWechat.ico  LogWatcherWithWechat.py #打包成exe
```

