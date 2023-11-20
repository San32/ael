import cv2
import json
import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import numpy as np

from e1214_modbus import *
from cont import *
from common import *
from camera import *

### 카메라에서 읽어오는것만 집중
# class Cam(QThread):

#     def __init__(self):
#         super().__init__()

#         self.cam_url = "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/22/media.smp"
#         self.cap = None
#         self.last_frame = None
#         self._run_flag = False
#         self._show_cv_flag = False
#         self._fps_show_flag = False
#         self.org=(5,280)
#         self.fps_org = (300, 10)
#         self.font=cv2.FONT_HERSHEY_SIMPLEX
#         self.set_size = 400, 300

#         # 카메라 연결 시도 횟수 및 재접속 간격 (초)
#         self.max_reconnect_attempts = 3
#         self.reconnect_interval = 5

#         # self.auto()
    
#     @pyqtSlot()
#     def run_show(self):
#         print(f'run_show...')
#         self._run_flag = True
#         self._show_cv_flag = True
#         self._fps_show_flag = True
#         self.start()

#     @pyqtSlot()
#     def run_only(self):
#         print(f'run_only...')
#         self._run_flag = True
#         self._show_cv_flag = False
#         self._fps_show_flag = False
#         self.start()

#     @pyqtSlot()
#     def stop(self):
#         self._run_flag = False

#     # @pyqtSlot()
#     def get_frame(self):
#         return self.last_frame

#     def run(self):
#         reconnect_count = 0

#         # FPS 계산을 위한 변수 초기화
#         frame_count = 0
#         start_time = time.time()
#         fps = 0

#         while self._run_flag:
#             try:
#                 if self.cap is None:
#                     # 카메라 연결 시도
#                     self.cap = cv2.VideoCapture(self.cam_url)
                
#                 # 영상 읽기
#                 ret, frame = self.cap.read()

#                 if ret:
#                     ## 크기변경
#                     frame = cv2.resize(frame, self.set_size, interpolation=cv2.INTER_AREA)

#                     if self._fps_show_flag:
#                         # 1초마다 FPS를 업데이트하고 출력
#                         frame_count += 1
#                         if time.time() - start_time >= 1:
#                             fps = frame_count / (time.time() - start_time)
#                             print(f"FPS: {fps:.2f}")
#                             frame_count = 0
#                             start_time = time.time()

#                         ## 글자가 깜빡이지 않기 위해 계속 표출해야함.
#                         fps_text = f"FPS: {fps:.2f}"
#                         cv2.putText(frame, fps_text, self.fps_org, self.font, 0.5, (255,0,0),2)
                        

#                     text = "test"
#                     cv2.putText(frame,text, self.org, self.font, 1, (255,0,0),2)


#                     # 영상을 imshow로 보여준다
#                     if self._show_cv_flag:
#                         cv2.imshow("Camera Feed", frame)
#                         if cv2.waitKey(1) & 0xFF == ord('q'):
#                             break

#                     ## 마지막 이미지만 저장해둠
#                     self.last_frame = frame

#                 else:
#                     # 연결이 끊어진 경우 재접속 시도
#                     reconnect_count += 1
#                     if reconnect_count >= self.max_reconnect_attempts:
#                         print("최대 재접속 시도 횟수를 초과했습니다.")
#                         break
#                     print("연결 끊김. 재접속 시도 중...")
#                     self.cap.release()
#                     cv2.destroyAllWindows()
#                     self.cap = None
#                     cv2.waitKey(self.reconnect_interval * 1000)
#             except KeyboardInterrupt:
#                 break

#         # 프로그램 종료 시 정리
#         if self.cap is not None:
#             self.cap.release()
#         cv2.destroyAllWindows()


# class ImgLabel(QLabel):
#     # ResizeSignal = pyqtSignal(int)
#     signal_rect = pyqtSignal(int, QRect)
#     log_signal = pyqtSignal(str)

#     def __init__(self):
#         super().__init__()

