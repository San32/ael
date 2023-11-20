import cv2
import json
import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import numpy as np

from common import *
## global 상수 사용 : CAM_STAT = ("RUN_OK", "RUN_FAIL", "READ_OK" , "READ_FAIL")

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    
    change_state_signal = pyqtSignal(int, str) ## global RUN, PLAY, STOP, READ_FAIL

    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._run_flag = False
        self._show_flag = False # 직접 바로 보낸다
        self.name = None
        self.vi = None
        self.tag = 0
        self.fps = 0
        self.cap = None
        self.set_size = None
        # self.state = 0 ###{0: run 종료, 10: run 진입, 11:정상읽음, 12:읽기 실패 }

        # self.default_img = cv2.imread('0017.jpg')
        # self.default_img =  self.load_default_img()
        self.default_img =  np.full(shape=(300, 400, 3), fill_value=200, dtype=np.uint8)

        # self.disconnect_img =  self.load_disconnect_img()
        self.last_cv_img = self.default_img

        self.change_state(CAM_STAT[4])  ## CAM_STAT =  ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK", "Disconnect")

    def __del__(self):
        pass
        # self._run_flag = False
        # self._show_flag = False
        # if not self.cap is None:
        #     if self.cap.isOpen():
        #         print('카메라 오픈 되어 있음')
        #         self.cap.release()
        #     # sys.exit(0)

    def set_init(self, vi, name, tag, w, h):
        self.vi = vi
        self.name = name
        self.set_size = w, h
        self.tag = tag

    # def set_vi(self, vi, name):
    #     self.vi = vi
    #     self.name = name
        
    # def set_img_size(self, w, h):
    #     self.set_size = w, h


    def send_log(self, msg):
        # self.log_signal.emit(f'{self.name}:{msg}')
        print(f'{self.name}:{msg}')

     ## 계속 읽음
    def run(self):

        

        # FPS 계산을 위한 변수 초기화
        frame_count = 0
        start_time = time.time()
        fps = 0

        # capture from web cam
        # self.change_state(CAM_STAT[1])  ## CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK")
        # self.state = 10 ###{0: run 종료, 10: run 진입, 11:정상읽음, 12:읽기 실패 }
        try:
            # self.change_state(self.PLAY)
            self.cap = cv2.VideoCapture(self.vi)
            if self.cap.isOpened(): 
                self.change_state(CAM_STAT[1])  ## CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK")
                width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                self.send_log('original size: %d, %d' % (width, height))

                self.send_log(f'video start {self.vi}')
                while self._run_flag:
                    ret, cv_img = self.cap.read()
                    if ret:
                        #크기 변환 해서 저장
                        self.last_cv_img = cv2.resize(cv_img, self.set_size, interpolation=cv2.INTER_AREA)
                        self.change_state(CAM_STAT[3])  ## CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK")

                        ## 1초마다 FPS를 업데이트하고 출력
                        frame_count += 1
                        if time.time() - start_time >= 1:
                            fps = frame_count / (time.time() - start_time)
                            # print(f"[{self.name}] FPS: {fps:.2f}")
                            self.fps = f"FPS: {fps:.2f}"
                            frame_count = 0
                            start_time = time.time()

                        ## 글자가 깜빡이지 않기 위해 계속 표출해야함.
                        # fps_text = f"FPS: {fps:.2f}"
                        # cv2.putText(frame, fps_text, self.fps_org, self.font, 0.5, (255,0,0),2)

                    else:
                        # self.last_cv_img = self.default_img
                        # self.send_log(f"read : {ret} ..... break")
                        # self.change_state(CAM_STAT[2])  ## CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK")
                        self.cap.release()
                        self.send_log(f"vt run stop")
                        self.change_state(CAM_STAT[2]) ## CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK")
                        break
                    cv2.waitKey(50)
                self.cap.release()
            self.change_state(CAM_STAT[0]) ## CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK")
            
        except Exception as e:
            # self.send_msg.emit('%s' % e)
            self.send_log(f"[{self.name}]  start Video exception : {e}..... break")
            self.change_state(CAM_STAT[0]) ## CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK")


        

    ## 백업 2023.10.25
    def run_old(self):
        # capture from web cam
        # self.change_pixmap_signal.emit(self.default_img)
        self._run_flag = True
        self.state = 10 ###{0: run 종료, 10: run 진입, 11:정상읽음, 12:읽기 실패 }
        try:
            # self.change_state(self.PLAY)
            self.cap = cv2.VideoCapture(self.vi)
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.send_log('original size: %d, %d' % (width, height))

            ### 카메라 설정 변경 안됨
            # cap.set(cv2.CAP_PROP_FRAME_WIDTH, width/3)
            # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height/3)
            
            # width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            # height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            # print('changed size: %d, %d' % (width, height))

            self.send_log(f'video start {self.vi}')
            while self._run_flag:
                ret, cv_img = self.cap.read()
                if ret:
                    if cv_img is None:
                        print(f'cv_img is None')
                        pass
                    else:
                        #크기 변환 해서 저장
                        self.last_cv_img = cv2.resize(cv_img, self.set_size, interpolation=cv2.INTER_AREA)

                        if self._show_flag :
                            self.change_pixmap_signal.emit(self.last_cv_img)
                        
                        self.state = 11 ###{0: run 종료, 10: run 진입, 11:정상읽음, 12:읽기 실패 }
                else:
                    # self.last_cv_img = self.default_img
                    self.send_log(f"read : {ret} ..... break")
                    self.state = 12 ###{0: run 종료, 10: run 진입, 11:정상읽음, 12:읽기 실패 }
                    break
                cv2.waitKey(50)
            # self.last_cv_img = self.default_img
            
        except Exception as e:
            # self.send_msg.emit('%s' % e)
            self.send_log(f"start Video exception : {e}..... break")
            self.state = 12 ###{0: run 종료, 10: run 진입, 11:정상읽음, 12:읽기 실패 }

        # shut down capture system
        self._run_flag = False
        self.change_pixmap_signal.emit(self.default_img)
        # self.change_state(self.STOP)
        self.state = 0 ###{0: run 종료, 10: run 진입, 11:정상읽음, 12:읽기 실패 }
        self.cap.release()
        self.send_log(f"vt run stop")
        
    @pyqtSlot()
    def auto_run(self):
        """Sets run flag to False and waits for thread to finish"""
        self.send_log(f'auto start')
        self._run_flag = True
        # self._show_flag = True
        self.start()
        # self.wait()

    @pyqtSlot()
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.send_log(f'vt stop')
        self._run_flag = False
        # self.wait()

    @pyqtSlot()
    def get_img(self):
        # print(self.last_cv_img.shape)
        # self.change_pixmap_signal.emit(self.last_cv_img)
        img = self.last_cv_img
        # self.last_cv_img = self.default_img
        return img, self.fps

    @pyqtSlot()
    def get_img_default(self):
        self.change_pixmap_signal.emit(self.default_img)


    def change_state(self, stat):
        # self.send_log(f'vt : {stat}')
        self.change_state_signal.emit(self.tag, stat)
        # self.state = stat

