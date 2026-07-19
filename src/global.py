import os
import json
import time
import threading
from datetime import datetime
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QPixmap

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

DATA_DIR = "data"
INDEX_DIR = os.path.join(DATA_DIR, "indexes")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class EditApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Host your Document")
        self.resize(1280, 720)

        central = QWidget()
        self.setCentralWidget(central)

        logo = QLabel()
        pixmap = QPixmap(resource_path("wd3.png"))
        pixmap = pixmap.scaled(
            300, 150,  # width, height
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.cut_line = QLabel("<br>")
        layout.addWidget(self.cut_line)
        layout.addWidget(logo)

        btn_select = QPushButton("Select index")
        btn_select.clicked.connect(self.select_file)
        layout.addWidget(
            btn_select,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
         
        self.old_fullname = QLabel()
        self.old_fullname.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.old_fullname)

        self.the_expiry = QLabel()
        self.the_expiry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.the_expiry)

        self.expiry_in = QLabel()
        self.expiry_in.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.expiry_in)

        self.file_label = QLabel("No file selected")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.file_label)

        label = QLabel("<br>Folder")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.name = QLineEdit()
        self.name.setFixedWidth(400)

        layout.addWidget(self.name, alignment=Qt.AlignmentFlag.AlignCenter)

        rdir = QLabel("Redirect File")
        rdir.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(rdir)

        self.redirect = QLineEdit()
        self.redirect.setFixedWidth(400)

        layout.addWidget(self.redirect, alignment=Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton("Save")
        btn.clicked.connect(self.register_name)
        layout.addWidget(
            btn,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        central.setLayout(layout)

        btn_select.setMaximumWidth(580)
        btn.setMaximumWidth(400)

        self.selected_file = None

    def register_name(self):
        self.register_file()
    
    def register_file(self):
        name = self.name.text().strip()
        redirect = self.redirect.text().strip()

        if not name:
            QMessageBox.warning(self, "Error", "Enter Folder Path")
            return
        if not redirect:
            QMessageBox.warning(self, "Error", "Enter Primary File")
            return
        if not self.selected_file:
            QMessageBox.warning(self, "Error", "Select an index file first")
            return

        try:
            data = {}

            if os.path.exists(self.selected_file):
                with open(self.selected_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

            data["folder"] = name
            data["primary_file"] = redirect
            data["created_time"] = time.time()

            with open(self.selected_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            QMessageBox.information(
                self,
                "Success",
                "Index file updated successfully."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def select_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select index file",
            INDEX_DIR,
            "*.dat"
        )

        if file_path:

            self.selected_file = file_path

            try:

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                fullname = data.get("fullname", "")
                expiry = data.get("expiry", 0)

                self.old_fullname.clear()
                self.old_fullname.setText(fullname)
                self.the_expiry.clear()
                self.the_expiry.setText(str(expiry))
                
                self.name.setText(data.get("folder", ""))
                self.redirect.setText(data.get("primary_file", ""))

                if isinstance(expiry, (int, float)):
                    expiry_date = datetime.fromtimestamp(expiry)

                expiry_date = datetime.fromtimestamp(expiry)
                
                if time.time() > expiry:
                    self.the_expiry.setText(f"EXPIRED ({expiry_date})")
                    self.expiry_in.setText(f"EXPIRED")
                else:
                    self.the_expiry.setText(f"ACTIVE ({expiry_date})")
                    self.expiry_in.setText(f"EXPIRES IN {expiry_date}")

                self.file_label.setText(file_path)

            except Exception as e:

                self.file_label.setText("Invalid index file")
                print("ERROR:", e)


app = QApplication([])
window = EditApp()
window.show()
app.exec()
