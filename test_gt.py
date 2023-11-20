import sys
import cv2
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
import torch

# YOLOv5 모델 로드
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
org=(10,280)
font=cv2.FONT_HERSHEY_SIMPLEX

def now_time_str():
    now = time.localtime()
    return time.strftime('%H:%M:%S', now)

def default_img():
    # front_image = '0017.jpg'
    # self.pix = QPixmap(front_image)

    image = np.full(shape=(300, 400, 3), fill_value=100, dtype=np.uint8)

    return image

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.camera_urls = ["rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/22/media.smp",
                    "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/28/media.smp",
                    "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/17/media.smp",
                    "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/25/media.smp"]

        self.set_size = 400, 300
        self.cameras = []
        self.img_label = []
        self.default_img = default_img()

        for id in range(4):
            cap = cv2.VideoCapture(self.camera_urls[id])
            self.cameras.append(cap)
            label = QLabel(self)
            self.img_label.append(label)

        self.central_widget = self.init_img_box()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        
        
            
        
        ##주기적으로 실행 할 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(400)
    
    def init_img_box(self):
        h1 = QHBoxLayout()
        h2 = QHBoxLayout()
        main = QVBoxLayout()

        h1.addWidget(self.img_label[0])
        h1.addWidget(self.img_label[1])
        h2.addWidget(self.img_label[2])
        h2.addWidget(self.img_label[3])

        widget = QWidget(self)
        main.addLayout(h1)
        main.addLayout(h2)
        widget.setLayout(main)

        return widget



    def update_frames(self):
        for i, camera in enumerate(self.cameras):
            ret, frame = camera.read()
            if ret:
                ## 크기변경
                frame = cv2.resize(frame, self.set_size, interpolation=cv2.INTER_AREA)

                # 객체 탐지 수행
                results = model(frame)
                img = results.render()[0]

                text = now_time_str()
                cv2.putText(img,text,org,font,1,(255,0,0),2)
                

            else:
                # print(f'ret : {ret} {i} {self.camera_urls[i]}')
                img = self.default_img
                text = "connect fail"
                cv2.putText(img,text,org,font,1,(255,0,0),2)

            ### 공통 처리되어야 하는 부분
            
            
            # OpenCV BGR 이미지를 PyQt QPixmap으로 변환하여 표시
            height, width, channel = img.shape
            bytesPerLine = 3 * width
            qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.img_label[i].setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())