class ImgLabel(QLabel):
    # ResizeSignal = pyqtSignal(int)
    signal_rect = pyqtSignal(int,bool, QRect)
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._flag_show_rect = False
        self._flag_show_text = False
        self._flag_draw_rect = False

        ## 여러개의 문자열 표출
        self.list_text = [ ]  ## (10,10,"test"), (100,100,"test") // x, y, "text"
        self.tag = 0 ## signal_rect 를 어느 이미지에서 보냈는지 확인하기 위한 tag

        self.begin = QPoint()
        self.end = QPoint()

        # self.begin_rect = QPoint()
        # self.end_rect = QPoint()

        # self.disconnect_img = self.load_disconnect_img()

        self.setStyleSheet("color: white; border-style: solid; border-width: 2px; border-color: #54A0FF; background-color: rgb(0,0,0)")
        # self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # width, height = 300,300
        # self.setGeometry(0, 0, width, height)
        # self.setFrameShape(QFrame.Box)
        # self.setLineWidth(3)
        self.pix = QPixmap()
        self.installEventFilter(self)

        self.load_default_img()

        self.init_contextmenu()

    ## popup 메뉴 
    def init_contextmenu(self):
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        act_draw = QAction("poi 설정" , self)
        act_save = QAction("poi 저장" , self)
        act_no_use = QAction("poi 사용안함" , self)

        # action1.setData(self.list_img[i])
        # action2.setData(self.list_img[i])

        act_draw.triggered.connect(self.click_act_draw)
        act_save.triggered.connect(self.click_act_save)
        act_no_use.triggered.connect(self.click_act_no_use)

        self.addAction(act_draw)
        self.addAction(act_save)
        self.addAction(act_no_use)
        
    def click_act_draw(self):
        self.show_ract(True)
        self.draw_ract(True)

    def click_act_save(self):
        # print(f'rect   begin: {self.begin.x()}, {self.begin.y()}  end: {self.end.x()}, {self.end.y()}')
        self.show_ract(False)
        self.draw_ract(False)
        self.signal_rect.emit(self.tag, bool(True), QRect(self.begin, self.end))


    def click_act_no_use(self):
        # print(f'no use...')
        self.begin = QPoint(0, 0)
        self.end = QPoint(400-1, 300-1)
        # print(f'rect   begin: {self.begin.x()}, {self.begin.y()}  end: {self.end.x()}, {self.end.y()}')
        self.signal_rect.emit(self.tag, bool(False), QRect(self.begin, self.end))

    ## popup 메뉴 end



    def send_log(self, msg):
        self.log_signal.emit(msg)

    def load_default_img(self):
        # front_image = '0017.jpg'
        # self.pix = QPixmap(front_image)

        image = np.full(shape=(300, 400, 3), fill_value=100, dtype=np.uint8)
        # self.pix = front_image
        self.pix = self.convert_cv_qt(image)

        self.update()
        
    def paintEvent(self, event):
        if not self.pix.isNull():
            
            # size = self.size()  ## 화면 크기에 맞게
            size = QSize(400,300)  ## 지정된 크기로 
            # print(f"size: {size}")

            painter = QPainter(self)

            point = QPoint(0, 0)
            scaledPix = self.pix.scaled(size, Qt.KeepAspectRatio, transformMode = Qt.FastTransformation) # 비율 고정
            # scaledPix = self.pix.scaled(size, Qt.IgnoreAspectRatio, transformMode=Qt.FastTransformation) # 창 크기에 따라
            painter.drawPixmap(point, scaledPix)

            if self._flag_show_rect:
                br = QBrush(QColor(100, 10, 10, 40))
                painter.setBrush(br)
                painter.drawRect(QRect(self.begin, self.end))
                # print(f'begin: {self.begin.x()}, {self.begin.y()}  end: {self.end.x()}, {self.end.y()}')
                
            if self._flag_show_text:
                painter.setFont(QFont('Times New Roman', 11))
                # painter.drawText(10, 290, self.text_str)

                ## 여러개의 문자 표시
                # print(f'{self.list_text}')
                for i, j in enumerate(self.list_text):
                    painter.drawText(j[0], j[1], j[2])

        else:
            print("pix null")

    ## 마우스 이벤트
    def mousePressEvent(self, event):
        # pass
        if event.button() == Qt.LeftButton:
            # pass
            if self._flag_draw_rect:
                self.begin = event.pos()
                self.end = event.pos()
                self.update()
                # print(f'press {self.begin}, {self.end}')
        
    def mouseMoveEvent(self, event):
        if self._flag_draw_rect:
            self.applye_event(event)
            self.update()
            # print(f'move {event.x()}, {event.y()}')

    def mouseReleaseEvent(self,event):
        if event.button() == Qt.LeftButton:
            if self._flag_draw_rect:
                self.applye_event(event)
                # print(f'Release {event.x()}, {event.y()}')

    def applye_event(self, event):
        self.end = event.pos()

    @pyqtSlot(np.ndarray)
    def changePixmap(self, cv_img):
        # if cv_img is None:
        #     text = f"img is None.............................."
        #     print(f"{text}")

        #     cv_img = self.disconnect_img
            

        self.pix = self.convert_cv_qt(cv_img)

        # print(f'cv_img : {type(cv_img)} {cv_img.shape}, self.pix : {type(self.pix)}')

        self.repaint()

    @pyqtSlot(QRect)
    def receive_rect(self, rect):
        self.begin = rect.topLeft()
        self.end = rect.bottomRight()
        # self.begin = rect.x(), rect.y()
        # self.end = rect.right(), rect.bottom()
        # print(f'receive begin: {rect.x()}, {rect.y()}  end: {rect.right()}, {rect.bottom()}')
        # self.send_log(f'receive begin: {rect.topLeft()}  end: {rect.bottomRight()}')
        # self.update()

    @pyqtSlot(bool)
    def show_ract(self, state):
        self._flag_show_rect = state

    @pyqtSlot(bool)
    def draw_ract(self, state):
        self._flag_draw_rect = state   

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(convert_to_Qt_format)

    def draw_text(self, frame, text, x1, y1):
        cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

