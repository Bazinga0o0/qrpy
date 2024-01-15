from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from pyzbar.pyzbar import decode
import cv2
import pyautogui
import time
from mss import mss
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QCursor

class ClickableLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.text = text

    def mousePressEvent(self, event):
        QDesktopServices.openUrl(QUrl(self.text))

app = QApplication([])

class Scanner:
    def __init__(self):
        self.label = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.scan)
        self.timer.start(1000)  # take a screenshot every second
        self.sct = mss()

    def scan(self):
        screenshot = self.sct.grab(self.sct.monitors[0])  # take a screenshot of the entire screen
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGBA2GRAY)
        codes = decode(image)
        if not codes:
            if self.label is not None:
                self.label.close()
        else:
            mouse_pos = QCursor.pos()
            closest_code = min(codes, key=lambda code: (code.polygon[1].x - mouse_pos.x())**2 + (code.polygon[1].y - mouse_pos.y())**2)
            data = closest_code.data.decode('utf-8')
            botP = closest_code.polygon[1]
            if self.label is not None:
                if data == self.label.text and self.label.pos().x() == botP.x and self.label.pos().y() == botP.y:
                    return
                else:
                    self.label.close()
            
            self.label = ClickableLabel(data)
            self.label.setStyleSheet("background-color: transparent; color: red; font-size: 18px;")
            self.label.move(botP.x, botP.y)
            self.label.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
            self.label.show()

scanner = Scanner()  # make scanner global

if __name__ == '__main__':
    app.exec_()