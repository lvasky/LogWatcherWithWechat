# -*- coding: utf-8 -*-

import pyautogui
import pyperclip
import time
import tkinter as tk
from tkinter import Toplevel, Label
from tkinter.font import Font
import threading
from collections import deque
import tkinter.filedialog as filedialog
from threading import Event

# Global stop event for thread synchronization
stop_event = Event()

# Function to alert the user with a GUI
def alert_user():
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()  # Use withdraw instead of iconify for better compatibility

    msg_window = Toplevel(root)
    msg_window.title("提醒")
    msg_window.attributes("-topmost", True)

    custom_font = Font(family="Helvetica", size=12, weight="bold")
    Label(msg_window, text="\n!!! 5s后开始发送微信消息!!!\n  如果不需要,请关闭Windows命令窗口 \n", font=custom_font).pack()
    
    root.after(6000, root.destroy)
    root.mainloop()

# Function to send a message
def send(msg):
    pyperclip.copy(msg)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')

# Thread function to wait for user input
def check_input():
    input("按任意键停止倒计时")
    stop_event.set()

def app_hotkey(app_type):
    if app_type == "wechat":
        pyautogui.hotkey('ctrl', 'alt', 'w')
        pyautogui.hotkey('ctrl', 'f')
    elif app_type == "wechat_work":
        pyautogui.hotkey('shift', 'alt', 's')
        pyautogui.hotkey('ctrl', 'f')
    else:
        pyautogui.hotkey('ctrl', 'alt', 'w')
        pyautogui.hotkey('ctrl', 'f')
    
# Function to send messages to a friend
def send_msg(friend, contents , app_type="wechat"):
    print("弹窗提醒用户")
    input_thread = threading.Thread(target=check_input)
    input_thread.start()
    alert_user()

    for i in range(5):
        if stop_event.is_set():
            print("程序终止")
            return
        print(5 - i)
        time.sleep(1)

    print("开始发送微信消息")
    app_hotkey(app_type)
    pyperclip.copy(friend)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')

    for msg in contents:
        send(msg)
        time.sleep(0.1)

# Function to check the last lines of a log file
def check_last_lines_of_log(log_file_path, contents, check_strs, n=10):
    with open(log_file_path, 'r', encoding='utf-8') as file:
        last_lines = deque(file, maxlen=n)

    for line in last_lines:
        for check_str in check_strs:
            if check_str in line:
                contents.append("".join(last_lines))
                contents.append("任务完成")
                return True, last_lines
    return False, last_lines

# Function to continuously check a log file
def continuously_check_log(log_file_path, contents, check_strs, interval=5, n=20):
    pre_last_lines = None
    cnt = 0
    while not stop_event.is_set():
        found, last_lines = check_last_lines_of_log(log_file_path, contents, check_strs, n)
        if last_lines == pre_last_lines:
            cnt += 1
        else:
            cnt = 0
        if cnt > 5:
            contents.append("".join(last_lines))
            contents.append("任务失败")
            break
        pre_last_lines = last_lines
        if found:
            break
        time.sleep(interval)

# Function to select a file
def select_file():
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()

    file_path = filedialog.askopenfilename()
    root.destroy()
    return file_path

# Function to prompt user input
def say_hello(check_dic , apptype_dic):
    check_strs = []
    print("-------------------------------------------------------------")
    print("$             hello , welcome to use this program !      ")
    print("$ 这个程序帮助您在检测fpga软件中的log文件,在编译完成后用微信提醒您.")
    print("-------------------------------------------------------------")
    print("$ 默认采用以下检测关键词:")
    for key, value in check_dic.items():
        print("* " + key + " : " + value)
        check_strs.append(value)
    print("-------------------------------------------------------------")
    if input("$ 是否需要修改关键词？(y/n)") == "y":
        check_strs = []
        while True:
            value = input("$ 请输入检测关键词(输入q退出):")
            if value in ["q", ""]:
                break
            check_strs.append(value)
    
    print("$ 以下为要生效的关键词:")
    for check_str in check_strs:
        print("* " + check_str)
    print("-------------------------------------------------------------")
    print("* 请确保你的微信电脑版已经登录了.")
    print("* 请确保你的fpga软件已经开始运行了.")
    print("-------------------------------------------------------------")

    friend_name = input("$ 请输入微信好友，想把消息发给谁，如果不输入，默认为'文件传输助手':")
    if not friend_name:
        friend_name = "文件传输助手"
    print("The friend's name is: " + friend_name)
    print("-------------------------------------------------------------")
    print("$ 请选择要使用的软件:")
    for key, value in apptype_dic.items():
        print("* " + key + " : " + value)
    key_input = input("$ 请选择要使用的软件:")
    # if key_input == "":
    #     key_input = "0"
    if key_input not in set(apptype_dic.keys()):
        key_input = "0"
        
    print(apptype_dic[key_input])
    print("-------------------------------------------------------------")
    return friend_name, check_strs, apptype_dic[key_input]

# Main function
if __name__ == '__main__':
    contents = []
    default_check_dic = {"安路软件关键词": "Generate bits file", "vivado软件关键词": "Generate bitstream successfully"}
    default_apptype_dic = {"0": "wechat", "1": "wechat_work"}
    friend_name, check_strs, app_type = say_hello(default_check_dic, default_apptype_dic)
    log_file_path = select_file()
    continuously_check_log_thread = threading.Thread(target=continuously_check_log, args=(log_file_path, contents, check_strs, 1, 20))
    continuously_check_log_thread.start()
    continuously_check_log_thread.join()  # Wait for log checking thread to complete
    send_msg(friend_name, contents, app_type)
