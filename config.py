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

#module
from common import *
from camera import *
from e1214_modbus import *

# cam_dict = {
#     "url": "",
#     "cam_use": "true",
#     "value_open" : 0,
#     "value_close" : "",
#     "value_wheelchair" : "",
#     "value_stroller" : "",
#     "value_silvercar" : "",
#     "value_scuter" : "",
#     "poi_use" : "",
#     "value_x" : "",
#     "value_y" : "",
#     "value_w" : "",
#     "value_h" : "",
# }

# io_dict =  {
#     "value_io_ip": "",
#     "value_io_relay_port": "",
#     "value_io_delay_time": "",
#     }

url_width = 500




# ##저장
# def write_config(file_path, data):
#     try:
#         with open(file_path, 'w', encoding='utf-8') as file:
#             json.dump(data, file, indent="\t")
#             return True
#     except(e):
#         print(f'write_config except {e}')
#         return False

# def read_config(file_path):
#     try:
#         with open(file_path, 'r') as file:
#             data = json.load(file)
#             # print("파일 존재함.")
#             # print(type(data))
#             return data
#     except(e):
#         print(f"read_config except :{e}")
#         return e 

## 인식률 lineEdit
class ValueBox(QLineEdit):
    def __init__(self, val):
        super().__init__(val)
        self.setMaximumWidth(60)
        self.setAlignment(Qt.AlignRight)

class KSpinBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.setMaximum(640)
        self.setMinimum(0)

## QLabel 우측정렬
class KLabel(QLabel):
    def __init__(self, title):
        super().__init__()
        self.setText(title)
        # self.setAlignment(Qt.AlignRight)
        # self.setAlignment(Qt.AlignLeft)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("color: blue;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: green;"
                      "border-radius: 3px")
        self.setMinimumWidth(150)

## IO제어기 설정 UI
class IO_conf_ui(QWidget):

    def __init__(self, title):
        super().__init__()
        self.title = title
        self.init_ui()
        # self.show()

    def init_ui(self):
        self.io_ip = QLineEdit()
        self.io_relay_port = QLineEdit()
        self.io_delay_time = QLineEdit()
        self.btn_io_test = QPushButton("test")

        ##
        self.btn_io_test = QPushButton("Test")

        lay_1 = QHBoxLayout()
        lay_1.addWidget(KLabel(self.title))
        lay_1.addWidget(QLabel("   IP"))
        lay_1.addWidget(self.io_ip)
        lay_1.addWidget(QLabel("   릴레이 포트"))
        lay_1.addWidget(self.io_relay_port)
        lay_1.addWidget(QLabel("   지연시간"))
        lay_1.addWidget(self.io_delay_time)
        lay_1.addStretch(1)
        lay_1.addWidget(self.btn_io_test)

        self.setLayout(lay_1)

    def set_data(self, data):
        try:
            self.io_ip.setText(data['value_io_ip'])
            self.io_relay_port.setText(data['value_io_relay_port'])
            self.io_delay_time.setText(data['value_io_delay_time'])
        except:
            # print("err")
            return "E"

    def get_data(self):
        try:
            data = {
                    "value_io_ip": self.io_ip.text(),
                    "value_io_relay_port" : self.io_relay_port.text(),
                    "value_io_delay_time" : self.io_delay_time.text(),
                }
            return data

        except:
            # print("err")
            return "E"


