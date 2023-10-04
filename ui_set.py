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


class UI_set(QWidget):

    def __init__(self):
        super().__init__()
        
        self.init_ui()
        # self.show()

    def init_ui(self):
        label_open = QLabel("open")
        label_close = QLabel("close")
        label_wh = QLabel("휠체어")
        label_st = QLabel("유모차")
        label_si = QLabel("실버카")
        label_sc = QLabel("스쿠터")

        self.edit_open = QLineEdit()
        self.edit_close = QLineEdit()
        self.edit_wh = QLineEdit()
        self.edit_st = QLineEdit()
        self.edit_si = QLineEdit()
        self.edit_sc = QLineEdit()
         
        hbox = QHBoxLayout()
        hbox.addWidget(label_open)
        hbox.addWidget(self.edit_open)
        hbox.addWidget(label_close)
        hbox.addWidget(self.edit_close)
        hbox.addWidget(label_wh)
        hbox.addWidget(self.edit_wh)
        hbox.addWidget(label_st)
        hbox.addWidget(self.edit_st)
        hbox.addWidget(label_si)
        hbox.addWidget(self.edit_si)
        hbox.addWidget(label_sc)
        hbox.addWidget(self.edit_sc)

        self.setLayout(hbox)

  





if __name__=="__main__":
    app = QApplication(sys.argv)
    ex = UI_set()
    ex.show()
    sys.exit(app.exec_())
    