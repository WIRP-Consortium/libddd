import os
import json
import time
import threading
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QMenu

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QLabel
)

REGISTRY_FILE = os.path.join("data/registry.dat")


class EditApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("THEYARE")
        self.resize(1280, 720)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.about = QLabel("THEYARE")
        self.about.setStyleSheet("font-size:18px;font-weight:bold;")
        self.about.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.about)

        self.search_name = QLineEdit()
        self.search_name.setFixedWidth(400)
        layout.addWidget(self.search_name, alignment=Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton("Search")
        btn.clicked.connect(self.search)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.fullname = QLabel()
        self.fullname.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.fullname)

        self.doctype = QLabel()
        self.doctype.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.doctype)

        self.extension = QLabel()
        self.extension.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.extension)

        self.register = QLabel()
        self.register.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.register)

        self.the_expiry = QLabel()
        self.the_expiry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.the_expiry)

        central.setLayout(layout)


    def search(self):
        self.result()
        
    def result(self):
        name = self.search_name.text().strip()

        found = False
        result_data = None

        with open(REGISTRY_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                item = json.loads(line)

                if item.get("fullname") == name:
                    found = True
                    result_data = item
                    break

        if found:
            self.registered_name = result_data["name"]
            self.fullname.setText(f"Name: {result_data['fullname']}")
            self.doctype.setText(f"Type: {result_data['type']}")
            self.extension.setText(f"Extension: {result_data['ext']}")
            registered_on = result_data["timestamp"]
            expiry_on = result_data["expiry"]

            expiry = datetime.fromtimestamp(expiry_on)

            register = datetime.fromtimestamp(registered_on)
            self.register.setText(f"Registered: {register.strftime('%Y-%m-%d %H:%M:%S')}")

            if time.time() > expiry_on:
                self.the_expiry.setText(f"EXPIRED ({expiry})")
            else:
                self.the_expiry.setText(f"EXPIRE ON ({expiry})")

           #QMessageBox.information(self, "Result", text)
            #QMessageBox.warning(self, "Result", "No matching file found.")


app = QApplication([])
window = EditApp()
window.show()
app.exec()