class ELCam_conf_ui(QWidget):

    signal_clicked_btn_cam_set = pyqtSignal()

    def __init__(self, title):
        super().__init__()
        self.title = title
        self.init_ui()
        # self.show()

    def set_data(self, data):
        try:
            self.cam_url.setText(data['cam']['url'])
            self.cam_cam_use.setChecked(bool(data['cam']['use']))
            self.cam_value_open.setText(data['detect']['door_open'])
            self.cam_value_close.setText(data['detect']['door_close'])
            self.cam_value_wheelchair.setText(data['detect']['wheelchair'])
            self.cam_value_stroller.setText(data['detect']['stroller'])
            self.cam_value_silvercar.setText(data['detect']['silvercar'])
            self.cam_value_scuter.setText(data['detect']['scuter'])
            self.cam_poi_use.setChecked(bool(data['poi']['use']))
            self.cam_poi_x.setText(data['poi']['x'])
            self.cam_poi_y.setText(data['poi']['y'])
            self.cam_poi_w.setText(data['poi']['e_x'])
            self.cam_poi_h.setText(data['poi']['e_y'])
        except Exception as e:
            print(f'err {e}')
            return "E"

    def get_data(self):
        try:
            cam_data = {
                "url": self.cam_url.text(),
                "use": self.cam_cam_use.isChecked(),
            }

            detect_data = {
                "door_open" : self.cam_value_open.text(),
                "door_close" : self.cam_value_close.text(),
                "wheelchair" : self.cam_value_wheelchair.text(),
                "stroller" : self.cam_value_stroller.text(),
                "silvercar" : self.cam_value_silvercar.text(),
                "scuter" : self.cam_value_scuter.text(),
            }

            poi_data = {
                "use" : self.cam_poi_use.isChecked(),
                "x" : self.cam_poi_x.text(),
                "y" : self.cam_poi_y.text(),
                "e_x" : self.cam_poi_w.text(),
                "e_y" : self.cam_poi_h.text(),
            }
            data = {
                    "cam": cam_data,
                    "detect": detect_data,
                    "poi" : poi_data
            }
            return data

        except:
            # print("err")
            return "E"

    def change_cam_use(self, state):
        if state == Qt.Checked:
            self.cam_url.setEnabled(True)
        else:
            self.cam_url.setEnabled(False)

    def clicked_btn_cam_set(self):
        self.signal_clicked_btn_cam_set.emit()
        # pass

    def change_poi_use(self, state):
        if state == Qt.Checked:
            ## 
            self.cam_poi_x.setEnabled(True)
            self.cam_poi_y.setEnabled(True)
            self.cam_poi_w.setEnabled(True)
            self.cam_poi_h.setEnabled(True)
        else:
            self.cam_poi_x.setEnabled(False)
            self.cam_poi_y.setEnabled(False)
            self.cam_poi_w.setEnabled(False)
            self.cam_poi_h.setEnabled(False)

    def init_ui(self):
        ## 생성
        self.cam_url = QLineEdit()
        self.cam_cam_use = QCheckBox()
        self.cam_value_open = ValueBox("0.8")
        self.cam_value_close = ValueBox("0.8")
        self.cam_value_wheelchair = ValueBox("0.8")
        self.cam_value_stroller = ValueBox("0.8")
        self.cam_value_silvercar = ValueBox("0.8")
        self.cam_value_scuter = ValueBox("0.8")
        self.cam_poi_use = QCheckBox()
        self.cam_poi_x = ValueBox("0")
        self.cam_poi_y = ValueBox("0")
        self.cam_poi_w = ValueBox("640")
        self.cam_poi_h = ValueBox("480")

        self.btn_cam_set = QPushButton("설정")

        ## 설정
        self.cam_url.setMinimumWidth(600)
        
        self.cam_cam_use.stateChanged.connect(self.change_cam_use)
        self.cam_poi_use.stateChanged.connect(self.change_poi_use)
        self.btn_cam_set.clicked.connect(self.clicked_btn_cam_set)

        self.cam_url.setEnabled(False)
        self.cam_poi_x.setEnabled(False)
        self.cam_poi_y.setEnabled(False)
        self.cam_poi_w.setEnabled(False)
        self.cam_poi_h.setEnabled(False)
        

        ##
        lay_1 = QHBoxLayout()
        # lay_1.addWidget(KLabel("카메라 설정"))
        lay_1.addWidget(QLabel("사용"))
        lay_1.addWidget(self.cam_cam_use)
        lay_1.addWidget(QLabel("   URL"))
        lay_1.addWidget(self.cam_url)
        lay_1.addStretch(1)
        

        lay_2 = QHBoxLayout()
        # lay_2.addWidget(KLabel("민감도 설정"))
        lay_2.addWidget(QLabel("문 열림"))
        lay_2.addWidget(self.cam_value_open)
        lay_2.addWidget(QLabel("문 닫힘"))
        lay_2.addWidget(self.cam_value_close)
        lay_2.addWidget(QLabel("휠체어"))
        lay_2.addWidget(self.cam_value_wheelchair)
        lay_2.addWidget(QLabel("유모차"))
        lay_2.addWidget(self.cam_value_stroller)
        lay_2.addWidget(QLabel("실버카"))
        lay_2.addWidget(self.cam_value_silvercar)
        lay_2.addWidget(QLabel("스쿠터"))
        lay_2.addWidget(self.cam_value_scuter)
        lay_2.addStretch(1)

        lay_3 = QHBoxLayout()
        # lay_3.addWidget(KLabel("관심영역"))
        lay_3.addWidget(QLabel("사용"))
        lay_3.addWidget(self.cam_poi_use)
        # lay_3.addWidget(QLabel("   "), 1)
        lay_3.addWidget(QLabel("   시작점 x:"))
        lay_3.addWidget(self.cam_poi_x)
        lay_3.addWidget(QLabel("y:"))
        lay_3.addWidget(self.cam_poi_y)
        lay_3.addWidget(QLabel("   끝점 x"))
        lay_3.addWidget(self.cam_poi_w)
        lay_3.addWidget(QLabel("y:"))
        lay_3.addWidget(self.cam_poi_h)
        lay_3.addStretch(1)
        lay_3.addWidget(self.btn_cam_set)

        vbox = QVBoxLayout()
        vbox.addLayout(lay_1)
        vbox.addLayout(lay_2)
        vbox.addLayout(lay_3)

        ##
        lay = QHBoxLayout()
        lay.addWidget(KLabel(self.title))
        lay.addLayout(vbox)
        
        self.setLayout(lay)

