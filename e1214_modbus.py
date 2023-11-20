import time
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *

from pyModbusTCP.client import ModbusClient

# TCP auto connect on first modbus request
# e1214 = ModbusClient(host="10.128.17.49", port=502, unit_id=1, auto_open=True)

# TCP auto connect on modbus request, close after it
# c = ModbusClient(host="10.128.17.49", auto_open=True, auto_close=True)


"""
DI port  0,  1,  2,  3,  4,   5
reg     [1] [2] [4] [8] [16] [32]
"""

def get_time():
    current_time = QTime.currentTime()
    text_time = current_time.toString("hh:mm:ss")
    # time_msg = "현재시간: " + text_time
    return text_time


# 제어를 위한 GUI
class E1214(QWidget):
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port

        self.e1214 = ModbusClient(host=self.ip, port=self.port, unit_id=1, auto_open=True)
        self.e1214.open()
        # self.init_ui()
        # self.init_zero_relay()

    

    def init_zero_relay(self):
        self.set_relay_multi([0, 0, 0, 0, 0, 0])

    def set_relay_multi(self, arr_relay):
        ret = self.e1214.write_multiple_coils(0, arr_relay)
        print(f"write_multiple_coils : {ret}")

    # def read_relay():

    @pyqtSlot(int)
    def relay_close(self, r_no):
        ret = self.e1214.write_single_coil(r_no, 1)
        # print(f"relay_close : {ret}")
        return ret
        


    @pyqtSlot(int)
    def relay_open(self, r_no):
        ret = self.e1214.write_single_coil(r_no, 0)
        # print(f"relay_open : {ret}")
        return ret

    @pyqtSlot(int)
    def push_call(self, no):
        # btn_name = sending_button.text()
        # print(f'{sending_button.text()}이 선택되었습니다!')
        # print(f'{sending_button.objectName()}이 선택되었습니다!')

        count = 0
        fail = False  # on의 실패 여부 판단
        while True:
            if self.e1214.write_single_coil(no, 1): # close
                QTest.qWait(100)
                break
            else:
                count = count +1
                if count > 5:
                    fail = True # on 실행 실패
                    break

        if fail == True:
            return False
        else:
            # count = 0
            while True:
                if self.e1214.write_single_coil(no, 0): #open
                    return True
                    break


    @pyqtSlot()
    def read_relay(self):
        # print(f'self.e1214.is_open : {self.e1214.is_open}')
        if self.e1214.is_open:
            try:
                regs = self.e1214.read_coils(0, 6)
                # print(f'{regs}, {type(regs)}, {len(regs)}')
                return regs
            except:
                return None
        else:
            print(f'self.e1214.is_open : {self.e1214.is_open}')


    @pyqtSlot()
    def read_di(self):
        if self.e1214.is_open:
            try:
                # regs = self.e1214.read_input_registers(0x30, 1)
                di_regs = self.e1214.read_input_registers(0x30, 1)  
                
                # print(f'{di_regs}, {type(di_regs)}, {len(di_regs)}')
                binary_num = bin(di_regs[0])[2:]
                flip_binary = binary_num[::-1]
                # print(flip_binary)
                # return flip_binary

                st_bool = []

                if di_regs[0] == 0:
                    st_bool = [False, False, False, False, False, False]
                else:
                    for ss in flip_binary:
                        if ss == '1':
                            st_bool.append(True)
                        else :
                            st_bool.append(False)

                # print(st_bool)
                return st_bool
            except:
                return None
        else:
            print(f'self.e1214.is_open : {self.e1214.is_open}')

    @pyqtSlot()
    def read_start(self):
        relay_regs = self.e1214.read_coils(0, 6)
        # print(f'{regs}, {type(regs)}, {len(regs)}')
 
        di_regs = self.e1214.read_input_registers(0x30, 1)  
        # print(f'{regs}, {type(regs)}, {len(regs)}')
        binary_num = bin(di_regs[0])[2:]
        flip_binary = binary_num[::-1]
        # print(flip_binary)
        # return flip_binary

        st_bool = []

        if di_regs[0] == 0:
            st_bool = [False, False, False, False, False, False]
        else:
            for ss in flip_binary:
                if ss == '1':
                    st_bool.append(True)
                else :
                    st_bool.append(False)

        return relay_regs, st_bool


class R_Button(QPushButton):
    """
    QPushButton 은 QWidget을 상속받고 있으므로 단일 창으로 표출 가능
    """
    def __init__(self, title):
        QPushButton.__init__(self, title)
        self.setFixedSize(100, 30)
        # self.setStyleSheet("background-color: green")

        self.setCheckable(True)
        self.toggled.connect(self.slot_toggle)
        self.slot_toggle(False)

    @pyqtSlot(bool)
    def slot_toggle(self, state):
        """
        toggle 상태에 따라 배경색과 상태 텍스트 변환
        """
        self.setStyleSheet("background-color: %s" % ({True: "red", False: "green"}[state]))
        self.setText({True: "Close", False: "Open"}[state])


