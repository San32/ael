import json
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import time
from e1214_modbus import *
from pyModbusTCP.client import ModbusClient

from common import *

"""
"io": {
			"value_io_ip": "10.128.17.49",
			"value_io_relay_port": "0",
			"value_io_delay_time": "10"
		}
"""

class Cont(QTextEdit):
    def __init__(self):
        super().__init__()

        self.io = None

        self.door_open = False
        self.called = False

        self.last_open_time = time.time()
        self.last_close_time = time.time()
        self.last_detect_time = time.time()
        self.last_call_time = time.time()


    def init_io(self, data):
        self.io_ip = data['value_io_ip']
        self.io_port = 502
        self.io_relay_port = int(data['value_io_relay_port'])
        self.io_delay_time = int(data['value_io_delay_time'])
        self.io = E1214(self.io_ip, self.io_port)
        # self.io = E1214(self.ip, self.port)

        # self.e1214 = ModbusClient(host=self.io_ip, port=self.io_port, unit_id=1, auto_open=True)

        arr_relay = [0, 0, 0, 0, 0, 0]
        self.io.e1214.write_multiple_coils(0, arr_relay)

    def append_log(self, str):
        self.append(f'[{self.now_time_str()}] {str}')

    @pyqtSlot(str)
    def receive_log(self, msg):
        self.append(f'r: {msg}')

    def receive_data(self, name, dict):
        # print(f'{dict}')
        # self.append(f'[{name}] {dict}')
        if "door_open" in dict:
            self.receive_open()
        elif "door_close" in dict:
            self.receive_close()
        elif "wheelchair" in dict:
            self.check_process(name, dict)
        elif "stroller" in dict:
            self.check_process(name, dict)
        elif "silvercar" in dict:
            self.check_process(name, dict)
        elif "scuter" in dict:
            self.check_process(name, dict)

    def receive_open(self):
        if self.door_open == False:
            self.append_log(f'open')
            self.last_open_time = time.time()
            self.door_open = True
            self.called = False

    def receive_close(self):

        if self.door_open == True:
            self.append_log(f'close')
            self.last_close_time = time.time()

            self.door_open = False

    def push_call(self):
        # self.append_log(f'push call // Relay:{self.io_relay_port} ')

        if self.io.push_call(self.io_relay_port):
            self.append_log(f'EL call(R{self.io_relay_port}) OK!')
        else:
            self.append_log(f'EL call(R{self.io_relay_port}) failed')
        

        # ret = self.e1214.write_single_coil(self.io_relay_port, 1)
        # print(f'e1214.write_single_coil close : {ret}')
        # QTest.qWait(400)
        
        # ret =self.e1214.write_single_coil(self.io_relay_port, 0)
        # print(f'e1214.write_single_coil open : {ret}')
        # self.last_call_time = time.time()
        # pass

    def now_time_str(self):
        now = time.localtime()
        return time.strftime('%H:%M:%S', now)

    """
    detect시 문이 단혀있으면 호출했었는지 확인하여 처리
    한번 호출후 3초후 재 호출, EL 출발시간 기다린다
    """

    def check_process(self, name, dict):  # 사물이 인식 되었으면
        self.append_log(f'[{name}] {dict}')
        if self.door_open == True:  # 문이 열려있으면 넘어감
            # print("detect : door_open == True  $$$$$$$   pass")
            pass

        elif self.called == True:  # 문이 닫혀있고, 호출을 하였으면 넘어감
            # print("detect : called == True     $$$$$$$   pass")
            pass

        else:  # 단혀있고, 호출한적이 없으면 호출한다.
            gap = time.time() - self.last_close_time
            if gap > self.io_delay_time:  # 한번 호출후 딜레이 시간 후 재 호출, EL 출발시간 기다린다
                
                # self.append(f"대기시간 :{'%0d' %gap}")
                self.push_call()
                self.called = True

            else: 
                self.append_log(f"문 닫힘 후 {self.io_delay_time}초 미만")

class Panel_cont_btn(QWidget):
    def __init__(self, cont):
        super().__init__()
        self.cont = cont

        self.init_ui()
    
    def init_ui(self):

        btn_layout = QVBoxLayout()

        self.btn_wheelchair = QPushButton("wheelchair")
        self.btn_stroller = QPushButton("stroller")
        self.btn_silvercar = QPushButton("silvercar")
        self.btn_scuter = QPushButton("scuter")
        self.btn_door_open = QPushButton("door_open")
        self.btn_door_close = QPushButton("door_close")

        self.btn_io_R1 = QPushButton("push call")

        self.btn_wheelchair.clicked.connect(self.detect_wheelchair)
        self.btn_stroller.clicked.connect(self.detect_stroller)
        self.btn_silvercar.clicked.connect(self.detect_silvercar)
        self.btn_scuter.clicked.connect(self.detect_scuter)
        self.btn_door_open.clicked.connect(self.open)
        self.btn_door_close.clicked.connect(self.close)
        self.btn_io_R1.clicked.connect(self.click_io_R1)

        btn_layout.addWidget(self.btn_wheelchair)
        btn_layout.addWidget(self.btn_stroller)
        btn_layout.addWidget(self.btn_silvercar)
        btn_layout.addWidget(self.btn_scuter)
        btn_layout.addWidget(self.btn_door_open)
        btn_layout.addWidget(self.btn_door_close)
        btn_layout.addWidget(self.btn_io_R1)

        self.setLayout(btn_layout)

    def detect_wheelchair(self):
        dict = {"wheelchair": 0.9}
        self.cont.receive_data("Test", dict)

    def detect_stroller(self):
        dict = {"stroller": 0.9}
        self.cont.receive_data("Test",dict)

    def detect_silvercar(self):
        dict = {"silvercar": 0.9}
        self.cont.receive_data("Test",dict)

    def detect_scuter(self):
        dict = {"scuter": 0.9}
        self.cont.receive_data("Test",dict)

    def open(self):
        dict = {"door_open":0.9}
        self.cont.receive_data("Test",dict)

    def close(self):
        dict = {"door_close":0.9}
        self.cont.receive_data("Test",dict)

    def click_io_R1(self):
        self.cont.push_call()




class Gui(QWidget):

    def __init__(self):
        super().__init__()

        self.init_ui()
        self.init_param()
        

    def init_ui(self):
        main_layout = QHBoxLayout()
        
        self.read_config()

        self.cont = Cont()
        self.init_param()

        

        self.panel_btn = Panel_cont_btn(self.cont)

        main_layout.addWidget(self.cont)
        main_layout.addWidget(self.panel_btn)

        self.setLayout(main_layout)

    def init_param(self):
        self.cont.init_io(self.data['up']['io'])

    def read_config(self):
        self.data = read_config(path_config)
   

    
    
    



if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = Gui()
    gui.show()
    sys.exit(app.exec_())