class Cont_panel(QWidget):
    signal_start = pyqtSignal()
    signal_play = pyqtSignal()
    signal_stop = pyqtSignal()
    signal_save = pyqtSignal()
    signal_get = pyqtSignal()
    signal_get_default = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._repeat = False

        self.btn_start = QPushButton("start")
        self.btn_play = QPushButton("play")
        self.btn_stop = QPushButton("stop")
        self.btn_save = QPushButton("save")
        self.btn_get = QPushButton("get")

        self.btn_start.clicked.connect(self.clicked_btn_start)
        self.btn_play.clicked.connect(self.clicked_btn_play)
        self.btn_stop.clicked.connect(self.clicked_btn_stop)
        self.btn_save.clicked.connect(self.clicked_btn_save)
        self.btn_get.clicked.connect(self.clicked_btn_get)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.btn_start)
        main_layout.addWidget(self.btn_play)
        main_layout.addWidget(self.btn_stop)
        main_layout.addWidget(self.btn_save)
        main_layout.addWidget(self.btn_get)

        self.setLayout(main_layout)

    

    def clicked_btn_start(self):
        self.signal_start.emit()

    def clicked_btn_play(self):
        self._repeat =True
        self.repeat_get()

    def clicked_btn_stop(self):
        self._repeat =False
        self.signal_get_default.emit()

    def clicked_btn_save(self):
        self.signal_save.emit()

    def clicked_btn_get(self):
        self.signal_get.emit()

    def repeat_get(self):
        print(f"repeat cam read")
        try:
            while self._repeat:
                
                self.signal_get.emit()
                #영상 이미지 갱신 간격
                loop = QEventLoop()
                QTimer.singleShot(25, loop.quit) #25 ms
                loop.exec_()
            print(f"stop cam read")

        except Exception as e:
            # self.send_msg.emit('%s' % e)
            print(f"repeat_get exception : {e}..... break")
            # self._is_cam_open = False



