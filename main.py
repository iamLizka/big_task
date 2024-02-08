import sys
import os

import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore


class Prog(QWidget):
    def __init__(self):
        super().__init__()
        self.getImage()
        self.initUI()

    def initUI(self):
        self.setGeometry(700, 300, 900, 550)

        ## Изображение
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(300, 25)
        self.image.resize(600, 500)
        self.image.setPixmap(self.pixmap)

        self.scale = 0.002


    def getImage(self):
        map_request = "http://static-maps.yandex.ru/1.x/?ll=24.952561%2C60.169489&spn=0.002,0.002&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Prog()
    ex.show()
    sys.exit(app.exec_())

