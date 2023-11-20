"""
어쩌구 저쩌구
"""
#-*-coding:utf-8-*-

import sys
import time
# import json
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import numpy as np

from e1214_modbus import *
from cont import *
from common import *
from camera import *
from modelEL import *
from ui_config import *


class Win(QMainWindow):
    """kk"""
    ## 모델 정의
    model = None
    default_img =  np.full(shape=(300, 400, 3), fill_value=200, dtype=np.uint8)
    run_img =  np.full(shape=(300, 400, 3), fill_value=10, dtype=np.uint8)
    read_fail_img =  np.full(shape=(300, 400, 3), fill_value=100, dtype=np.uint8)
    run_fail_img =  np.full(shape=(300, 400, 3), fill_value=50, dtype=np.uint8)
    fps_x = 5
    fps_y = 15
    stat_x = 5
    stat_y = 40

    def __init__(self):
        super().__init__()
        self.init_set()
        self.init_model()
        self.init_ui()
        self.init_menu()
        ## 메뉴 활성/비활성화 처리
        self.menu_click_process()
        # self.init_signal()
        self.show()
        self.auto_run()


### 메뉴
    def init_menu(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(True)

        fileMenu = menubar.addMenu('File')
        menubar.addSeparator()

        up_camMenu = menubar.addMenu("상부 카메라")
        menubar.addSeparator()

        dn_camMenu = menubar.addMenu("하부 카메라")
        menubar.addSeparator()
        
        confMenu = menubar.addMenu("설정")
        menubar.addSeparator()

        helpMenu = menubar.addMenu("&Help")
        
        exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        # exitAction.triggered.connect(qApp.quit)
        exitAction.triggered.connect(self.closeEvent)

                
        fileMenu.addAction(exitAction)

    ### file 하부 메뉴
        self.fileAction = QAction("file", self)
        self.fileAction.triggered.connect(self.fileopen)

        fileMenu.addAction(self.fileAction)
        fileMenu.addAction(exitAction)


    ### 상부 카메라 하부 메뉴
        self.up_cam1_startAction = QAction('cam1 시작', self)
        self.up_cam1_startAction.triggered.connect(self.start_up_cam1)
        self.up_cam1_stopAction = QAction('cam1 정지', self)
        self.up_cam1_stopAction.triggered.connect(self.stop_up_cam1)

        self.up_cam2_startAction = QAction('cam2 시작', self)
        self.up_cam2_startAction.triggered.connect(self.start_up_cam2)
        self.up_cam2_stopAction = QAction('cam2 정지', self)
        self.up_cam2_stopAction.triggered.connect(self.stop_up_cam2)

        up_camMenu.addAction(self.up_cam1_startAction)
        up_camMenu.addAction(self.up_cam1_stopAction)
        up_camMenu.addSeparator()
        up_camMenu.addAction(self.up_cam2_startAction)
        up_camMenu.addAction(self.up_cam2_stopAction)

    ### 하부 카메라 하부 메뉴

        self.dn_cam1_startAction = QAction('cam1 시작', self)
        self.dn_cam1_startAction.triggered.connect(self.start_dn_cam1)
        self.dn_cam1_stopAction = QAction('cam1 정지', self)
        self.dn_cam1_stopAction.triggered.connect(self.stop_dn_cam1)

        self.dn_cam2_startAction = QAction('cam2 시작', self)
        self.dn_cam2_startAction.triggered.connect(self.start_dn_cam2)
        self.dn_cam2_stopAction = QAction('cam2 정지', self)
        self.dn_cam2_stopAction.triggered.connect(self.stop_dn_cam2)

        dn_camMenu.addAction(self.dn_cam1_startAction)
        dn_camMenu.addAction(self.dn_cam1_stopAction)
        dn_camMenu.addSeparator()
        dn_camMenu.addAction(self.dn_cam2_startAction)
        dn_camMenu.addAction(self.dn_cam2_stopAction)

    ## 설정 하부 메뉴
        self.confAction = QAction('환경설정', self)
        self.confAction.triggered.connect(self.show_configPanel)
        
        confMenu.addAction(self.confAction)

    ## help 하부 메뉴
        self.helpAction = QAction('도움말', self)
        self.helpAction.triggered.connect(self.show_helpPanel)
        
        helpMenu.addAction(self.helpAction)


    def show_configPanel(self):
        ## 모든 카메라를 중지시키고 환경설정창을 띄운다.
        self.stop_cam(0)
        self.stop_cam(1)
        self.stop_cam(2)
        self.stop_cam(3)
        ## 창 띄우기
        dlg = UI_config()
        if dlg.exec_():
            print("acept...")
        else:
            print("cancel...")

        self.init_set()

        self.auto_run()
        

    def show_helpPanel(self):
        print(f"help")


    def show_img_rect(self):
        # self.stop_cam()
        for i in range(4):
            self.list_img[i].show_ract(True)
            self.list_img[i].draw_ract(True)

    def hide_img_rect(self):
        # self.stop_cam()
        for i in range(4):
            # if bool(self.list_poi[i]['use']):
                # rect = QRect(int(self.list_poi[i]['x']), int(self.list_poi[i]['y']), int(self.list_poi[i]['w']), int(self.list_poi[i]['h']))
                # self.list_img[i].receive_rect(rect)
            self.list_img[i].show_ract(False)
            self.list_img[i].draw_ract(False)
        


    def menu_click_process(self):
        ##
        if self.list_cam_btn_stat[0] == 0: ## stop
            self.up_cam1_startAction.setEnabled(True)
            self.up_cam1_stopAction.setEnabled(False)
        else:
            self.up_cam1_startAction.setEnabled(False)
            self.up_cam1_stopAction.setEnabled(True)

        ##
        if self.list_cam_btn_stat[1] == 0: ## stop
            self.up_cam2_startAction.setEnabled(True)
            self.up_cam2_stopAction.setEnabled(False)
        else:
            self.up_cam2_startAction.setEnabled(False)
            self.up_cam2_stopAction.setEnabled(True)

        ##
        if self.list_cam_btn_stat[2] == 0: ## stop
            self.dn_cam1_startAction.setEnabled(True)
            self.dn_cam1_stopAction.setEnabled(False)
        else:
            self.dn_cam1_startAction.setEnabled(False)
            self.dn_cam1_stopAction.setEnabled(True)

        ##
        if self.list_cam_btn_stat[3] == 0: ## stop
            self.dn_cam2_startAction.setEnabled(True)
            self.dn_cam2_stopAction.setEnabled(False)
        else:
            self.dn_cam2_startAction.setEnabled(False)
            self.dn_cam2_stopAction.setEnabled(True)


    ### 모델
    def init_model(self):
        if self.model == None:
            self.model = Model()
            # self.model.load_model_el()
            # self.model.load_model_yolov5()
            print(f"type(self.model) : {type(self.model)}")

        
        # self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')


    ####
    def start_up_cam1(self):
        self.start_cam(0)

    def start_up_cam2(self):
        self.start_cam(1)

    def start_dn_cam1(self):
        self.start_cam(2)

    def start_dn_cam2(self):
        self.start_cam(3)

    ####
    def stop_up_cam1(self):
        self.stop_cam(0)

    def stop_up_cam2(self):
        self.stop_cam(1)

    def stop_dn_cam1(self):
        self.stop_cam(2)

    def stop_dn_cam2(self):
        self.stop_cam(3)

    ####
    def start_cam(self, id):

        
        self.list_cam[id].set_init(self.list_url[id], self.list_name[id], id, 400, 300)

        self.list_img[id].signal_rect.connect(self.receive_rect)
        self.list_cam[id].change_state_signal.connect(self.receive_state)
    
        self.list_cam[id].auto_run()
        self.list_cam_btn_stat[id] = 1 ## start
        
        ## 메뉴 활성/비활성화 처리
        self.menu_click_process()

        
        self.list_cam_start_time[id] = time.time()
        

    def stop_cam(self, id):
        
        self.list_cam[id].stop()
        # self.list_cam[id] = None
        self.list_cam_btn_stat[id] = 0 ## stop

        ## 메뉴 활성/비활성화 처리
        self.menu_click_process()

        self.list_cam_stop_time[id] = time.time()

    def init_set(self):
        self.data = read_config(path_config)

        self.repeat_index = 0

        # self.list_cont = [None, None, None, None]
        

        # self.list_cam = [None, None, None, None]
        self.list_cam_btn_stat = [0, 0, 0, 0] ## 사용자가 선택한 상태 0:"stop", 1:"start", 
        self.list_cam_stat = [None, None, None, None] ## cam 에서 보내온 상태
        self.list_cam_stat_old = [None, None, None, None]  ## 이전 상태와 비교하기 위함.
        self.list_url = [self.data['up']['cam1']['cam']['url'], self.data['up']['cam2']['cam']['url'], self.data['dn']['cam1']['cam']['url'], self.data['dn']['cam2']['cam']['url']]
        self.list_cam_use = [self.data['up']['cam1']['cam']['use'], self.data['up']['cam2']['cam']['use'], self.data['dn']['cam1']['cam']['use'], self.data['dn']['cam2']['cam']['use']]
        self.list_cam_stop_time = [None, None, None, None]
        self.list_cam_start_time = [None, None, None, None]
        
        # self.list_img = [None, None, None, None]
        self.list_name = ["up cam1", "up cam2", "down cam1", "down cam2"]
        self.list_detect = [self.data['up']['cam1'].get('detect'), self.data['up']['cam2'].get('detect'), self.data['dn']['cam1'].get('detect'), self.data['dn']['cam2'].get('detect')]
        # self.list_cont = [self.ui_autoel.up_floor.edit_cont, self.ui_autoel.up_floor.edit_cont, self.ui_autoel.dn_floor.edit_cont, self.ui_autoel.dn_floor.edit_cont]
        self.list_poi = [self.data['up']['cam1'].get('poi'), self.data['up']['cam2'].get('poi'), self.data['dn']['cam1'].get('poi'), self.data['dn']['cam2'].get('poi')]
        self.list_io = [self.data['up'].get('io'), self.data['up'].get('io'), self.data['dn'].get('io'), self.data['dn'].get('io')]

    def init_ui(self):
        self.setWindowTitle("자동호출 시스템    Ver 3.1")

        self.statusBar = self.statusBar()
        self.statusBar.showMessage("ready")

        # self.setWindowIcon(QIcon('./assets/editor.png'))
        # self.setGeometry(0, 0, 1300, 600)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.make_floor_box())
        layout.addWidget(self.make_io_box())

        self.setCentralWidget(widget)
        # self.layout = QVBoxLayout(self.central_widget)


    def make_io_box(self):
        ip = "10.128.17.49"
        port = 502
    
        # self.io_box = Win_io(ip, port)
        # return Win_widget(ip, port)
        return Win_io(ip, port)


    def make_floor_box(self):
        self.list_cam = [None, None, None, None]
        self.list_img = [None, None, None, None]
        for id in range(4):
            cam = VideoThread()
            self.list_cam[id] = cam

            label = ImgLabel()
            label._flag_show_text = True
            label.tag = int(id)
            label.setFixedSize(400, 300)
            # label.setStyleSheet("color: white; border-style: solid; border-width: 2px; border-color: #54A0FF; background-color: rgb(0,0,0)")
            self.list_img[id] = label

            # CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK", "연결 끊어짐")
            stat_text = (self.stat_x, self.stat_y, "연결 끊어짐") 
            list_text = [stat_text]
            self.list_img[id].list_text = list_text
            self.list_img[id].changePixmap(self.run_fail_img)

        self.cont_up = Cont()
        self.cont_dn = Cont()

        self.cont_up.init_io(self.data['up']['io'])
        self.cont_dn.init_io(self.data['dn']['io'])

        self.list_cont = [self.cont_up, self.cont_up, self.cont_dn, self.cont_dn]



        h1 = QHBoxLayout()
        h2 = QHBoxLayout()
        main = QVBoxLayout()

        h1.addWidget(self.list_img[0])
        h1.addWidget(self.list_img[1])
        h1.addWidget(self.cont_up)
        h2.addWidget(self.list_img[2])
        h2.addWidget(self.list_img[3])
        h2.addWidget(self.cont_dn)

        widget = QWidget(self)
        main.addLayout(h1)
        main.addLayout(h2)
        widget.setLayout(main)

        return widget

    
    def init_signal(self):
        for i in range(4):
            self.list_img[i].signal_rect.connect(self.receive_rect)
            self.list_cam[i].change_state_signal.connect(self.receive_state)

    def fileopen(self):
        fname = QFileDialog.getOpenFileName(self, "Open file", './')
        print(type(fname), fname)
        return fname

    # def read_conf(self):
    #     """ 현재폴더아래에서 init.json을 읽어서 config파일 읽어온다.
    #         conf 파일이 없거나 config 파일 경로가 없으면, 파일 오픈 다이알로그를 실행한다.
    #     """
    #     init_conf = os.getcwd() + "/"+ "init.json"
    #     print(f"current_conf path : {init_conf}")
    #     if os.path.isfile(init_conf):    
    #         """ init 파일이 존재함"""
    #         # print("ok")
    #         try:
    #             with open(init_conf, 'r') as file:
    #                 self.conf_data = json.load(file)
    #                 # print(self.conf_data)
    #                 el_config_path = self.conf_data['el_config_file']
    #                 print(el_config_path)
    #                 if os.path.isfile(el_config_path):
    #                     """ config 파일이 존재하므로 읽어서 self.data에 넣는다
    #                     """
    #                     with open(el_config_path, 'r') as file:
    #                         self.data = json.load(el_config_path)
    #                         print(self.data)
    #                 else:
    #                     self.data = None
    #         except Exception as e:
    #             print(f"read_config except :{e}")
    #             self.data = None
    #     else:
    #         """ init 파일이 없음, 므로 새로 만든다 """
        
    #     if self.data == None:
    #         """ config 파일을 읽지 못함. """
    #         print("config 파일을 읽지 못함.")
            self.fileopen()
    
    def auto_run(self):

        self.read_conf()
        
        # self.init_timer(int(self.data['comm']['read_cam_time']))
        # self.timer_repeat.start()
        # # pass
        # if bool(self.data['comm']['auto_start']):
        #     for id in range(4):
        #         if bool(self.list_cam_use[id]):
        #             self.start_cam(id)

    ## 반복수행 타이머
    def init_timer(self, repeat_time):
        
        self.timer_repeat = QTimer()
        self.timer_repeat.setInterval(repeat_time)
        # self.tm.timeout.connect(self.time_process)
        self.timer_repeat.timeout.connect(self.repeat_process)


    # def repeat_process(self):
    #     # print(f'[{now_time_str()}] {self.list_cam_stat}')

    #     start_time = time.time()
    #     for id in range(4):
    #         ## CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK")
    #         if self.list_cam_stat[id] == "READ_OK":
    #             # print(f"READ_OK")

    #             img, fps = self.list_cam[id].get_img()

    #             ## poi 영역
    #             if self.list_poi[id]['use']:
    #                 ## 영역만 detect
    #                 ## poi 영역 계산
    #                 x= int(self.list_poi[id]['x'])
    #                 y= int(self.list_poi[id]['y'])
    #                 end_x= int(self.list_poi[id]['e_x']) + x
    #                 end_y= int(self.list_poi[id]['e_y']) + y
                    
    #                 ## 관심영역 테두리 표시
    #                 cv2.rectangle(img, (x, y), (end_x, end_y), (0,0,255), 2)
                    
    #                 ## 관심영역 카피
    #                 roi_img = img[y:end_y, x:end_x]

    #                 ## 관심영역 detect
    #                 roi_img2, label_dict = self.infer(roi_img, self.list_detect[id])
    #                 img[y:end_y, x:end_x] = roi_img2

                            
    #             else:   ## 전체 detect
    #                 ## 전체 영역 테두리 표시(관심영역과 동일한 색으로 표시)
    #                 cv2.rectangle(img, (0, 0), (400, 300), (0,0,255), 2)
    #                 img, label_dict = self.infer(img, self.list_detect[id])


    #             self.list_cont[id].receive_data( self.list_name[id], label_dict)

    #             fps_text = (self.fps_x,self.fps_y, str(fps))
    #             stat_text = (self.stat_x, self.stat_y, str(self.list_cam_stat[id]))
    #             list_text = [fps_text, stat_text]
    #             self.list_img[id].list_text = list_text
    #             self.list_img[id].changePixmap(img)
    #         # else:
    #         #     stat_text = (self.stat_x, self.stat_y, "disconnect")
    #         #     list_text = [ stat_text]
    #         #     self.list_img[id].list_text = list_text
    #         #     self.list_img[id].changePixmap(self.run_fail_img)
    #         elif self.list_cam_stat[id] == "RUN_FAIL":
    #             print(f"{self.list_name[id]} : RUN_FAIL")
    #             # fps_text = (self.fps_x,self.fps_y, str(0))
    #             # stat_text = (self.stat_x, self.stat_y, str(self.list_cam_stat[id]))
    #             # list_text = [fps_text, stat_text]
    #             # self.list_img[id].list_text = list_text
    #             self.list_img[id].changePixmap(self.run_fail_img)
    #             # self.list_cont[id].receive_log(f'[{now_time_str()}] : {self.list_name[id]}  {self.list_cam_stat[id]}')
    #             if self.list_cam_btn_stat[id] == 1:
    #                 gap = time.time() - self.list_cam_start_time[id]

    #                 print(f"다시시작 {gap}")
    #                 self.list_cam_stat[id] = None
    #                 self.start_cam(id)

    #                 # gap = time.time() - self.list_cam_start_time[id]
    #                 # print(f"{self.list_name[id]}   {self.list_cam_start_time[id]}  gap:{gap}")
    #                 # if (gap > 5.0) & (self.list_cam_start_time[id] == "RUN_FAIL"):
    #                 #     print(f"5초경과로 다시시작")
    #                 #     self.start_cam(id)

    #         # elif self.list_cam_stat[id] == "RUN_OK":
    #         #     # print(f"RUN_FAIL")
    #         #     # fps_text = (self.fps_x,self.fps_y, str(0))
    #         #     stat_text = (self.stat_x, self.stat_y, str(self.list_cam_stat[id]))
    #         #     list_text = [stat_text]
    #         #     self.list_img[id].list_text = list_text
    #         #     self.list_img[id].changePixmap(self.run_img)
    #         #     # self.list_cont[id].receive_log(f'[{now_time_str()}] : {self.list_name[id]}  {self.list_cam_stat[id]}')
    #         #     pass
    #         # elif self.list_cam_stat[id] == "READ_FAIL":
    #         #     print(f"{self.list_name[id]} : READ_FAIL")
    #         #     stat_text = (10, 40, str(self.list_cam_stat[id]))
    #         #     list_text = [stat_text]
    #         #     self.list_img[id].list_text = list_text
    #         #     self.list_img[id].changePixmap(self.read_fail_img)
    #         #     pass
    #     end_time = time.time()
    #     # print(f"{end_time - start_time:.5f}sec")
    #     self.statusBar.showMessage(f"read & infer time : {(end_time - start_time)*1000:.2f}msec")

    def repeat_process(self):

        if self.repeat_index == 4:
            self.repeat_index = 0
        
        self.repeat_process_index(self.repeat_index)
        self.repeat_index = self.repeat_index + 1

    ## self.repeat_index 를 증가시키면서 카메라 하나씩 불러와서 실행한다
    def repeat_process_index(self, id):
        

        start_time = time.time()

               
        ## CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK")
        if self.list_cam_stat[id] == "READ_OK":
            # print(f"READ_OK")

            img, fps = self.list_cam[id].get_img()

            ## poi 영역
            if self.list_poi[id]['use']:
                ## 영역만 detect
                ## poi 영역 계산
                x= int(self.list_poi[id]['x'])
                y= int(self.list_poi[id]['y'])
                end_x= int(self.list_poi[id]['e_x']) + x
                end_y= int(self.list_poi[id]['e_y']) + y
                
                ## 관심영역 테두리 표시
                cv2.rectangle(img, (x, y), (end_x, end_y), (0,0,255), 2)
                
                ## 관심영역 카피
                roi_img = img[y:end_y, x:end_x]

                ## 관심영역 detect
                roi_img2, label_dict = self.infer(roi_img, self.list_detect[id])
                img[y:end_y, x:end_x] = roi_img2

                        
            else:   ## 전체 detect
                ## 전체 영역 테두리 표시(관심영역과 동일한 색으로 표시)
                cv2.rectangle(img, (0, 0), (400, 300), (0,0,255), 2)
                img, label_dict = self.infer(img, self.list_detect[id])


            self.list_cont[id].receive_data( self.list_name[id], label_dict)

            fps_text = (self.fps_x,self.fps_y, str(fps))
            stat_text = (self.stat_x, self.stat_y, str(self.list_cam_stat[id]))
            list_text = [fps_text, stat_text]
            self.list_img[id].list_text = list_text
            self.list_img[id].changePixmap(img)

        elif self.list_cam_stat[id] == "RUN_FAIL":
            print(f"{self.list_name[id]} : RUN_FAIL")

            self.list_img[id].changePixmap(self.run_fail_img)
            # self.list_cont[id].receive_log(f'[{now_time_str()}] : {self.list_name[id]}  {self.list_cam_stat[id]}')
            if self.list_cam_btn_stat[id] == 1:
                gap = time.time() - self.list_cam_start_time[id]

                print(f"다시시작 {gap}")
                self.list_cam_stat[id] = None
                self.start_cam(id)

        end_time = time.time()
        # print(f"{end_time - start_time:.5f}sec")
        self.statusBar.showMessage(f"{self.list_name[id]} read & infer time : {(end_time - start_time)*1000:.2f}msec")



    ### 영상분석
    ### input : cv_img, detect_list
    ### return : img, label_list을 
    def infer(self, cv_img, detect_list):
        
        # print("infer ...")
        labels, cord = self.model.score_frame(cv_img)
        # print(f'score_frame =>  {labels} : {type(labels)}, {cord} : {type(cord)}')
        label_list = []
        label_dict = {}
        n = len(labels)
        frame = cv_img
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            name = self.model.class_to_label(labels[i])
            # print(name)
            if name in detect_list:
                if row[4] > float(detect_list[name]):
                    # print(f'{name} {row[4]} {type(row[4])} {detect_list[name]}, {type(float(detect_list[name]))}, {float(detect_list[name]) - row[4] }')

                    # print(f'row[4] > float(detect_list[name]) {row[4]} {float(detect_list[name])}')
                    x1, y1, x2, y2 = int(row[0] * x_shape), int(row[1] * y_shape), int(row[2] * x_shape), int(row[3] * y_shape)
                    str = name + ": %0.2f" % row[4]
                    # print(f'plot_boxes str : {str}')
                    label_dict[name] = "%0.2f" % row[4]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), self.model.colors(int(labels[i])), 2)
                    
                    cv2.putText(frame, str, (x1+5, y1+15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.model.colors(int(labels[i])), 1)
                    
                    # label_list.append(str)
        # time_str = now_time_str()
        # cv2.putText(frame, time_str, (self.img_size_w - 100, self.img_size_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 1)
        return frame, label_dict


    @pyqtSlot(int, str)  #CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK")
    def receive_state(self, tag, stat):
        ## 쓰레드 상태를 수신해서 처리
        # print(f'receive state : {tag}, {stat} ')
        self.list_cam_stat[tag] = stat
        
            
        ##

    @pyqtSlot(int, bool, QRect)
    def receive_rect(self, tag, use, rect):
        print(f'[{now_time_str()}] rect receive : {tag} {use} {rect} {rect.left()} {rect.top()} {rect.width()} {rect.height()}')
        # print(f'{self.list_poi[tag]}')

        self.list_poi[tag]['use'] = use
        self.list_poi[tag]['x'] = str(rect.left())
        self.list_poi[tag]['y'] = str(rect.top())
        self.list_poi[tag]['e_x'] = str(rect.width())
        self.list_poi[tag]['e_y'] = str(rect.height())

        
        if tag == 0:
            self.data['up']['cam1']['poi'] = self.list_poi[0]
        elif tag == 1:
            self.data['up']['cam2']['poi'] = self.list_poi[1]
        elif tag == 2:
            self.data['dn']['cam1']['poi'] = self.list_poi[2]
        elif tag == 3:
            self.data['dn']['cam2']['poi'] = self.list_poi[3]

        # print(f'{self.list_poi[tag]}')
        print(f'{self.data}')

        write_config(path_config, self.data)

    ## 종료시 정말종료할까요 물어보기
    def closeEvent(self, event):
        quit_msg = "Want to exit?"
        replay = QMessageBox.question(self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No)
        if replay == QMessageBox.Yes:
            # event.accept()
            qApp.quit()
        else:
            event.ignore()



if __name__=="__main__":
    app = QApplication(sys.argv)
    # a = Cam()
    a = Win()
    # a.show()
    sys.exit(app.exec())
