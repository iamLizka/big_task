import sys
import os

import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore


class Prog(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(700, 300, 900, 550)

        self.lon = "44.913507"
        self.lat = "53.224134"
        self.scale = 0.002

        self.image = QLabel(self)
        self.image.move(300, 25)
        self.image.resize(600, 500)

        self.getImage()
        self.show_map()

    def show_map(self):
        ## Изображение
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def getImage(self):
        api_server = "http://static-maps.yandex.ru/1.x/"

        params = {
            "ll": ",".join([self.lon, self.lat]),
            "spn": ",".join([str(self.scale), str(self.scale)]),
            "l": "map"
        }
        response = requests.get(api_server, params=params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_PageDown:
            self.scale += 0.001 if self.scale <= 50 else 50
        elif event.key() == QtCore.Qt.Key_PageUp:
            self.scale -= 0.001 if self.scale != 0.0 else 0.0
        self.getImage()
        self.show_map()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Prog()
    ex.show()
    sys.exit(app.exec_())

