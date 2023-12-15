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

from enum import Enum, auto

class LogAppType(Enum):
    OTHER = 0  # 0
    VIVADO = 1  # 1

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
    Label(msg_window, text="\n!!! 5s后开始发送微信消息!!!\n  如果不需要,请关闭Windows命令窗口 \n", font=custom_font, fg="red").pack()
    
    root.after(4000, root.destroy)
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
    print("发送完成")

# Function to check the last lines of a log file
def check_last_lines_of_log(log_file_path, contents, check_strs, n=10):
    with open(log_file_path, 'r', encoding='utf-8') as file:
        last_lines = deque(file, maxlen=n)

    for line in last_lines:
        for check_str in check_strs:
            if check_str in line:
                contents.append("".join(last_lines))
                contents.append("任务完成")
                print("$ 检测到关键词: " + check_str)
                return True, last_lines
    return False, last_lines

# Function to continuously check a log file
def continuously_check_log(logApp_type, log_file_path, contents, check_strs, interval=20, timeout_cnt=12, n=20):
    print("$ 如果log文件" + str(timeout_cnt * interval) + "s没有更新,则判定结束;\n持续侦测中...")
    pre_last_lines = None
    cnt = 0
    synthesis_end_flag = False
    found = False

    while not stop_event.is_set():
        # vivado软件需要检测synth和impl两个log文件
        if logApp_type == LogAppType.VIVADO :
            if not synthesis_end_flag:
                synthesis_end_flag, last_lines = check_last_lines_of_log(log_file_path + "/synth_1/runme.log", contents, ["synth_design completed successfully"])
            elif synthesis_end_flag and not found:
                found, last_lines = check_last_lines_of_log(log_file_path + "/impl_1/runme.log", contents, ["Bitgen Completed Successfully"])
        # 其他软件只需要检测一个log文件
        else:
            found, last_lines = check_last_lines_of_log(log_file_path, contents, check_strs, n)
        
        if last_lines == pre_last_lines:
            cnt += 1
        else:
            cnt = 0

        if cnt > timeout_cnt:
            contents.append("".join(last_lines))
            contents.append("任务失败")
            print("$ 检测到log文件" + str(timeout_cnt * interval) + "s没有更新,判定任务失败...")
            break

        pre_last_lines = last_lines

        if found:
            print("$ 检测到所有关键词,任务完成")
            break

        time.sleep(interval)

# ...


# Function to select a file
def select_file(logApp_type):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    
    if logApp_type == LogAppType.VIVADO:
        print("$ 选择要监控的vivado工程下的proj_name.runs目录")
        time.sleep(2)
        file_path = filedialog.askdirectory()
        print("* 收到的vivado_Workpath: "+ file_path)
    else:
        print("$ 选择要监控的log文件")
        time.sleep(2)
        file_path = filedialog.askopenfilename()
        print("* 收到的log_Filepath: "+ file_path)
    
    root.destroy()
    print("-------------------------------------------------------------")
    return file_path

def input_num(word):
    try:
        num = int(input(word))
    except ValueError:
        num = 0
    return num

# function to read a ini file and return a dictionary
import configparser
def read_ini_file(file_path):
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the INI file
    config.read(file_path)

    # Initialize an empty dictionary to store the contents
    ini_dict = {}

    # Iterate through sections and options to populate the dictionary
    for section in config.sections():
        ini_dict[section] = {}
        for option in config.options(section):
            ini_dict[section][option] = config.get(section, option)

    return ini_dict
    
