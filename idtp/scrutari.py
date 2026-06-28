import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

from client import EditApp

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WWC Scrutari")
        self.resize(1280, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.search.setFixedWidth(1500)

        btn = QPushButton("Search")
        btn.clicked.connect(self.open_browser)
        btn.setFixedWidth(100)

        title = QLabel()
        pixmap = QPixmap(resource_path("wwd.png"))

        pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        title.setPixmap(pixmap)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet("""
            background-color: #666666;

            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #333;
                padding: 5px;
                border-radius: 5px;
            }

            QPushButton {
                background-color: white;
                color: black;
                border: 1px solid #333;
                padding: 5px 15px;
                border-radius: 5px;
            }

            QPushButton:hover {
                background-color: #e0e0e0;
            }

            QLabel {
                color: white;
            }
        """)

        container = QWidget()
        top_bar = QHBoxLayout(container)

        top_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_bar.addWidget(self.search)
        top_bar.addWidget(btn)

        layout.addWidget(container) 

        center_input = QLineEdit()
        center_input.setPlaceholderText("Search...")
        center_input.setFixedWidth(400)
        center_button = QPushButton("Search")
        center_button.clicked.connect(self.open_browser)
        center_button.setFixedWidth(100)

        layout.addSpacing(260)

        middle = QVBoxLayout()
        middle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        middle.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        middle.addSpacing(15)

        center_bar = QHBoxLayout()
        center_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        center_bar.addWidget(center_input)
        center_bar.addWidget(center_button)

        middle.addLayout(center_bar)

        self.search.setStyleSheet("background-color: white; color: black;")
        center_button.setStyleSheet("background-color: white; color: black;")
        center_input.setStyleSheet("background-color: white; color: black;")
        btn.setStyleSheet("background-color: white; color: black;")

        layout.addLayout(middle)


    def open_browser(self):
        query = self.search.text().strip()

        self.browser = EditApp()

        self.browser.recipient.setText(query)
        self.browser.method.setText("/")

        self.browser.show()

        self.browser.send()


app = QApplication(sys.argv)

win = HomeWindow()
win.show()

sys.exit(app.exec())