#         self._flag_show_rect = False
#         self._flag_show_text = False
#         self._flag_draw_rect = False

#         self.text_str = "text"
#         self.tag = 0 ## signal_rect 를 어느 이미지에서 보냈는지 확인하기 위한 tag

#         self.begin = QPoint()
#         self.end = QPoint()

#         # self.begin_rect = QPoint()
#         # self.end_rect = QPoint()

#         # self.disconnect_img = self.load_disconnect_img()

#         self.setStyleSheet("color: white; border-style: solid; border-width: 2px; border-color: #54A0FF; background-color: rgb(0,0,0)")
#         # self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
#         # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         # width, height = 300,300
#         # self.setGeometry(0, 0, width, height)
#         # self.setFrameShape(QFrame.Box)
#         # self.setLineWidth(3)
#         self.pix = QPixmap()
#         self.installEventFilter(self)

#         self.load_default_img()

#         self.init_contextmenu()

#     ## popup 메뉴 
#     def init_contextmenu(self):
#         self.setContextMenuPolicy(Qt.ActionsContextMenu)

#         act_draw = QAction("poi 설정" , self)
#         act_save = QAction("poi 저장" , self)
#         act_no_use = QAction("poi 사용안함" , self)

#         # action1.setData(self.list_img[i])
#         # action2.setData(self.list_img[i])

#         act_draw.triggered.connect(self.click_act_draw)
#         act_save.triggered.connect(self.click_act_save)
#         act_no_use.triggered.connect(self.click_act_no_use)

#         self.addAction(act_draw)
#         self.addAction(act_save)
#         self.addAction(act_no_use)
        
#     def click_act_draw(self):
#         self.show_ract(True)
#         self.draw_ract(True)

#     def click_act_save(self):
#         # print(f'rect   begin: {self.begin.x()}, {self.begin.y()}  end: {self.end.x()}, {self.end.y()}')
#         self.show_ract(False)
#         self.draw_ract(False)
#         self.signal_rect.emit(self.tag, QRect(self.begin, self.end))


#     def click_act_no_use(self):
#         # print(f'no use...')
#         self.begin = QPoint(0, 0)
#         self.end = QPoint(400-1, 300-1)
#         # print(f'rect   begin: {self.begin.x()}, {self.begin.y()}  end: {self.end.x()}, {self.end.y()}')
#         self.signal_rect.emit(self.tag, QRect(self.begin, self.end))

#     ## popup 메뉴 end



#     def send_log(self, msg):
#         self.log_signal.emit(msg)

#     def load_default_img(self):
#         # front_image = '0017.jpg'
#         # self.pix = QPixmap(front_image)

#         image = np.full(shape=(300, 400, 3), fill_value=100, dtype=np.uint8)
#         # self.pix = front_image
#         self.pix = self.convert_cv_qt(image)

#         self.update()
        
#     def paintEvent(self, event):
#         if not self.pix.isNull():
            
#             # size = self.size()  ## 화면 크기에 맞게
#             size = QSize(400,300)  ## 지정된 크기로 
#             # print(f"size: {size}")

#             painter = QPainter(self)

#             point = QPoint(0, 0)
#             scaledPix = self.pix.scaled(size, Qt.KeepAspectRatio, transformMode = Qt.FastTransformation) # 비율 고정
#             # scaledPix = self.pix.scaled(size, Qt.IgnoreAspectRatio, transformMode=Qt.FastTransformation) # 창 크기에 따라
#             painter.drawPixmap(point, scaledPix)

#             if self._flag_show_rect:
#                 br = QBrush(QColor(100, 10, 10, 40))
#                 painter.setBrush(br)
#                 painter.drawRect(QRect(self.begin, self.end))
#                 # print(f'begin: {self.begin.x()}, {self.begin.y()}  end: {self.end.x()}, {self.end.y()}')
                
#             if self._flag_show_text:
#                 painter.setFont(QFont('Times New Roman', 11))
#                 painter.drawText(10, 290, self.text_str)
#         else:
#             print("pix null")

