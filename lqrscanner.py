from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QDesktopServices, QCursor
from pyzbar.pyzbar import decode
import cv2
from mss import mss
import numpy as np

class ClickableLabel(QLabel):
    def __init__(self, text, parent=None):
        super(ClickableLabel, self).__init__(text, parent)
        self.text = text
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        QDesktopServices.openUrl(QUrl(self.text))
        self.close()
        scanner.scan()

app = QApplication([])

class Scanner:
    def __init__(self):
        self.label = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.scan)
        self.timer.start(500)
        self.sct = mss()
        self.no_codes_counter = 0
        

    def scan(self):
        screenshot = self.sct.grab(self.sct.monitors[0])
        
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGBA2GRAY)
        try:
            codes = decode(image)
        except:
            codes = None
        if not codes:
            self.no_codes_counter += 1
            if self.no_codes_counter >= 6:
                self.timer.start(2000)
            if self.label is not None:
                self.label.close()
        else:
            self.no_codes_counter = 0
            self.timer.start(300)
            mouse_pos = QCursor.pos()
            closest_code = min(codes, key=lambda code: (code.polygon[1].x - mouse_pos.x())**2 + (code.polygon[1].y - mouse_pos.y())**2)
            data = closest_code.data.decode('utf-8')
            botP = closest_code.polygon[0]
            height = closest_code.rect.height
            gap = 10
            if self.label is not None:
                if data != self.label.text or self.label.pos().x() != botP.x or self.label.pos().y() != botP.y + height + gap:
                    self.label.close()
                    self.create_label(data, botP, height, gap)
            else:
                self.create_label(data, botP, height, gap)

    def create_label(self, data, botP, height, gap):
        self.label = ClickableLabel(data)
        self.label.setStyleSheet("background-color: rgba(128, 128, 128, 128); color: white; font-size: 18px;")
        self.label.move(botP.x, botP.y + height + gap)
        self.label.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.label.show()

scanner = Scanner()

if __name__ == '__main__':
    app.exec_()