class DI_Label(QLabel):
    """
    QPushButton 은 QWidget을 상속받고 있으므로 단일 창으로 표출 가능
    """
    di_input = ["color:blue; background-color:red;", "input"]
    di_none =  ["color:blue; background-color:green;", "none"]

    def __init__(self, title):
        QLabel.__init__(self, title)
        # self.setFixedSize(100, 30)
        self.setAlignment(Qt.AlignCenter)
        self.set_state(False)

    @pyqtSlot(bool)
    def set_state(self, state):
        """
        toggle 상태에 따라 배경색과 상태 텍스트 변환
        """
        self.setStyleSheet({True: self.di_input[0], False: self.di_none[0]}[state])
        self.setText({True: self.di_input[1], False: self.di_none[1]}[state])

        
class R_Label(QLabel):
    """
    QPushButton 은 QWidget을 상속받고 있으므로 단일 창으로 표출 가능
    """
    r_close = ["color:blue; background-color:red;", "Close"]
    r_open =  ["color:blue; background-color:green;", "Open"]

    def __init__(self, title):
        QLabel.__init__(self, title)
        # self.setFixedSize(100, 30)
        self.setAlignment(Qt.AlignCenter)
        self.set_state(False)

    @pyqtSlot(bool)
    def set_state(self, state):
        """
        toggle 상태에 따라 배경색과 상태 텍스트 변환
        """
        self.setStyleSheet({True: self.r_close[0], False: self.r_open[0]}[state])
        self.setText({True: self.r_close[1], False: self.r_open[1]}[state])