#     ## 마우스 이벤트
#     def mousePressEvent(self, event):
#         # pass
#         if event.button() == Qt.LeftButton:
#             # pass
#             if self._flag_draw_rect:
#                 self.begin = event.pos()
#                 self.end = event.pos()
#                 self.update()
#                 # print(f'press {self.begin}, {self.end}')
        
#     def mouseMoveEvent(self, event):
#         if self._flag_draw_rect:
#             self.applye_event(event)
#             self.update()
#             # print(f'move {event.x()}, {event.y()}')

#     def mouseReleaseEvent(self,event):
#         if event.button() == Qt.LeftButton:
#             if self._flag_draw_rect:
#                 self.applye_event(event)
#                 # print(f'Release {event.x()}, {event.y()}')

#     def applye_event(self, event):
#         self.end = event.pos()

#     @pyqtSlot(np.ndarray)
#     def changePixmap(self, cv_img):
#         # print(f'{type(cv_img)}')
#         # if cv_img is None:
#         #     text = f"img is None.............................."
#         #     print(f"{text}")

#         #     cv_img = self.disconnect_img
            

#         self.pix = self.convert_cv_qt(cv_img)

#         # print(f'cv_img : {type(cv_img)} {cv_img.shape}, self.pix : {type(self.pix)}')

#         self.repaint()

#     @pyqtSlot(QRect)
#     def receive_rect(self, rect):
#         self.begin = rect.topLeft()
#         self.end = rect.bottomRight()
#         # self.begin = rect.x(), rect.y()
#         # self.end = rect.right(), rect.bottom()
#         # print(f'receive begin: {rect.x()}, {rect.y()}  end: {rect.right()}, {rect.bottom()}')
#         # self.send_log(f'receive begin: {rect.topLeft()}  end: {rect.bottomRight()}')
#         # self.update()

#     @pyqtSlot(bool)
#     def show_ract(self, state):
#         self._flag_show_rect = state

#     @pyqtSlot(bool)
#     def draw_ract(self, state):
#         self._flag_draw_rect = state   

#     def convert_cv_qt(self, cv_img):
#         """Convert from an opencv image to QPixmap"""
#         rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
#         h, w, ch = rgb_image.shape
#         bytes_per_line = ch * w
#         convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
#         # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
#         return QPixmap.fromImage(convert_to_Qt_format)

#     def draw_text(self, frame, text, x1, y1):
#         cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)


