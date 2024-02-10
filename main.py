import sys
import os

import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5 import QtCore


#  нахождение масштаба, при показе объекта
def find(size):
    delta1 = abs(float(size["lowerCorner"].split()[0]) - float(size["upperCorner"].split()[0]))
    delta2 = abs(float(size["lowerCorner"].split()[1]) - float(size["upperCorner"].split()[1]))
    return delta1, delta2


# создаю класс для QComboBox, переопределяя метод для обработки событий клавиатуры,
# чтобы, при нажатии стрелочек на клавиатуре, значение ComboBox не менялось
class CustomComboBox(QComboBox):
    def keyPressEvent(self, event: QKeyEvent):
        event.ignore()


class Prog(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(700, 300, 600, 550)

        self.image = QLabel(self)
        self.image.setGeometry(0, 0, 600, 450)

        self.cheak_map = CustomComboBox(self)
        self.cheak_map.setGeometry(10, 460, 180, 25)
        self.cheak_map.addItem("схема")
        self.cheak_map.addItem("спутник")
        self.cheak_map.addItem("гибрид")
        self.cheak_map.currentTextChanged.connect(self.cheaking_map)

        self.find_object = QLineEdit(self)
        self.find_object.setGeometry(10, 490, 180, 25)
        self.find_object.setPlaceholderText("Введите название объекта")
        self.find_object.textChanged.connect(self.handleTextChanged)

        self.but_find = QPushButton("Найти", self)
        self.but_find.setGeometry(10, 520, 60, 25)
        self.but_find.clicked.connect(self.find_coords)

        self.output_ful_address = QLineEdit(self)
        self.output_ful_address.setGeometry(200, 460, 260, 25)
        self.output_ful_address.setText("щас очистится")
        self.output_ful_address.setReadOnly(True)

        self.initial_data()

        self.but_find = QPushButton("Сбросить", self)
        self.but_find.setGeometry(510, 510, 80, 30)
        self.but_find.clicked.connect(self.initial_data)

    # начальные данные
    def initial_data(self):
        self.lon, self.lat = 44.915441, 53.224134  # широта и долгота
        self.scale1, self.scale2 = 0.002, 0.002  # масштаб
        self.delta1, self.delta2 = 0.001, 0.001  # изменение масштаба
        self.label_on_map = None  # метка на карте
        self.cheak_map.setCurrentText("схема")  # текущий тип карты
        self.find_object.clear()  # очищаем поля для ввода названия объекта
        self.find_object.setPlaceholderText("Введите название объекта")
        self.output_ful_address.clear()  # очищаем поля для вывода полного адреса объекта
        self.cheaking_map()

    # нажодение координат объекта по названию
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
            full_address = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"][
                "AddressDetails"]["Country"]["AddressLine"]
            self.output_ful_address.setText(full_address)

            size = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]["boundedBy"]["Envelope"]
            self.scale1, self.scale2 = find(size)  # масштаб
            self.delta_scale()

            coords_center = json_response["response"]["GeoObjectCollection"
            ]["featureMember"][0]["GeoObject"]["Point"]["pos"]
            # широта и долгота
            self.lon, self.lat = float(coords_center.split(" ")[0]), float(coords_center.split(" ")[1])
            self.label_on_map = f'{",".join([str(self.lon), str(self.lat)])},pm2rdm' # метка на карту

            self.getImage()
            self.show_map()

        except:
            self.find_object.clear()
            self.find_object.setPlaceholderText("Объект не найден")

    # отслеживание какой тип карты выбран
    def cheaking_map(self):
        if self.cheak_map.currentText() == "схема":
            self.map = "map"
        elif self.cheak_map.currentText() == "спутник":
            self.map = "sat"
        else:
            self.map = "sat,skl"
        self.getImage()
        self.show_map()

    # вывод карты
    def show_map(self):
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    # получение из static-maps карты
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

    # изменение масштаба и движение по карте при нажатии на клавиши
    def keyPressEvent(self, event):
        # чтобы быстрее приближало или отдаляло зажимайте кнопку
        if event.key() == QtCore.Qt.Key_PageDown:
            self.scale1 = self.scale1 + self.delta1 if self.scale1 + self.delta1 <= 50 else 50
            self.scale2 = self.scale2 + self.delta2 if self.scale2 + self.delta2 <= 50 else 50
        elif event.key() == QtCore.Qt.Key_PageUp:
            self.scale1 = self.scale1 - self.delta1 if self.scale1 - self.delta1 > 0.0 else 0.0
            self.scale2 = self.scale2 - self.delta2 if self.scale2 - self.delta2 > 0.0 else 0.0

        elif event.key() == QtCore.Qt.Key_Left:
            self.lon = self.lon - self.delta1 if self.lon + self.delta1 >= -180 else 179.0
        elif event.key() == QtCore.Qt.Key_Right:
            self.lon = self.lon + self.delta2 if self.lon + self.delta2 <= 179.0 else -180.0
        elif event.key() == QtCore.Qt.Key_Up:
            self.lat = self.lat + self.delta1 if self.lat + self.delta1 <= 83 else -83.0
        elif event.key() == QtCore.Qt.Key_Down:
            self.lat = self.lat - self.delta2 if self.lat + self.delta2 >= -83.0 else 83.0

        self.delta_scale()
        self.getImage()
        self.show_map()

    # относительно текущего масштаба изменяем дельту масштаба
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

    # пока пользователь чего-нибудь не написал в поле, там выводится надпись =>
    def handleTextChanged(self, text):
        if not text and self.find_object.hasFocus():
            self.find_object.setPlaceholderText("Введите название объекта")

    # при закрытии окна удаляем файлик с картой
    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Prog()
    ex.show()
    sys.exit(app.exec_())