class Win_view(QWidget):
    signal_auto_show = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt live label demo")

        self.init_ui()
        self.setMouseTracking(False)
        self.init_set()
        # self.init_auto_show()
        
        

    def init_ui(self):
        # create the label that holds the image
        self.image_label = ImgLabel()
        self.image_label.setFixedSize(400, 300)
        self.image_label._flag_draw = True

        self.cont_panel = Cont_panel()
        

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label, 1)
        main_layout.addWidget(self.cont_panel)

        self.setLayout(main_layout)
        # self.resize(600,400)


        
    def init_set(self):
        vi = "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/20/media.smp"
        # vi = "rtsp://101.100.3.151/1/stream3"
        # create the video capture thread
        self.thread = VideoThread()
        self.thread.set_vi(vi, vi)
        self.thread.set_img_size(400,300)
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.image_label.changePixmap)

        self.cont_panel.signal_start.connect(self.thread.start)
        # self.cont_panel.signal_play.connect(self.thread.play)
        self.cont_panel.signal_stop.connect(self.thread.stop)
        self.cont_panel.signal_get.connect(self.thread.get_img)
        self.cont_panel.signal_get_default.connect(self.thread.get_img_default)
        # start the thread
        # self.thread.start()

    # def closeEvent(self, event):
    #     self.thread.stop()
    #     event.accept()

    def init_auto_show(self):
        vi = "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/20/media.smp"
        # create the video capture thread
        self.thread = VideoThread()
        self.thread.set_img_size = 400, 300
        # self.thread.set_vi = vi
        self.thread.change_pixmap_signal.connect(self.image_label.changePixmap)
        self.thread.auto_run()


    def closeEvent(self, event):
        quit_msg = "Want to exit?"
        replay = QMessageBox.question(self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No)
        if replay == QMessageBox.Yes:
            self.thread.stop()
            self.cont_panel.clicked_btn_stop()
            event.accept()
        else:
            event.ignore()

 




if __name__=="__main__":
    app = QApplication(sys.argv)
    a = Win_view()
    a.show()
    sys.exit(app.exec())


