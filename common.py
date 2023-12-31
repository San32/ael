import json
import sys
import time
from PIL import Image,ImageTk,ImageFont

global path_config

global RUN_OK 
global RUN_FAIL
global READ_OK
global READ_FAIL

# global pwd

font_path = "/home/nvidia/work/auto_el/data/NanumMyeongjoBold.ttf"
font = ImageFont.truetype(font_path, 20)

pwd = "/home/comm/conda_work/git_test/ael/"
# path_config = pwd + "sample1.json"
path_config = pwd + "config.json"

path_disconnect_file = pwd + 'disconnect.png'

CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK", "연결 끊어짐")
# RUN_OK = 1
# RUN_FAIL = 0
# READ_OK = 11
# READ_FAIL = 10

def read_config(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # print("파일 존재함.")
            # print(type(data))
            return data
    except Exception as e:
        print(f"read_config except :{e}")
        return e

##저장
def write_config(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent="\t")
            return True
    except(e):
        print(f'write_config except {e}')
        return False

def now_time_str():
    now = time.localtime()
    return time.strftime('%H:%M:%S', now)

# class Common():