class View_cam(QDialog):
    signal_rect = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        self.vi = None
        self.poi_use = None

        self.past_x = None
        self.past_y = None
        
        self.present_x = None
        self.present_y = None

        self.init_ui()
        self.init_signal()
        self.setMouseTracking(False)
        # self.show()
        # self.init_auto_show()

        
    def init_ui(self):
        self.setWindowTitle("카메라 설정")

        self.thread = VideoThread()
        
        self.image_label = ImgLabel()
        self.image_label.setFixedSize(640, 480)

        self.vi_edit = QLineEdit()

        self.btn_play = QPushButton("play")
        self.btn_stop = QPushButton("stop")
        self.btn_snap = QPushButton("snap")

        self.use  = QCheckBox("관심영역 설정")
        self.draw_rect = QCheckBox("그리기")
        self.x = KSpinBox()
        self.y = KSpinBox()
        self.w = KSpinBox()
        self.h = KSpinBox()

        self.btn_save = QPushButton("적용") 
        self.btn_close = QPushButton("나가기")

        ## layout
        lay_poi = QHBoxLayout()
        lay_poi.addWidget(self.use)
        lay_poi.addWidget(self.x)
        lay_poi.addWidget(self.y)
        lay_poi.addWidget(self.w)
        lay_poi.addWidget(self.h)
        lay_poi.addWidget(self.draw_rect)

        lay_cont = QHBoxLayout()
        lay_cont.addWidget(self.btn_play)
        lay_cont.addWidget(self.btn_stop)
        lay_cont.addWidget(self.btn_snap)

        lay_btn = QHBoxLayout()
        lay_btn.addWidget(self.btn_save)
        lay_btn.addWidget(self.btn_close) 
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label,1)
        main_layout.addWidget(self.vi_edit)
        main_layout.addLayout(lay_cont)
        main_layout.addLayout(lay_poi,1)
        main_layout.addLayout(lay_btn)
        
        self.setLayout(main_layout)
        # self.resize(700,600)

        print("init")

    def set_data(self, data):
        self.data = data

        self.vi_edit.setText(self.data['cam']['url'])
        self.use.setChecked(bool(self.data['poi']['use']))
        self.x.setValue(int(self.data['poi']['x']))
        self.y.setValue(int(self.data['poi']['y']))
        self.w.setValue(int(self.data['poi']['e_x']))
        self.h.setValue(int(self.data['poi']['e_y']))

    def get_data(self):
        self.data['cam']['url'] = self.vi_edit.text()
        self.data['poi']['use'] = self.use.isChecked()
        self.data['poi']['x'] = str(self.x.value())
        self.data['poi']['y'] = str(self.y.value())
        self.data['poi']['e_x'] = str(self.w.value())
        self.data['poi']['e_y'] = str(self.h.value())

    def init_signal(self):
        self.thread.change_pixmap_signal.connect(self.image_label.changePixmap)
        self.image_label.signal_rect.connect(self.change_img_rect)
        self.signal_rect.connect(self.image_label.receive_rect)

        self.btn_play.clicked.connect(self.clicked_play)
        self.btn_stop.clicked.connect(self.clicked_stop)
        self.btn_snap.clicked.connect(self.clicked_snap)
        
        self.btn_close.clicked.connect(self.clicked_close)
        self.btn_save.clicked.connect(self.clicked_save)
        self.use.stateChanged.connect(self.change_use)
        self.draw_rect.stateChanged.connect(self.change_draw_rect)

        self.x.valueChanged.connect(self.change_poi)
        self.y.valueChanged.connect(self.change_poi)
        self.w.valueChanged.connect(self.change_poi)
        self.h.valueChanged.connect(self.change_poi)

    @pyqtSlot(QRect)
    def change_img_rect(self, rect):
        # print(f'receive rect : {rect.bottomLeft().x()},{rect.bottomLeft().y()}, {rect.bottomRight().x()}, {rect.bottomRight().y()}')
        self.x.setValue(rect.x())
        self.y.setValue(rect.y())
        self.w.setValue(rect.right())
        self.h.setValue(rect.bottom())

    def change_poi(self):
        rect = QRect(QPoint(self.x.value(), self.y.value()), QPoint(self.w.value(), self.h.value()))
        # print(f'rect : {rect}')
        # if self.sender() == self.x:
        #     print(f'x: {self.x.value()}')
        self.signal_rect.emit(rect)
 
    def change_use(self, state):
        if state == Qt.Checked:
            ## 
            self.x.setEnabled(True)
            self.y.setEnabled(True)
            self.w.setEnabled(True)
            self.h.setEnabled(True)
            self.image_label.show_ract(True)
        else:
            self.x.setEnabled(False)
            self.y.setEnabled(False)
            self.w.setEnabled(False)
            self.h.setEnabled(False)
            self.image_label.show_ract(False)

    def change_draw_rect(self, state):
        if state == Qt.Checked:
            self.image_label.draw_ract(True)
        else:
            
            self.image_label.draw_ract(False)

    def clicked_play(self):
        self.thread.set_vi(self.vi_edit.text(), self.vi_edit.text())
        self.thread.set_img_size(640, 480)
        self.thread._run_flag = True
        self.thread._show_flag = True
        self.thread.start()
        pass

    def clicked_stop(self):
        self.thread.stop()
        pass

    def clicked_snap(self):
        pass

    def clicked_save(self):
        self.get_data()
        self.accept()

    def clicked_close(self):
        self.reject()
        
    def init_auto_show(self):
        self.thread.auto_show()

    def stop_thread(self):
        del self.thread
        self.close()

    def showModal(self):
        return super().exec_()

