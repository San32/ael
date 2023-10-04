import sys

import cv2
import numpy as np
from PIL import Image, ImageFont, ImageTk
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtTest import *
from PyQt5.QtWidgets import *

"""
    사용자 모듈
"""
from camera import *
from common import *
from modelEL import *
from ui_autoel import *
from ui_config import *

from e1214_modbus import *




class Main_win(QMainWindow):
    """
    여기다 적으면 접힌다.
    """

    def __init__(self):
        super().__init__()

        self.model = None

        self.img_size_w = 400
        self.img_size_h = 300

        self.init_ui()
        
        self.init_timer()
        # self.init_model()

        
        self.init_menu()

        self.auto_exe()
    
    ### 프로그램 시작 시 자동실행
    def auto_exe(self):
        #초기값을 불러온다

        self.data = read_config(path_config)

        print(f"auto_run : {self.data['auto_run']}")
        if bool(self.data['auto_run']):
            self.show_autoel()
            self.init_cam()
            # self.timer_infer.start()


        ###check
        
        

    ### 메뉴
    def init_menu(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        
        exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        # exitAction.triggered.connect(qApp.quit)
        exitAction.triggered.connect(self.closeEvent)

        
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        ### 카메라 메뉴
        camMenu = menubar.addMenu("카메라")

        camstartAction = QAction('영상 재시작', self)
        camstartAction.triggered.connect(self.restart_cam)

        camstopAction = QAction('영상 중지', self)
        camstopAction.triggered.connect(self.stop_cam)

        showrectAction = QAction('영역 설정', self)
        showrectAction.triggered.connect(self.show_rectPanel)

        saverectAction = QAction('영역 저장', self)
        saverectAction.triggered.connect(self.save_rect)

        camMenu.addAction(camstartAction)
        camMenu.addAction(camstopAction)
        camMenu.addAction(showrectAction)
        camMenu.addAction(saverectAction)



        ### I/O 제어기 메뉴
        configMenu = menubar.addMenu("설정")

        showconfigAction = QAction('설정', self)
        # exitAction.setShortcut('Ctrl+Q')
        # showconfigAction.setStatusTip('설정')
        showconfigAction.triggered.connect(self.show_configPanel)

        configMenu.addAction(showconfigAction)

        fileDialogAction = QAction('불러오기', self)
        fileDialogAction.triggered.connect(self.file_open_dialog)
        configMenu.addAction(fileDialogAction)

        ### I/O 제어기
        ioMenu = menubar.addMenu("I/O 제어기")

        showioAction = QAction('상태보기', self)
        showioAction.triggered.connect(self.show_io)
        ioMenu.addAction(showioAction)

    ## 메뉴 활성화 / 비활성화
    def menu_cont(self):
        pass

    ## 카메라 플레이하기 위한 준비
    def init_cam(self):
        

        if self.model == None:
            self.model = Model()

        self.up_cam1 = None
        self.up_cam2 = None
        self.dn_cam1 = None
        self.dn_cam2 = None

        self.list_cam = [self.up_cam1, self.up_cam2, self.dn_cam1, self.dn_cam2]
        self.list_url = [self.data['up']['cam1']['cam']['url'], self.data['up']['cam2']['cam']['url'], self.data['dn']['cam1']['cam']['url'], self.data['dn']['cam2']['cam']['url']]
        self.list_img = [self.ui_autoel.up_floor.img_cam1, self.ui_autoel.up_floor.img_cam2, self.ui_autoel.dn_floor.img_cam1, self.ui_autoel.dn_floor.img_cam2]
        self.list_name = ["cam1", "cam2", "cam1", "cam2"]
        self.list_detect = [self.data['up']['cam1'].get('detect'), self.data['up']['cam2'].get('detect'), self.data['dn']['cam1'].get('detect'), self.data['dn']['cam2'].get('detect')]
        self.list_cont = [self.ui_autoel.up_floor.edit_cont, self.ui_autoel.up_floor.edit_cont, self.ui_autoel.dn_floor.edit_cont, self.ui_autoel.dn_floor.edit_cont]
        self.list_poi = [self.data['up']['cam1'].get('poi'), self.data['up']['cam2'].get('poi'), self.data['dn']['cam1'].get('poi'), self.data['dn']['cam2'].get('poi')]

        for i in range(4):
            self.list_img[i]._flag_show_text = True
            self.list_img[i].text_str = "연결 안됨"
        #     self.list_cam[i] = VideoThread()
        #     self.list_cam[i].set_vi(self.list_url[i], self.list_name[i])
        #     self.list_cam[i].set_img_size(self.img_size_w, self.img_size_h)
        #     self.list_cam[i]._run_flag = True
        #     if bool(self.list_poi[i]['use']):
        #         print(f"{self.list_poi[i]['use']}")
        #         rect = QRect(int(self.list_poi[i]['x']), int(self.list_poi[i]['y']), int(self.list_poi[i]['e_x']), int(self.list_poi[i]['e_y']))
        #         self.list_img[i].receive_rect(rect)
        #         self.list_img[i].show_ract(True)
        #         self.list_img[i].draw_ract(False)
        #     self.list_cam[i].start()


    ## 화면 디자인, 여러화면(QStackedWidget) 생성
    def init_ui(self):
        self.setWindowTitle("자동호출 시스템    Ver 3.1")

        self.statusBar = self.statusBar()
        self.statusBar.showMessage("ready")

        # self.setWindowIcon(QIcon('./assets/editor.png'))
        self.setGeometry(0, 0, 1300, 600)

        #UI 생성
        self.ui_config = UI_config()
        
        self.ui_autoel = UI_autoel()

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.ui_config)
        self.stacked_widget.addWidget(self.ui_autoel)
        self.setCentralWidget(self.stacked_widget)


    ## 반복수행 타이머
    def init_timer(self):
        self.timer_infer = QTimer()
        self.timer_infer.setInterval(400)
        # self.tm.timeout.connect(self.time_process)
        self.timer_infer.timeout.connect(self.infer_process)


    ## 종료시 정말종료할까요 물어보기
    def closeEvent(self, event):
        quit_msg = "Want to exit?"
        replay = QMessageBox.question(self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No)
        if replay == QMessageBox.Yes:
            # event.accept()
            qApp.quit()
        else:
            event.ignore()

    ## file open dialog 생성
    def file_open_dialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        print(type(fname), fname)


    ## config 파일을 읽고, 데이터 초기화
    def read_config(self):
        

        self.ui_autoel.up_floor.set_config(self.data['up'], "상부")
        self.ui_autoel.dn_floor.set_config(self.data['dn'], "하부")

        self.ui_autoel.up_floor.edit_cont.init_io(self.data['up']['io'])
        self.ui_autoel.dn_floor.edit_cont.init_io(self.data['dn']['io'])
        


    ## 모든 카메라 재시작
    def restart_cam(self):
        self.show_autoel()
        self.stop_cam()
        QTest.qWait(100)

        self.init_cam()
        self.timer_infer.start()
        
    ## 모든 카메라 중지
    def stop_cam(self):
        if self.timer_infer.isActive():
            self.timer_infer.stop()

        for i in range(4):
            self.list_cam[i]._run_flag = False
            self.list_img[i].load_default_img()
            self.list_img[i].show_ract(False)
            self.list_img[i].draw_ract(False)
            # self.list_cam[i].start()

    
    ## 영상분석 프로세스
    def infer_process(self):
        # print(f'timer process : {now_time_str()}')
        #  obj_cam, obj_img_label, obj_cont, obj_detect_list, name
        time_str = now_time_str()

        # list_cam_use [self.]
        

        for ii in range(4):
            if self.list_cam[ii].state == 11:
                img = self.list_cam[ii].get_img()  ##cv_img

                # print(f"get_img, {ii}, type({img})")
                

                ## poi 영역 계산
                x= int(self.list_poi[ii]['x'])
                y= int(self.list_poi[ii]['y'])
                end_x= int(self.list_poi[ii]['e_x']) + x
                end_y= int(self.list_poi[ii]['e_y']) + y
                
                ## 관심영역 테두리 표시
                cv2.rectangle(img, (x, y), (end_x, end_y), (0,0,255), 2)
                
                ## 관심영역 카피
                roi_img = img[y:end_y, x:end_x]
                # print(f'img : {type(img)} {img.shape}')

                # x=10
                # y=10
                # w=210
                # h=210
                # end_x = x+w
                # end_y = y+h
                # # print(f'x:{x}, y:{y}, w:{w}, h:{h}')
                # img2 = img[y:end_y, x:end_x]
                # print(f'img2 : {type(img2)} {img2.shape}')
                # output = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
                # print(f'output : {type(output)} {output.shape}')
                # img[y:end_y, x:end_x] = output
                # print(f'img : {type(img)} {img.shape}')
                

                # img, label_list = self.infer(img, self.list_detect[ii])
                roi_img2, label_list = self.infer(roi_img, self.list_detect[ii])
                img[y:end_y, x:end_x] = roi_img2

                self.list_cont[ii].receive_data( self.list_name[ii], label_list)
                # self.list_cont[ii].append(f'{self.list_name[ii]}, {label_list}')

                ## 필요한 처리   
                ## put_text(self, frame, text, w, h, color):
                if img is None:
                    print(f"get_img : image is None")
                else:
                    # img = self.put_text(img, time_str, 10, 10, (255, 255, 0))
                    self.list_img[ii].changePixmap(img)
            elif self.list_cam[ii].state == 0:  ## VT 멈추면 재시작
                print(f"VT restart")
                self.list_cam[ii]._flag_show_text = True
                self.list_cam[ii].text_str = "reconnecting..."
                # cv2.putText(frame, str, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, self.colors(int(labels[i])), 2)
                self.list_cam[ii]._run_flag = True
                self.list_cam[ii].start()

    ## 영상분석
    # input : cv_img, detect_list
    # return : img, label_list을 
    def infer(self, cv_img, detect_list):

        # print("infer ...")
        labels, cord = self.model.score_frame(cv_img)
        # print(f'plot_boxes  {labels}  {type(labels)}, {type(cord)}')
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
                    # print(f'{name} {row[4]} {type(row[4])} {detect_list[name]}, {type(float(detect_list[name]))}')

                    # print(f'row[4] > float(detect_list[name]) {row[4]} {float(detect_list[name])}')
                    x1, y1, x2, y2 = int(row[0] * x_shape), int(row[1] * y_shape), int(row[2] * x_shape), int(
                        row[3] * y_shape)
                    str = name + ": %0.1f" % row[4]
                    # print(f'plot_boxes str : {str}')
                    label_dict[name] = "%0.1f" % row[4]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), self.model.colors(int(labels[i])), 2)
                    
                    cv2.putText(frame, str, (x1+5, y1+15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.model.colors(int(labels[i])), 1)
                    
                    # label_list.append(str)
        time_str = now_time_str()
        cv2.putText(frame, time_str, (self.img_size_w - 100, self.img_size_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 1)
        return frame, label_dict

    ## 설정 화면
    def show_configPanel(self):
        self.stop_cam()
        self.ui_config.clicked_read()
        # self.setCentralWidget(self.ui_config)
        self.stacked_widget.setCurrentWidget(self.ui_config) 

    def show_rectPanel(self):
        # self.stop_cam()
        for i in range(4):
            # if bool(self.list_poi[i]['use']):
                # rect = QRect(int(self.list_poi[i]['x']), int(self.list_poi[i]['y']), int(self.list_poi[i]['w']), int(self.list_poi[i]['h']))
                # self.list_img[i].receive_rect(rect)
            self.list_img[i].show_ract(True)
            self.list_img[i].draw_ract(True)

    def show_autoel(self):
        # self.ui_autoel = UI_autoel()
        # self.setCentralWidget(self.ui_autoel)
        self.stacked_widget.setCurrentWidget(self.ui_autoel) 

    def save_rect(self):
        ## 화면크기를 벋어나지 않도록 조정
        # self.img_size_w = 400, self.img_size_h = 300
        for i in range(4):
            print(f'rect begin: {self.list_img[i].begin.x()}, {self.list_img[i].begin.y()}  end: {self.list_img[i].end.x()}, {self.list_img[i].end.y()}')
            print(f'type: {type(self.list_img[i].begin.x())}')
            
            if int(self.list_img[i].begin.x()) < 0:
                self.list_poi[i]['x'] = "0"
            elif int(self.list_img[i].begin.x()) > self.img_size_w:
                self.list_poi[i]['x'] = str(self.img_size_w)
            else:
                self.list_poi[i]['x'] = str(self.list_img[i].begin.x())

            if int(self.list_img[i].begin.y()) < 0:
                self.list_poi[i]['y'] = "0"
            elif int(self.list_img[i].begin.y()) > self.img_size_h:
                self.list_poi[i]['y'] = str(self.img_size_h)
            else:
                self.list_poi[i]['y'] = str(self.list_img[i].begin.y())

            if int(self.list_img[i].end.x()) < 0:
                self.list_poi[i]['e_x'] = "0"
            elif int(self.list_img[i].end.x()) > self.img_size_w:
                self.list_poi[i]['e_x'] = str(self.img_size_w)
            else:
                self.list_poi[i]['e_x'] = str(self.list_img[i].end.x() - self.list_img[i].begin.x())

            if int(self.list_img[i].end.y()) < 0:
                self.list_poi[i]['e_y'] = "0"
            elif int(self.list_img[i].end.y()) > self.img_size_h:
                self.list_poi[i]['e_y'] = str(self.img_size_h)
            else:
                self.list_poi[i]['e_y'] = str(self.list_img[i].end.y() - self.list_img[i].begin.y())

            # self.list_poi[i]['x'] = str(self.list_img[i].begin.x())
            # self.list_poi[i]['y'] = str(self.list_img[i].begin.y())
            # self.list_poi[i]['e_x'] = str(self.list_img[i].end.x() - self.list_img[i].begin.x())
            # self.list_poi[i]['e_y'] = str(self.list_img[i].end.y() - self.list_img[i].begin.y())

            # print(f'{self.list_poi[i]}')
        write_config(path_config, self.data)

    def show_io(self):
        self.io_panel = None
        ip = self.data['up']['io']['value_io_ip']
        port = 502
        self.io_panel = Win_io(ip, port)
        self.io_panel.setGeometry(100,800, 300, 100)
        self.io_panel.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Main_win()
    ex.show()
    sys.exit(app.exec_())
