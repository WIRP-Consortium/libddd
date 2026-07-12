import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QStyle

from PyQt6.QtCore import QSize

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

        search_icon = QIcon(resource_path("assets/search.png"))
        logo_icon = QIcon(resource_path("assets/wwd.png"))

        self.setWindowTitle("WWC Scrutari")
        self.resize(1280, 720)
        self.setWindowIcon(QIcon(resource_path("assets/wwd.png")))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.search = QLineEdit()
        self.search.setToolTip("Enter your search query here")
        self.search.setPlaceholderText("Search...")
        self.search.setFixedWidth(1500)

        btn = QPushButton("Search")
        btn.clicked.connect(self.open_browser)
        btn.setFixedWidth(100)

        self.search.setFixedHeight(23)
        btn.setFixedHeight(23)

        title = QLabel()
        pixmap = QPixmap(resource_path("assets/wwd.png"))
# Scale small logo if needed
        pixmap = pixmap.scaled(260, 260, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        title.setPixmap(pixmap)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        more_button = QToolButton()
        more_button.setText("☰")
        menu = QMenu()

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setFixedHeight(1)
        line.setStyleSheet("""
            QFrame {
                background-color: #999999;
                border: none;
            }
        """)

        about_action = menu.addAction("About")
        about_action.triggered.connect(self.about)

        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        more_button.setMenu(menu)
        more_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.setStyleSheet("""
            background-color: #666666;

            QLineEdit {
                background: white;
                color: black;
                border: 1px solid #333;
                padding: 5px;
                border-radius: 5px;
            }

            QPushButton {
                background: white;
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
        top_bar.setSpacing(0) 

        self.search.addAction(
            logo_icon,
            QLineEdit.ActionPosition.LeadingPosition
        )

        wirp_logo = QLabel()

        wirp_pixmap = QPixmap(resource_path("assets/wirp.png"))
        wirp_pixmap = wirp_pixmap.scaled(
            120,
            120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        wirp_logo.setPixmap(wirp_pixmap)
        wirp_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.search.setStyleSheet("""
                QLineEdit {
                background: white;
                color: black;
                border: 1px solid #333;
                border-right:0px;
            }
        """)

        btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #333;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 1px;
                border-bottom-right-radius: 1px;
                padding: 1px 15px;
                background: white;
            }
            QPushButton:hover {
                background-color: #89CFF0;
            }
        """)
        more_button.setStyleSheet("""
            QToolButton {
                border: 1px solid #333;
                border-right:0px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 1px;
                border-bottom-right-radius: 1px;
                padding: 1px 15px;
                background: white;
            }
        """)

        top_bar.addWidget(more_button)
        top_bar.addWidget(self.search)
        top_bar.addWidget(btn)

        layout.addWidget(container)  # for QMainWindow
        layout.addWidget(line)

        logo_bar = QHBoxLayout()
        logo_bar.setContentsMargins(10, 5, 10, 0)

        logo_bar.addStretch()
        logo_bar.addWidget(wirp_logo)

        layout.addLayout(logo_bar)

        center_input = QLineEdit()
        center_input.setToolTip("Enter your search query here")
        center_input.setPlaceholderText("Search...")
        center_input.setFixedWidth(400)
        center_button = QPushButton("➜")
        center_button.clicked.connect(self.open_browser)
        center_button.setFixedWidth(100)

        layout.addSpacing(200)

        middle = QVBoxLayout()
        middle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        middle.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        middle.addSpacing(15)

        center_bar = QHBoxLayout()
        center_bar.setSpacing(0) 
        center_bar.setContentsMargins(0, 0, 0, 0)  
        center_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        link = QLabel('Your contribution helps us the software improve. <a href="donate">Donate us</a>')
        link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        link.setOpenExternalLinks(False)
        link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        br = QLabel("<br>")

        link.linkActivated.connect(self.open_donate)

        center_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #333;
                border-right: none;
                border-top-left-radius: 1px;
                border-bottom-left-radius: 1px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                padding: 1px;
                background: white;
            }
        """)

        center_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #333;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 1px;
                border-bottom-right-radius: 1px;
                padding: 1px 15px;
                background: #00BFFF;
                color:white;
                font-size: 22px;
            }
            QPushButton:hover {
                background-color: #89CFF0;
            }
            QPushButton:pressed {
                background: #87CEFA;
            }
        """)
        center_input.setFixedSize(430, 30)
        center_button.setFixedSize(60, 30)
        more_button.setFixedHeight(23)

        center_input.addAction(
            search_icon,
            QLineEdit.ActionPosition.LeadingPosition
        )

        center_bar.addWidget(center_input)
        center_bar.addWidget(center_button)

        middle.addLayout(center_bar)

        layout.addLayout(middle)

        layout.addWidget(link)


    def open_browser(self):
        query = self.search.text().strip()

        self.browser = EditApp()

        self.browser.recipient.setText(query)
        self.browser.method.setText("/")

        self.browser.show()

        self.browser.send()

    def open_donate(self, href):
        from donate import DonateWindow

        self.donate_window = DonateWindow()
        self.donate_window.show()

    def about(self):

        msg = QMessageBox(self)
        msg.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )

        msg.setWindowTitle("About WD3")

        msg.setText(
            "WD3 Version 0.001\n\n"
            "World Distributed Data Directory \n\n"
            "WD3 is a peer-to-peer document-sharing system.\n"
            "WD3 enables everyone to share knowledge on "
            "the internet in a decentralized way\n"
            "WD3 uses an ICH (Internet Crypto Hash) address "
            "is a simple document sharing protocol "
            "that helps host your docs "
            "on the internet\n\n"
            "(C)Copyright Rohith Poyyara & WIRP Consortium\n\n"
            "WD3 & WRANS are Trademark of WIRP Consortium & Rohith"

        )

        pixmap = QPixmap("assets/wd3_2.png")

        if pixmap.isNull():
            msg.setIcon(QMessageBox.Icon.Information)
        else:
            msg.setIconPixmap(
                pixmap.scaled(
                    80,
                    80,
                    Qt.AspectRatioMode.KeepAspectRatio
                )
            )

        msg.exec()


app = QApplication(sys.argv)

win = HomeWindow()
win.show()

sys.exit(app.exec())