class Win(QMainWindow):
    # signal_cam
    def __init__(self):
        super().__init__()
        self.init_set()
        self.init_ui()
        self.init_signal()
        self.show()
        # self.auto_run()


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


    def init_set(self):
        self.data = read_config(path_config)

        self.list_img = []
        self.list_cont = []
        

        self.list_cam = []
        self.list_cam_stat = [0,0,0,0]
        self.list_url = [self.data['up']['cam1']['cam']['url'], self.data['up']['cam2']['cam']['url'], self.data['dn']['cam1']['cam']['url'], self.data['dn']['cam2']['cam']['url']]
        # self.list_img = [self.ui_autoel.up_floor.img_cam1, self.ui_autoel.up_floor.img_cam2, self.ui_autoel.dn_floor.img_cam1, self.ui_autoel.dn_floor.img_cam2]
        self.list_name = ["up cam1", "up cam2", "down cam1", "down cam2"]
        self.list_detect = [self.data['up']['cam1'].get('detect'), self.data['up']['cam2'].get('detect'), self.data['dn']['cam1'].get('detect'), self.data['dn']['cam2'].get('detect')]
        # self.list_cont = [self.ui_autoel.up_floor.edit_cont, self.ui_autoel.up_floor.edit_cont, self.ui_autoel.dn_floor.edit_cont, self.ui_autoel.dn_floor.edit_cont]
        self.list_poi = [self.data['up']['cam1'].get('poi'), self.data['up']['cam2'].get('poi'), self.data['dn']['cam1'].get('poi'), self.data['dn']['cam2'].get('poi')]
        self.list_io = [self.data['up'].get('io'), self.data['up'].get('io'), self.data['dn'].get('io'), self.data['dn'].get('io')]

    def init_ui(self):
        self.setWindowTitle("자동호출 시스템    Ver 3.2")

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
        for id in range(4):
            cam = VideoThread()
            # cam.set_vi(self.list_url[id], self.list_name[id])
            cam.set_init(self.list_url[id], self.list_name[id], id, 400, 300)
            # cam.set_img_size(400, 300)
            self.list_cam.append(cam)

            label = ImgLabel()
            label._flag_show_text = True
            label.tag = int(id)
            label.setFixedSize(400, 300)
            # label.setStyleSheet("color: white; border-style: solid; border-width: 2px; border-color: #54A0FF; background-color: rgb(0,0,0)")
            self.list_img.append(label)

        self.cont1 = Cont()
        self.cont2 = Cont()

        self.cont1.init_io(self.data['up']['io'])
        self.cont2.init_io(self.data['dn']['io'])



        h1 = QHBoxLayout()
        h2 = QHBoxLayout()
        main = QVBoxLayout()

        h1.addWidget(self.list_img[0])
        h1.addWidget(self.list_img[1])
        h1.addWidget(self.cont1)
        h2.addWidget(self.list_img[2])
        h2.addWidget(self.list_img[3])
        h2.addWidget(self.cont2)

        widget = QWidget(self)
        main.addLayout(h1)
        main.addLayout(h2)
        widget.setLayout(main)

        return widget

    def init_cam(self, no):
        pass

    def init_signal(self):
        for i in range(4):
            self.list_img[i].signal_rect.connect(self.receive_rect)
            self.list_cam[i].change_state_signal.connect(self.receive_state)
    
    def auto_run(self):
        for id in range(4):
            self.list_cam[id].start()
        

        self.init_timer(1000)
        self.timer_repeat.start()
        pass

    ## 반복수행 타이머
    def init_timer(self, repeat_time):
        
        self.timer_repeat = QTimer()
        self.timer_repeat.setInterval(repeat_time)
        # self.tm.timeout.connect(self.time_process)
        self.timer_repeat.timeout.connect(self.repeat_process)


    def repeat_process(self):
        for id in range(4):
            ## CAM_STAT = ("RUN_FAIL", "RUN_OK", "READ_FAIL", "READ_OK")
            if self.list_cam_stat[id] == "READ_OK":

                img, fps = self.list_cam[id].get_img()
                # self.list_img[id].
                fps_text = (10, 10, str(fps))
                stat_text = (10, 40, str(self.list_cam_stat[id]))
                list_text = [fps_text, stat_text]
                self.list_img[id].list_text = list_text
                self.list_img[id].changePixmap(img)
            elif self.list_cam_stat[id] == "RUN_FAIL":
                pass



        # print(f'{now_time_str()}')

        # for i, url in enumerate(self.list_url):
        #     print(f"{i} {url}")

    @pyqtSlot(int, str)
    def receive_state(self, tag, stat):
        # print(f'receive state : {tag}, {stat} ')
        self.list_cam_stat[tag] = f'[{now_time_str()}] {stat}'
        # print(f'[{now_time_str()}] self.list_cam_stat : {self.list_cam_stat}')

    @pyqtSlot(int, QRect)
    def receive_rect(self, tag, rect):
        print(f'[{now_time_str()}] rect receive : {tag}  {rect} {rect.left()} {rect.top()} {rect.width()} {rect.height()}')
        # print(f'{self.list_poi[tag]}')

        self.list_poi[tag]['x'] = str(rect.left())
        self.list_poi[tag]['y'] = str(rect.top())
        self.list_poi[tag]['e_x'] = str(rect.width())
        self.list_poi[tag]['e_y'] = str(rect.height())

        print(f'{self.list_poi[tag]}')
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
