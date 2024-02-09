import sys
import os

import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5 import QtCore


def find(size):
    delta1 = abs(float(size["lowerCorner"].split()[0]) - float(size["upperCorner"].split()[0]))
    delta2 = abs(float(size["lowerCorner"].split()[1]) - float(size["upperCorner"].split()[1]))
    return delta1, delta2


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

        self.lon, self.lat = 44.915441, 53.224134
        self.scale1, self.scale2 = 0.002, 0.002
        self.delta1, self.delta2 = 0.001, 0.001
        self.map = "map"
        self.label_on_map = None

        self.image = QLabel(self)
        self.image.setGeometry(200, 0, 600, 450)

        self.cheak_map = CustomComboBox(self)
        self.cheak_map.setGeometry(15, 70, 170, 25)
        self.cheak_map.addItem("схема")
        self.cheak_map.addItem("спутник")
        self.cheak_map.addItem("гибрид")
        self.cheak_map.currentTextChanged.connect(self.cheaking_map)

        self.find_object = QLineEdit(self)
        self.find_object.setGeometry(15, 100, 170, 25)
        self.find_object.setPlaceholderText("Введите название объекта")
        self.find_object.textChanged.connect(self.handleTextChanged)
        self.cheaking_map()

        self.but_find = QPushButton("Найти", self)
        self.but_find.setGeometry(15, 130, 60, 25)
        self.but_find.clicked.connect(self.find_coords)

    def find_coords(self):
        toponym_to_find = self.find_object.text()
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)

        if not response:
            self.find_object.setPlaceholderText("Объект не найден")

        json_response = response.json()
        try:
            size = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]["boundedBy"]["Envelope"]
            self.scale1, self.scale2 = find(size)
            self.delta_scale()

            coords_center = json_response["response"]["GeoObjectCollection"
            ]["featureMember"][0]["GeoObject"]["Point"]["pos"]
            self.lon, self.lat = float(coords_center.split(" ")[0]), float(coords_center.split(" ")[1])
            self.label_on_map = f'{",".join([str(self.lon), str(self.lat)])},pm2rdm'

            self.getImage()
            self.show_map()

        except:
            self.find_object.clear()
            self.find_object.setPlaceholderText("Объект не найден")

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
            "spn": ",".join([str(self.scale1), str(self.scale2)]),
            "l": self.map,
            "pt": self.label_on_map
        }
        response = requests.get(api_server, params=params)

        if not response:
            self.find_object.clear()
            self.find_object.setPlaceholderText("Объект не найден")
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
            self.scale1 = self.scale1 + self.delta1 if self.scale1 + self.delta1 <= 50 else 50
            self.scale2 = self.scale2 + self.delta2 if self.scale2 + self.delta2 <= 50 else 50
        elif event.key() == QtCore.Qt.Key_PageUp:
            self.scale1 = self.scale1 - self.delta1 if self.scale1 - self.delta1 > 0.0 else 0.0
            self.scale2 = self.scale2 - self.delta2 if self.scale2 - self.delta2 > 0.0 else 0.0

        elif event.key() == QtCore.Qt.Key_Left:
            self.lon = self.lon - 0.001 if self.lon + 0.001 >= -180 else 179.0
        elif event.key() == QtCore.Qt.Key_Right:
            self.lon = self.lon + 0.001 if self.lon + 0.001 <= 179.0 else -180.0
        elif event.key() == QtCore.Qt.Key_Up:
            self.lat = self.lat + 0.001 if self.lat + 0.001 <= 83 else -83.0
        elif event.key() == QtCore.Qt.Key_Down:
            self.lat = self.lat - 0.001 if self.lat + 0.001 >= -83.0 else 83.0

        self.delta_scale()
        self.getImage()
        self.show_map()

    def delta_scale(self):
        if self.scale1 < 0.05:
            self.delta1 = 0.001
        elif 0.05 <= self.scale1 <= 1:
            self.delta1 = 0.05
        else:
            self.delta1 = 1

        if self.scale2 < 0.05:
            self.delta2 = 0.001
        elif 0.05 <= self.scale2 <= 1:
            self.delta2 = 0.05
        else:
            self.delta2 = 1

    def handleTextChanged(self, text):
        if not text and self.find_object.hasFocus():
            self.find_object.setPlaceholderText("Введите название объекта")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Prog()
    ex.show()
    sys.exit(app.exec_())

