import sys
import os

import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5 import QtCore


# создаю класс для QComboBox, переопределяя метод для обработки событий клавиатуры,
# чтобы при нажатии стрелочек на клавиатуре значение ComboBox не менялось
class CustomComboBox(QComboBox):
    def keyPressEvent(self, event: QKeyEvent):
        event.ignore()


class Prog(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(700, 300, 800, 450)

        self.lon = 44.915441
        self.lat = 53.224134
        self.scale = 0.002
        self.map = "map"

        self.image = QLabel(self)
        self.image.setGeometry(200, 0, 600, 450)

        self.cheak_map = CustomComboBox(self)
        self.cheak_map.setGeometry(15, 70, 170, 25)
        self.cheak_map.addItem("схема")
        self.cheak_map.addItem("спутник")
        self.cheak_map.addItem("гибрид")
        self.cheak_map.currentTextChanged.connect(self.cheaking_map)

        self.cheaking_map()


    def cheaking_map(self):
        if self.cheak_map.currentText() == "схема":
            self.map = "map"
        elif self.cheak_map.currentText() == "спутник":
            self.map = "sat"
        else:
            self.map = "sat,skl"
        self.getImage()
        self.show_map()

    def show_map(self):
        ## Изображение
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def getImage(self):
        api_server = "http://static-maps.yandex.ru/1.x/"

        params = {
            "ll": ",".join([str(self.lon), str(self.lat)]),
            "spn": ",".join([str(self.scale), str(self.scale)]),
            "l": self.map,
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
        os.remove(self.map_file)

    # чтобы быстрее приближало или отдаляло зажимайте кнопку
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_PageDown:
            self.scale = self.scale + 0.001 if self.scale <= 50 else 50
        elif event.key() == QtCore.Qt.Key_PageUp:
            self.scale = self.scale - 0.001 if self.scale != 0.0 else 0.0
        elif event.key() == QtCore.Qt.Key_Left:
            self.lon = self.lon - 0.001 if self.lon + 0.001 >= -180 else 179.0
        elif event.key() == QtCore.Qt.Key_Right:
            self.lon = self.lon + 0.001 if self.lon + 0.001 <= 179.0 else -180.0
        elif event.key() == QtCore.Qt.Key_Up:
            self.lat = self.lat + 0.001 if self.lat + 0.001 <= 83 else -83.0
        elif event.key() == QtCore.Qt.Key_Down:
            self.lat = self.lat - 0.001 if self.lat + 0.001 >= -83.0 else 83.0
        self.getImage()
        self.show_map()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Prog()
    ex.show()
    sys.exit(app.exec_())