class View_io_test(QDialog):
    # signal_rect = pyqtSignal(QRect)

    def __init__(self, ip, port ):
        super().__init__()
        self.win_io = Win_io(ip, port)
        
        layout = QVBoxLayout()
        layout.addWidget(self.win_io)

        self.setLayout(layout)
        
    # def init_ui(self):
    #     ip = "10.128.17.49"
    #     port = 502

        

    def showModal(self):
        return super().exec_()
        

class Config_main_ui(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_signal()
        self.clicked_read()
        self.show()

    def init_ui(self):
        self.up_cam1 = ELCam_conf_ui("cam1")
        self.up_cam2 = ELCam_conf_ui("cam2")
        self.up_io = IO_conf_ui("IO 제어기")

        self.dn_cam1 = ELCam_conf_ui("cam1")
        self.dn_cam2 = ELCam_conf_ui("cam2")
        self.dn_io = IO_conf_ui("IO 제어기")

        ##버튼
        self.btn_read = QPushButton("read")
        self.btn_save = QPushButton("save")

        btn_widget = QWidget()
        btn_lay = QHBoxLayout()
        btn_lay.addWidget(self.btn_read)
        btn_lay.addWidget(self.btn_save)
        btn_widget.setLayout(btn_lay)

        ##
        up_grb = QGroupBox("상부 카메라")
        up_lay = QVBoxLayout()
        up_lay.addWidget(self.up_cam1)
        up_lay.addWidget(self.up_cam2)
        up_lay.addWidget(self.up_io)
        up_grb.setLayout(up_lay)

        dn_grb = QGroupBox("하부 카메라")
        dn_lay = QVBoxLayout()
        dn_lay.addWidget(self.dn_cam1)
        dn_lay.addWidget(self.dn_cam2)
        dn_lay.addWidget(self.dn_io)
        dn_grb.setLayout(dn_lay)

        ##
        vbox = QVBoxLayout()
        vbox.addWidget(up_grb)
        vbox.addWidget(dn_grb)
        vbox.addWidget(btn_widget)

        self.setLayout(vbox)
        self.resize(1000,500)


    def init_signal(self):

        self.btn_read.clicked.connect(self.clicked_read)
        self.btn_save.clicked.connect(self.clicked_save)

        self.up_cam1.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_up_cam_1)
        self.up_cam2.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_up_cam_2)
        self.dn_cam1.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_dn_cam_1)
        self.dn_cam2.signal_clicked_btn_cam_set.connect(self.clicked_btn_view_dn_cam_2)

        ## io
        self.up_io.btn_io_test.clicked.connect(self.clicked_up_io_btn_test)
        self.dn_io.btn_io_test.clicked.connect(self.clicked_dn_io_btn_test)

    def clicked_up_io_btn_test(self):
            data = self.up_io.get_data()
            # print(data)
            io = View_io_test(data['value_io_ip'], 502)
            io.showModal()
            

    def clicked_dn_io_btn_test(self):
            data = self.dn_io.get_data()
            io = View_io_test(data['value_io_ip'], 502)
            io.showModal()
            

    @pyqtSlot()
    def clicked_btn_view_up_cam_1(self):
        data = self.up_cam1.get_data()
        v = View_cam()
        v.set_data(data)
        res = v.showModal()
        if res:
            print('save')
            print(v.data)
            self.up_cam1.set_data(v.data)

    @pyqtSlot()
    def clicked_btn_view_up_cam_2(self):
        data = self.up_cam2.get_data()
        v = View_cam()
        v.set_data(data)
        res = v.showModal()
        if res:
            print('save')
            print(v.data)
            self.up_cam2.set_data(v.data)

    @pyqtSlot()
    def clicked_btn_view_dn_cam_1(self):
        data = self.dn_cam1.get_data()
        v = View_cam()
        v.set_data(data)
        res = v.showModal()
        if res:
            print('save')
            print(v.data)
            self.dn_cam1.set_data(v.data)

    @pyqtSlot()
    def clicked_btn_view_dn_cam_2(self):
        data = self.dn_cam2.get_data()
        v = View_cam()
        v.set_data(data)
        res = v.showModal()
        if res:
            print('save')
            print(v.data)
            self.dn_cam2.set_data(v.data)


    ## 입력 시험
    def clicked_read(self):
        print(f"clicked_read")
        data = read_config(path_config)
        self.disp_data(data)
        pass

    def clicked_save(self):
        print(f"clicked_save")
        data = self.read_ui_make_data()
        print(data)
        write_config(path_config, data)
        pass

    def read_ui_make_data(self):
        pass
        up_data = {}
        dn_data = {}
        data ={}

        cam1 = self.up_cam1.get_data()
        cam2 = self.up_cam2.get_data()
        io = self.up_io.get_data()

        up_data['cam1'] = cam1
        up_data['cam2'] = cam2
        up_data['io'] = io

        ##
        cam1 = self.dn_cam1.get_data()
        cam2 = self.dn_cam2.get_data()
        io = self.dn_io.get_data()

        dn_data['cam1'] = cam1
        dn_data['cam2'] = cam2
        dn_data['io'] = io

        ##
        data['up'] = up_data
        data['dn'] = dn_data

        return data

    def disp_data(self, data):  
        self.up_cam1.set_data(data['up']['cam1'])
        self.up_cam2.set_data(data['up']['cam2'])
        self.up_io.set_data(data['up']['io'])

        self.dn_cam1.set_data(data['dn']['cam1'])
        self.dn_cam2.set_data(data['dn']['cam2'])
        self.dn_io.set_data(data['dn']['io'])

    def cam_get_test(self):
        print(f'clicked read')

        data = self.up_cam1.get_data()
        print(f'type : {type(data)}')
        print(data)

        data = self.up_io.get_data()
        print(f'type : {type(data)}')
        print(data)

    def cam_set_test(self):
        print(f'clicked save')
        cam_dict = {
				"url": "rtsp:............111",
				"cam_use": "true",
				"value_open" : "",
				"value_close" : "",
				"value_wheelchair" : "",
				"value_stroller" : "",
				"value_silvercar" : "",
				"value_scuter" : "",
				"poi_use" : "false",
				"value_x" : "",
				"value_y" : "",
				"value_w" : "",
				"value_h" : "",
			}
        self.up_cam1.set_data(cam_dict)

        io_dict =  {
            "value_io_ip": "000.000.000.000",
            "value_io_relay_port": "1",
            "value_io_delay_time": "10",
            }
        self.up_io.set_data(io_dict)


class Main():
    def __init__(self):
        super().__init__()

        self.show_main_ui()
        # self.view_cam = View_cam()

        

        
    def show_main_ui(self):
        app = QApplication(sys.argv)
        ex = Config_main_ui()
        sys.exit(app.exec_())

    def init_signal(self):
        
        pass

    


if __name__=="__main__":
    app = QApplication(sys.argv)
    ex = Config_main_ui()
    sys.exit(app.exec_())
    