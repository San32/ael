import cv2
import json
import sys
import time
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import numpy as np


from common import *
from camera import *
from cont import *
from ui_config import *


class Panel_floor(QWidget):
    def __init__(self):
        super().__init__()
        # self.set_config()
        self.init_ui()

        
    def set_config(self, data, name ):
        ## data['up']
        self.data = data

        self.name = name
        self.cam1_url = self.data['cam1']['cam']['url']
        self.cam2_url = self.data['cam2']['cam']['url']
        self.io_ip = self.data['io']['value_io_ip']
        self.io_port = self.data['io']['value_io_relay_port']
             
      

        # self.cam_1.set_vi(self.data['cam1']['cam']['url'], 'cam1')
        # self.cam_2.set_vi(self.data['cam2']['cam']['url'], 'cam2')
        self.label_title.setText(self.name)

        self.img_cam1._flag_show_text = True
        self.img_cam1.text_str = self.cam1_url

        self.img_cam2._flag_show_text = True
        self.img_cam2.text_str = self.cam2_url

        self.edit_cont.append(f'IO제어기 IP:{self.io_ip} port:{self.io_port}')

        # self.init_cont()   

    def init_ui(self):
        self.title_w = 80
        self.title_h = 300

        self.img_w = 400
        self.img_h = 300

        self.cont_w = 400
        self.cont_h = 300

        self.label_title = QLabel("name")
        self.img_cam1 = ImgLabel()
        self.img_cam2 = ImgLabel() 

        self.edit_cont = Cont()
        

        self.label_title.setFixedSize(self.title_w, self.title_h)
        self.img_cam1.setFixedSize(self.img_w, self.img_h)
        self.img_cam2.setFixedSize(self.img_w, self.img_h)
        self.edit_cont.setFixedSize(300, self.cont_h)

        self.label_title.setStyleSheet("color: white;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "background-color: blue;"
                      "border-radius: 3px")
        self.label_title.setAlignment(Qt.AlignCenter)
        # self.cam1.setStyleSheet("color: white; border: 1px solid black; background-color: black;")
        # self.cam2.setStyleSheet("color: white; border: 1px solid black; background-color: black;")

        box_cam = QHBoxLayout()
        box_cam.addWidget(self.label_title)
        box_cam.addWidget(self.img_cam1)
        box_cam.addWidget(self.img_cam2)
        box_cam.addWidget(self.edit_cont)

        ## 콘트롤을 위한 위젯 생성
        self.conf_cam1 = ELCam_conf_ui2("cam1")
        self.conf_cam2 = ELCam_conf_ui2("cam2")
        self.chk_poi = QCheckBox("관심영역")
        self.chk_poi2 = QCheckBox("test2")

        box_info = QHBoxLayout()
        box_info.addWidget(self.conf_cam1)
        box_info.addWidget(self.conf_cam2)
        # box_info.addWidget(self.chk_poi)
        # box_info.addWidget(self.chk_poi2)

        ## main box
        box_main = QVBoxLayout()
        box_main.addLayout(box_cam)
        # box_main.addLayout(box_info)

        self.setLayout(box_main)
        


class UI_autoel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.up_floor = Panel_floor()
        self.dn_floor = Panel_floor()

        vbox = QVBoxLayout()
        vbox.addWidget(self.up_floor)
        vbox.addWidget(self.dn_floor)

        self.setLayout(vbox)


if __name__=="__main__":
    app = QApplication(sys.argv)
    ex = UI_autoel()
    ex.show()
    sys.exit(app.exec_())