# Function to prompt user input
def say_hello(check_dic , apptype_dic):
    check_strs = []
    ini_contents = read_ini_file("info.ini")
    section_name = 'info'
    print("-------------------------------------------------------------")
    print("$             hello , welcome to use this program !      ")
    print("$ 这个程序帮助您在检测fpga软件中的log文件,在编译完成后用微信提醒您.")
    print("& 提示: enter键可以跳过任意需要输入的地方")
    print("-------------------------------------------------------------")
    print("* 请确保你的微信电脑版已经登录了.")
    print("* 请确保你的fpga软件已经开始运行了.")
    print("-------------------------------------------------------------")
    print("$ 选择要监控的产生log文件的软件类型: \n\t0 - 其他(监控用户选择的log文件及其关键词) \n\t1 - vivado软件(监控vivado目录的synth和impl)")
    if section_name in ini_contents and 'logapp' in ini_contents[section_name]:
        logApp_type = LogAppType(int(ini_contents[section_name]['logapp']))
    else:
        logApp_type = lambda:input_num("$ 请输入软件类型序号(不填为0):")
        logApp_type = LogAppType(logApp_type())
    
    print("最终选择的log软件类型是:" + str(logApp_type))

    if logApp_type == LogAppType.OTHER:
        print("$ 默认采用以下检测关键词:")
        for key, value in check_dic.items():
            print("* " + key + " : " + + "\"" + value + "\"")
            check_strs.append(value)
        print("-------------------------------------------------------------")
        if section_name in ini_contents and 'keyword' in ini_contents[section_name]:
            keyword = ini_contents[section_name]['keyword']
            print("$ 检测到ini文件,以下为要生效的关键词:\n\t" + "\"" + keyword + "\"")
        else:
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
    print("$ 可供选择的通信软件列表:")
    for key, value in apptype_dic.items():
        print("\t* " + key + " : " + value)
    
    if section_name in ini_contents and 'apptype' in ini_contents[section_name]:
        key_input = ini_contents[section_name]['apptype']
    else:
        key_input = input("$ 请选择要使用的通信软件(不输入为wechat):")
    
    if key_input not in set(apptype_dic.keys()):
        key_input = "0"
        
    print("最终选择的软件是:" + apptype_dic[key_input])
    print("-------------------------------------------------------------")
    if section_name in ini_contents and 'friend' in ini_contents[section_name]:
        friend_name = ini_contents[section_name]['friend']
    else:
        friend_name = input("$ 请输入微信好友，想把消息发给谁，(不输入为'文件传输助手'):")
    
    if not friend_name:
        friend_name = "文件传输助手"
    print("The friend's name is: " + friend_name)
    print("-------------------------------------------------------------")
    dft_interval_sec = 10
    dft_timeout_cnt = 12
    if section_name in ini_contents and 'timeout' in ini_contents[section_name]:
        interval_sec = dft_interval_sec
        timeout_cnt = ini_contents[section_name]['timeout']
    else:
        print("$ 选择查询间隔时间和文件不更新后判定失败的检测次数")
        interval_sec = input("$ 请输入查询间隔时间(不输入为"+str(dft_interval_sec)+"s):")
        timeout_cnt =  input("$ 请输入判定失败的所需检测次数timeout(不输入为" + str(dft_timeout_cnt) + "次):")
    
    if interval_sec == "":
        interval_sec = dft_interval_sec
    else :
        interval_sec = int(interval_sec)
    
    if timeout_cnt == "":
        timeout_cnt = dft_timeout_cnt
    else:
        timeout_cnt = int(timeout_cnt)

    print("查询间隔时间" + str(interval_sec) + "s" + "; 文件不更新后判定失败的检测次数" + str(timeout_cnt) + "次")
    print("-------------------------------------------------------------")
    return logApp_type, friend_name, check_strs, apptype_dic[key_input], interval_sec, timeout_cnt

# Main function
if __name__ == '__main__':
    contents = []
    default_check_dic = {"安路软件关键词": "Generate bits file"}
    default_apptype_dic = {"0": "wechat", "1": "wechat_work"}
    logApp_type, friend_name, check_strs, app_type, interval_sec, timeout_cnt = say_hello(default_check_dic, default_apptype_dic)
    log_file_path = select_file(logApp_type)
    
    continuously_check_log_thread = threading.Thread(target=continuously_check_log, args=(logApp_type, log_file_path, contents, check_strs, interval_sec, timeout_cnt , 20))
    continuously_check_log_thread.start()
    continuously_check_log_thread.join()  # Wait for log checking thread to complete
    send_msg(friend_name, contents, app_type)