class Win_io(QWidget):
    def __init__(self, ip, port):
        super().__init__()

        self.ip = ip
        self.port = port
        self.io = E1214(self.ip, self.port)

        self.label_style = "color: white; border-style: solid; border-color: #54A0FF; background-color: rgb(0,0,0)"

        
        self.init_ui()
        self.title = f"I/O 제어기 {self.ip}"
        self.setWindowTitle(f"{self.title}") ## 연결상태를 뒤에 붙여서 표시

        # self.show()
        self.init_timer()  ##주기적으로 상태 업데이트

        

    def init_timer(self):
        self.timer = QTimer()
        self.timer.start(100)
        # self.timer.timeout.connect(self.clicked_r_read)
        # self.timer.timeout.connect(self.clicked_read_all)
        self.timer.timeout.connect(self.time_repeate)


    def init_cont(self):
    # def init_ui(self):
        relay_label = ["Relay 0", "Relay 1", "Relay 2", "Relay 3", "Relay 4", "Relay 5"]
        self.list_grb = []

        cont_layout = QHBoxLayout()

        label = QLabel("Relay 제어")
        label.setStyleSheet(self.label_style)
        label.setMinimumSize(100, 100)
        label.setAlignment(Qt.AlignCenter)
        cont_layout.addWidget(label)

        for i in range(6):
           grp = QGroupBox(relay_label[i])
           rb_open = QRadioButton("open")
        #    rb_open.setObjectName("open")
           rb_close = QRadioButton("close")
        #    rb_close.setObjectName("close")
           rb_open.setChecked(True)
           grp_layout = QBoxLayout(QBoxLayout.TopToBottom, self)
           grp.setLayout(grp_layout)
           grp_layout.addWidget(rb_open)
           grp_layout.addWidget(rb_close)
           self.list_grb.append(grp)
           cont_layout.addWidget(grp)
        
        btn = QPushButton("전송")
        btn.setMinimumSize(100, 100)
        btn.clicked.connect(self.clicked_btn_send)
        cont_layout.addWidget(btn)

        return cont_layout

    def init_cont_btn(self):
    # def init_ui(self):
        relay_label = ["Relay 0", "Relay 1", "Relay 2", "Relay 3", "Relay 4", "Relay 5"]
        self.list_grb = []

        cont_layout = QHBoxLayout()

        label = QLabel("E/L 호출")
        label.setStyleSheet(self.label_style)
        label.setMinimumSize(100, 100)
        label.setAlignment(Qt.AlignCenter)
        cont_layout.addWidget(label)

        for i in range(6):
           grp = QGroupBox(relay_label[i])
           rb_open = QRadioButton("open")
        #    rb_open.setObjectName("open")
           rb_close = QRadioButton("close")
        #    rb_close.setObjectName("close")
           rb_open.setChecked(True)
           grp_layout = QBoxLayout(QBoxLayout.TopToBottom, self)
           grp.setLayout(grp_layout)
           grp_layout.addWidget(rb_open)
           grp_layout.addWidget(rb_close)
           self.list_grb.append(grp)
           cont_layout.addWidget(grp)
        
        btn = QPushButton("전송")
        btn.setMinimumSize(100, 100)
        btn.clicked.connect(self.clicked_btn_send)
        cont_layout.addWidget(btn)

        return cont_layout

    def clicked_btn_send(self):
        res = []
        for i in range(len(self.list_grb)):
            for rb in self.list_grb[i].findChildren(QRadioButton):
                # print(f'{type(rb)}')
                if rb.isChecked():
                    if rb.text() == "close":
                        res.append(1)
                    else:
                        res.append(0)

        print(f'sned : {res}, {get_time}')


        # self.io.init_zero_relay()
        if len(res) == 6:
            self.io.set_relay_multi(res)
        else:
            print(f"ERROR : set_relay")

        # self.clicked_read_all()

    def init_ui(self):
        self.list_di = []
        self.list_r = []
        self.list_call = []
        
        port_label = ["PORT 0", "PORT 1", "PORT 2", "PORT 3", "PORT 4", "PORT 5"]
        di_label = ["None", "None", "None", "None", "None", "None"]
        relay_label = ["open", "open", "open", "open", "open", "open"]

        
        
        #타이틀
        box_label = QHBoxLayout()
        label = QLabel("구분")
        label.setStyleSheet(self.label_style)
        label.setMinimumSize(100, 30)
        label.setAlignment(Qt.AlignCenter)
        box_label.addWidget(label)
        for i in range(6):
            label = QLabel(port_label[i])
            # label.setStyleSheet(self.unset)
            label.setMinimumSize(100, 30)
            label.setAlignment(Qt.AlignCenter)
            # self.list_di.append(label)
            box_label.addWidget(label)
        
        #DI
        box_di = QHBoxLayout()
        label = QLabel("DI 상태")
        label.setStyleSheet(self.label_style)
        label.setMinimumSize(100, 30)
        label.setAlignment(Qt.AlignCenter)
        box_di.addWidget(label)
        for i in range(6):
            label = DI_Label(di_label[i])
            label.setMinimumSize(100, 30)
            self.list_di.append(label)
            box_di.addWidget(label)

        ##### Relay box
        box_R = QHBoxLayout()
        label = QLabel("Relay 상태")
        label.setStyleSheet(self.label_style)
        label.setMinimumSize(100, 30)
        label.setAlignment(Qt.AlignCenter)
        box_R.addWidget(label)
        for i in range(6):
            btn = R_Label(relay_label[i])
            btn.setObjectName(str(i))
            # btn.clicked.connect(self.clicked_r_btn)
            self.list_r.append(btn)
            box_R.addWidget(btn)

        ##### push Relay 
        box_call = QHBoxLayout()
        label = QLabel("Push Call")
        label.setStyleSheet(self.label_style)
        label.setMinimumSize(100, 30)
        label.setAlignment(Qt.AlignCenter)
        box_call.addWidget(label)
        for i in range(6):
            btn = QPushButton(str(i))
            btn.setObjectName(str(i))
            btn.clicked.connect(self.clicked_call_btn)
            self.list_call.append(btn)
            box_call.addWidget(btn)

 
        box_main = QVBoxLayout()
        box_main.addLayout(box_label)
        box_main.addLayout(box_di)
        box_main.addLayout(box_R)
        box_main.addLayout(box_call)

        self.setLayout(box_main)

    def clicked_call_btn(self):
        sending_button = self.sender()
        self.io.push_call(int(sending_button.objectName()))

    
                

    def clicked_di_read(self):
        st_di = self.io.read_di()
        if st_di != None:
            # print(f'st: {st} {type(st)}')
            for i in range(len(st_di)):
                self.list_di[i].set_state(st_di[i])
       


    def clicked_r_read(self):
        st_r = self.io.read_relay()
        # print(type(st), len(st), st)
        for i in range(len(st_r)):
            # print(st[i])
            self.list_r[i].set_state(st_r[i])

    def time_repeate(self):
        # self.io.e1214.open()
        if self.io.e1214.is_open:
            self.setWindowTitle(f"{self.title}  connected")
            # print("open")
            self.clicked_read_all()
        else:
            # print("not open -> open")
            self.setWindowTitle(f"{self.title}  connection failed")
            self.io.e1214.open()



    def clicked_read_all(self):
        
        # # st_r, st_di = self.io.read_start()
        st_r = self.io.read_relay()
        st_di = self.io.read_di()
        # # print(f'read_all {st_di}, {st_r}')


        # for i in range(len(st_di)):
        #     self.list_di[i].set_state(st_di[i])

        # for i in range(len(st_r)):
        #     self.list_r[i].set_state(st_r[i])

        # # print(get_time)

        if st_r != None:
            for i in range(len(st_r)):
                self.list_r[i].set_state(st_r[i])
        else:
            print("Relay read error")

        if st_di != None:
            for i in range(len(st_di)):
                self.list_di[i].set_state(st_di[i])
        else:
            print("DI read error")





if __name__ == "__main__":
    app = QApplication(sys.argv)

    ip = "10.128.17.49"
    port = 502
    
    a = Win_io(ip, port)
        
    # a = ContPanel()
    a.show()
    sys.exit(app.exec_())
