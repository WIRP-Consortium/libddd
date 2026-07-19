import hashlib
import secrets
import sys
import os
import json
import subprocess
import webbrowser
import hmac
import requests
import psutil
import time
import socket
import threading
from datetime import datetime, timedelta

from cryptography.fernet import Fernet

from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QIcon

from PyQt6.QtWidgets import (
    QSizePolicy
)

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QLineEdit,
    QFileDialog
)
from PyQt6.QtWidgets import (
    QHBoxLayout, QListWidget, QStackedWidget, QComboBox
)

from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtGui import QTextFormat
from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtCore import QSize

from PyQt6.QtWidgets import (
    QPushButton, QTableWidget, QTableWidgetItem, QStackedLayout
)
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit
)
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from PyQt6.QtGui import (
    QPixmap,
    QPainter,
    QColor,
    QFont,
    QPen
)

PORT = 443

DATA_DIR = os.path.join(
    os.environ["APPDATA"],
    "libddd",
    "data"
)
ICH_FILE = os.path.join(DATA_DIR, "internet.ich")
INDEX_DIR = os.path.join(DATA_DIR, "indexes")
LICENSE_FILE = os.path.join(DATA_DIR, "license.key")
DATA_FILE = "allowed_ips.json"
REQUEST_FILE = "request.json"
TRANSACTION_FILE = "data/transaction.json"

country_code = None
continent_code = None

#code = get_codes()
if not os.path.exists(ICH_FILE):
    from find import get_codes

def create_entry():
    ip = allowed_ip.text().strip()

    if not ip:
        return

    sha = hashlib.sha256(ip.encode()).hexdigest()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add to table
    row = table.rowCount()
    table.insertRow(row)
    table.setItem(row, 0, QTableWidgetItem(ip))
    table.setItem(row, 1, QTableWidgetItem(sha))
    table.setItem(row, 2, QTableWidgetItem(date))

    # Save to JSON
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append({
        "ip": ip,
        "sha256": sha,
        "date": date
    })

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    allowed_ip.clear()

def load_entries():
    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    for entry in data:
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(entry["ip"]))
        table.setItem(row, 1, QTableWidgetItem(entry["sha256"]))
        table.setItem(row, 2, QTableWidgetItem(entry["date"]))


def create_splash():

    # Window size
    pixmap = QPixmap(520, 300)
    pixmap.fill(QColor("white"))

    painter = QPainter(pixmap)

    logo = QPixmap(resource_path("assets/wd3.png"))
    logo = logo.scaled(
        110,
        110,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    painter.drawPixmap(25, 35, logo)

    # ---------------- Title ----------------
    title_font = QFont("Segoe UI", 20)
    title_font.setBold(True)

    painter.setFont(title_font)
    painter.setPen(QColor(30, 30, 30))

    painter.drawText(160, 80, "GlobalBytes")

    sub_font = QFont("Segoe UI", 11)
    painter.setFont(sub_font)

    painter.drawText(160, 110, "World Distributed Data Directory")

    version_font = QFont("Segoe UI", 10)
    painter.setFont(version_font)
    painter.setPen(QColor(90, 90, 90))

    painter.drawText(160, 135, "Version 0.001")

    painter.drawText(
        25,
        250,
        "(C) WIRP Consortium"
    )

    # ---------------- Bottom line ----------------
    painter.setPen(QPen(QColor(210, 210, 210)))
    painter.drawLine(0, 265, 520, 265)

    painter.end()

    splash = QSplashScreen(pixmap)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    return splash

def generate_license():
    """
    Generate encryption key if not exists
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(LICENSE_FILE):
        key = Fernet.generate_key()

        with open(LICENSE_FILE, "wb") as f:
            f.write(key)

def is_online():
    try:
        requests.get("https://ipwho.is/", timeout=3)
        return True
    except requests.RequestException:
        return False
    

def load_license():
    """
    Load encryption key
    """
    with open(LICENSE_FILE, "rb") as f:
        return f.read()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def generate_router_id(continent_code, country_code):
    random_part = secrets.token_hex(8)

    raw = f"{continent_code}:{country_code}:{random_part}"
    h = hashlib.sha256(raw.encode()).hexdigest()

    return f"{continent_code}:{country_code}:GW:{h[:10]}"

def load_all_data():
    results = []

    if not os.path.exists(INDEX_DIR):
        return results

    for file in os.listdir(INDEX_DIR):
        if file.endswith(".dat"):
            file_path = os.path.join(INDEX_DIR, file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                results.append({
                    "fullname": data.get("fullname"),
                    "folder": data.get("folder"),
                    "primary_file": data.get("primary_file"),
                    "private_key": data.get("asymmetric_private")
                })

            except Exception as e:
                print(f"Failed reading {file}: {e}")

    return results

def load_all_names_from_indexes():
    names = []

    if not os.path.exists(INDEX_DIR):
        return names

    for file in os.listdir(INDEX_DIR):
        if file.startswith("index_") and file.endswith(".dat"):
            file_path = os.path.join(INDEX_DIR, file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # case 1: single record
                if isinstance(data, dict):
                    name = data.get("fullname")
                    if name:
                        names.append(name)

                # case 2: list of records (common in index systems)
                elif isinstance(data, list):
                    for item in data:
                        name = item.get("fullname")
                        if name:
                            names.append(name)

            except Exception as e:
                print(f"Failed reading {file}: {e}")

    return names

def try_send(ip, packet):
    try:
        PORT = 500
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer:
            peer.settimeout(5)

            print(f"Connecting to {ip}:{PORT}...")
            peer.connect((ip, PORT))

            peer.sendall(packet.encode("utf-8"))
            print("Message sent successfully")

            response = peer.recv(8192).decode("utf-8", errors="ignore")

            print("\n--- SERVER RESPONSE ---\n")
            print(response)

            if not response:
                print("Server sent no response.")
                return False

            ext = None
            data = None

            for line in response.splitlines():
                if line.startswith("RESOURCE:"):
                    ext = line.split("/", 1)[-1].strip()

                elif line.startswith("DATA:"):
                    try:
                        data = int(line.split(":", 1)[1].strip())
                    except ValueError:
                        print("Invalid DATA field.")
                        return False

            if data is None:
                print("Missing DATA field in server response.")
                return False

            os.makedirs("data", exist_ok=True)

            record = {
                "resource": ext,
                "data": data,
                "response": response,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            print(f"Resource: {ext}")
            print(f"Data size: {data}")

            return True

    except socket.timeout:
        print("Connection timed out")
        return False

    except ConnectionRefusedError:
        print("Connection refused")
        return False

    except Exception as e:
        print("Direct P2P failed")
        print("Reason:", e)
        return False
    
def recv_all(conn):
    buffer = b""
    while True:
        part = conn.recv(4096)
        if not part:
            break
        buffer += part
        if len(part) < 4096:
            break
    return buffer  

class App(QMainWindow):

    def __init__(self):
        super().__init__()

        splash.showMessage("Reading license...")
        QApplication.processEvents()

        # load license

        splash.showMessage("Loading indexes...")
        QApplication.processEvents()

        # load indexes

        splash.showMessage("Preparing UI...")
        QApplication.processEvents()

        self.server_process = None 

        shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        shortcut.activated.connect(self.open_wrs)

        shortcut2 = QShortcut(QKeySequence("Ctrl+G"), self)
        shortcut2.activated.connect(self.open_global)

        shortcut3 = QShortcut(QKeySequence("Ctrl+D"), self)
        shortcut3.activated.connect(self.open_donate)

        shortcut4 = QShortcut(QKeySequence("Ctrl+A"), self)
        shortcut4.activated.connect(self.about)

        shortcut5 = QShortcut(QKeySequence("Ctrl+P"), self)
        shortcut5.activated.connect(self.about_qt)

        shortcut6 = QShortcut(QKeySequence("Ctrl+M"), self)
        shortcut6.activated.connect(self.motto)

        shortcut7 = QShortcut(QKeySequence("Ctrl+Q"), self)
        shortcut7.activated.connect(self.close)

        self.setWindowTitle("GlobalBytes")
        self.resize(1280, 720)
        self.setWindowIcon(QIcon(resource_path("assets/wd3.png")))

        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        file_menu.addAction("Select Index File").triggered.connect(self.select_file)
        file_menu.addAction("Register").triggered.connect(self.registry)
        file_menu.addAction("Host").triggered.connect(self.host)
        file_menu.addAction("HLRN").triggered.connect(self.hlrn)
        file_menu.addAction("Exit").triggered.connect(self.close)

        tool_menu = menubar.addMenu("Tool")
        tool_menu.addAction("Register").triggered.connect(self.registry)
        tool_menu.addAction("Start Maintain").triggered.connect(self.maintain)
        tool_menu.addAction("Create WRIP").triggered.connect(self.wrip)
        tool_menu.addAction("Start Mining").triggered.connect(self.mining)

        wddd_menu = menubar.addMenu("WD3")
        wddd_menu.addAction("Visit on Github").triggered.connect(self.open_web)
        wddd_menu.addAction("Donate").triggered.connect(self.donate)

        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About GlobalBytes").triggered.connect(self.about)
        help_menu.addAction("About PyQt").triggered.connect(self.about_qt)
        help_menu.addAction("WDDD Motto").triggered.connect(self.motto)

        os.makedirs(DATA_DIR, exist_ok=True)
        generate_license()

        key = load_license()
        cipher = Fernet(key)

        if os.path.exists(ICH_FILE):
            try:
                with open(ICH_FILE, "rb") as f:
                    encrypted_data = f.read()

                data = json.loads(cipher.decrypt(encrypted_data).decode())
                ich_address = data["public"]
                welcome_text = "Welcome to GlobalBytes"
                self.current_hash = str(ich_address)

            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                sys.exit()

        else:
            country_code, continent_code, *_ = get_codes()
            random_data = secrets.token_bytes(256)
            h = hashlib.sha256(random_data).hexdigest()
            ich_hash = ":".join([h[i:i+3] for i in range(0, len(h), 3)])

            data = {
                "public": f"{continent_code}:{country_code}-{ich_hash}",
                "private": hashlib.sha512(secrets.token_bytes(512)).hexdigest(),
                "route_id": generate_router_id(continent_code, country_code)
            }

            ich_address = data["public"]
            ciphered = cipher.encrypt(json.dumps(data).encode())
            self.current_hash = str(ich_address)

            with open(ICH_FILE, "wb") as f:
                f.write(ciphered)

            welcome_text = "Welcome to GlobalBytes (New User)"

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        #  SIDEBAR
        self.nav = QListWidget()
        
        items = [
            ("Home", resource_path("assets/home.png")),
            ("IDTP", resource_path("assets/idtp.png")),
            ("Indexes", resource_path("assets/list.png")),
            ("Network Sync", resource_path("assets/sync.png")),
            ("Data Sync", resource_path("assets/sync.png")),
            ("Stream", resource_path("assets/global.png")),
            ("About", resource_path("assets/info.png"))  
        ]

        for text, icon in items:
            if icon:
                item = QListWidgetItem(QIcon(icon), text)
            else:
                item = QListWidgetItem(text)
            self.nav.addItem(item)
        self.nav.setFixedWidth(180)
        self.nav.setIconSize(QSize(25, 25))

        self.nav.setStyleSheet("""
            QListWidget {
                background-color: #e0e0e0;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 5px;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #c8c8c8;
                color:black;
                border: none;
                outline: none;
            }
            QListWidget::item:hover {
                background-color: #d6d6d6;
            }
            QListWidget::item:focus {
                outline: none;
            }
        """)

        self.sidebar_title = QLabel("Home")
        self.sidebar_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
            padding:12px;
            background:#e0e0e0;
            color:black;
        """)

        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 10)
        sidebar_layout.setSpacing(0)

        # NAV at top
        sidebar_layout.addWidget(self.nav)

# Spacer pushes logo to bottom
        sidebar_layout.addStretch()

        bottom_logo = QLabel()

        pixmap = QPixmap(resource_path("assets/wd3.png"))
        pixmap = pixmap.scaled(
            110, 110,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        bottom_logo.setPixmap(pixmap)
        bottom_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sidebar_layout.addWidget(bottom_logo)

        right_layout = QVBoxLayout()
        self.pages = QStackedWidget()

        # HOME PAGE
        home_page = QWidget()
        home_layout = QVBoxLayout(home_page)

        home_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        home_layout.setContentsMargins(20, 20, 20, 20)
        home_layout.setSpacing(12)

        logo = QLabel()
        pixmap = QPixmap(resource_path("assets/wd3.ico"))
        pixmap = pixmap.scaled(
            300, 150,
            Qt.AspectRatioMode.KeepAspectRatio
        )
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("WD3 Version 0.001")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:22px;font-weight:bold;")

        sub = QLabel("WORLD DISTRIBUTED DATA DIRECTORY")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("font-size:18px;font-weight:bold;")

        welcome = QLabel(welcome_text)
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setWordWrap(True)

        hash_label = QLabel(str(ich_address))
        hash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hash_label.setWordWrap(True)
        hash_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        hash_label.setStyleSheet("font-family: monospace; font-size: 12px;")

        copy_btn = QPushButton("Copy ICH Address")
        copy_btn.clicked.connect(self.copy_hash)
        copy_btn.setMaximumWidth(180)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        copy_btn.setStyleSheet("""
            font-size:12px;
            padding:6px;
            border-radius:6px;
            background-color:#2d2d2d;
            color:white;
        """)

        about_text = QLabel(
            "<br>Don't share the file 'internet.ich' & 'license.key'"
        )
        about_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        home_layout.addWidget(logo)
        home_layout.addWidget(title)
        home_layout.addWidget(sub)
        home_layout.addWidget(welcome)
        home_layout.addWidget(hash_label)
        home_layout.addWidget(copy_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        home_layout.addWidget(about_text)

        # SETTINGS PAGE
        idtp_page = QWidget()
        s_layout = QVBoxLayout(idtp_page)
        s_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        s_label = QLabel("Internet Data Transmission Protocol")
        s_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s_layout.addWidget(s_label)
 
        #Server Part
        self.label = QLabel("Server Status: Stopped")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s_layout.addWidget(self.label)

        self.start_btn = QPushButton("Start Server")
        self.start_btn.clicked.connect(self.start_server)
        s_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop Server")
        self.stop_btn.clicked.connect(self.stop_server)
        s_layout.addWidget(self.stop_btn)

        
        net = psutil.net_io_counters()

        sent_label = QLabel(f"Sent: {net.bytes_sent / 1024:.2f} KB")
        received_label = QLabel(f"Received: {net.bytes_recv / 1024:.2f} KB")
        total_label = QLabel(f"Total: {(net.bytes_sent + net.bytes_recv) / 1024:.2f} KB")

        ns_page = QWidget()
        a_layout = QVBoxLayout(ns_page)
        a_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        a_label = QLabel("Network Sync")
        a_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        a_layout.addWidget(a_label)

        a_layout.addWidget(sent_label)
        a_layout.addWidget(received_label)
        a_layout.addWidget(total_label)

        #==========index==============
        index_page = QWidget()
        i_page = QVBoxLayout(index_page)
        i_page.setAlignment(Qt.AlignmentFlag.AlignCenter)

        i_label = QLabel("Indexes")
        i_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        i_page.addWidget(i_label)

        name_label = QLabel("Name")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        i_page.addWidget(name_label)
        self.name = QLineEdit()
        self.name.setFixedWidth(700)
        i_page.addWidget(self.name, alignment=Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton("Search")
        btn.clicked.connect(self.search_name)
        i_page.addWidget(
            btn,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        btn.setFixedWidth(100)

        names = load_all_names_from_indexes()
        names_widget = QListWidget()
        names_widget.addItems(names)

        i_page.addWidget(names_widget)

        #stream
        sync_page = QWidget()
        sync_layout = QVBoxLayout(sync_page)


# Tabs (Request / Receive)
        sync_tabs = QTabWidget()

        sync_tabs.setStyleSheet("""
        QTabWidget::pane {
            border: 1px solid #cccccc;
        }

        QTabBar::tab {
            background: #eeeeee;
            padding: 10px 40px;
        }

        QTabBar::tab:selected {
            background: #2d2d2d;
            color: white;
        }

        QTabBar::tab:hover {
        }
        """)


# Request tab
        request_page = QWidget()

        request_layout = QFormLayout(request_page)
        request_layout.setContentsMargins(20, 20, 20, 20)
        request_layout.setSpacing(12)

        request_label = QLabel("Request Node Data")
        request_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ip_label = QLineEdit()
        self.ich_label = QLineEdit()
        self.sha_label = QLineEdit()
        self.dfsp_label = QLineEdit()
        btn = QPushButton("Request")
        btn.setMaximumWidth(150)
        btn.setIcon(QIcon(resource_path("assets/sync.png")))
        btn.clicked.connect(self.request_part)

        self.req_table = QTableWidget()

        self.req_table.setColumnCount(5)
        self.req_table.setHorizontalHeaderLabels([
            "IP Address",
            "ICH Address",
            "SHA-256",
            "Sharing Protocol Address",
            "Date"
        ])
        req_header = self.req_table.horizontalHeader()
        req_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.load_requests()

        request_layout.addRow(request_label)
        request_layout.addRow("IP Address:", self.ip_label)
        request_layout.addRow("ICH Address:", self.ich_label)
        request_layout.addRow("SHA-256:", self.sha_label)
        request_layout.addRow("SP Code:", self.dfsp_label)
        request_layout.addRow("", btn)
        request_layout.addRow(self.req_table)


# Receive tab
        receive_page = QWidget()
        receive_layout = QFormLayout(receive_page)
        receive_layout.setContentsMargins(20, 20, 20, 20)
        receive_layout.setSpacing(12)

        receive_label = QLabel("Receive Node Data")
        receive_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.allowed_ip = QLineEdit()
        allow_btn = QPushButton("Create")
        allow_btn.setMaximumWidth(150)
        allow_btn.setIcon(QIcon(resource_path("assets/sync.png")))
        allow_btn.clicked.connect(self.create_entry)

        self.table = QTableWidget()

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "IP Address",
            "SHA-256",
            "Sharing Protocol Address",
            "Date"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.load_entries()

        receive_layout.addRow(receive_label)
        receive_layout.addRow("Allowed IP:", self.allowed_ip)
        receive_layout.addRow("", allow_btn)
        receive_layout.addRow(self.table)

        
        # Transactions Tab
        transactions_page = QWidget()
        transactions_layout = QVBoxLayout(transactions_page)

        transactions_label = QLabel("Transactions")
        transactions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels([
            "Transaction ID",
            "Sender",
            "Receiver",
            "Status",
            "Date"
        ])
        self.load_transactions()

        transactions_header = self.transactions_table.horizontalHeader()
        transactions_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.search_saction = QLineEdit()
        self.search_saction.setPlaceholderText("Enter ID")
        self.search_ip = QLineEdit()
        self.search_ip.setPlaceholderText("Enter IP")
        self.search_ip.setMaximumWidth(460)

        self.search_saction.textChanged.connect(
            self.search_transactions
        )

        self.search_ip.textChanged.connect(
            self.search_transactions
        )

        self.select = QComboBox()
        self.select.addItem("All")
        self.select.addItem("This Day")
        self.select.addItem("This Week")
        self.select.addItem("This Month")
        self.select.addItem("This Year")

        self.select.currentTextChanged.connect(self.load_transactions)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.select)
        top_layout.addWidget(self.search_saction)
        top_layout.addWidget(self.search_ip)

        transactions_layout.addWidget(transactions_label)
        transactions_layout.addLayout(top_layout)
        transactions_layout.addWidget(self.transactions_table)

        sync_tabs.addTab(request_page, "Request")
        sync_tabs.addTab(receive_page, "Receive")
        sync_tabs.addTab(transactions_page, "Transactions")

        sync_layout.addWidget(sync_tabs)


        #Status
        stream_page = QWidget()
        st_page = QVBoxLayout(stream_page)
        st_page.setAlignment(Qt.AlignmentFlag.AlignCenter)

        st_label = QLabel("Stream")
        st_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st_page.addWidget(st_label)

        #About
        about_page = QWidget()
        ab_page = QVBoxLayout(about_page)

        ab_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ab_page.setContentsMargins(20, 20, 20, 20)
        ab_page.setSpacing(10)

        logo = QLabel()
        pixmap = QPixmap(resource_path("assets/wd3.png"))
        pixmap = pixmap.scaled(
            300, 150,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ab_label = QLabel("About")
        ab_label.setStyleSheet("font-size:20px;font-weight:bold;")
        ab_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ab_text = QTextBrowser()

        ab_text.setPlainText("""
        GlobalBytes (WD3) is a distributed information-sharing system built on top of the Internet. It allows anyone to host, publish, share, and access information through documents and applications connected across the network.
        WD3 works using several technologies, including the Internet Data Transmission Protocol (IDTP), the WD3 Hypertext format (WHX), and other supporting protocols. Together, these technologies provide a common way for computers to locate, request, transfer, and display information.
        When a user enters a document name into a WD3 client, the client first checks the registry.dat database to translate the name into an IP address or network location. After the address is found, the client connects to the target server using TCP, and optionally TLS for secure communication.
        Once the connection is established, the client sends an IDTP request to the server. The server processes the request and returns an IDTP response containing the requested resource. The response may include WHX documents, text, images, audio, scripts, metadata, and other digital content.
        The client then parses the WHX document, creates the required objects and resources, and renders the final document page for the user.
        The goal of WD3 is to provide an open and distributed information system where anyone can publish and access information without depending on centralized platforms or services.
                             
        - Internet Data Transmission Protocol (IDTP)

        Internet Data Transmission Protocol (IDTP) is an application-layer protocol designed for distributed, collaborative data transfer and information-sharing systems. IDTP serves as the communication foundation of the GlobalBytes / WD3 ecosystem, enabling clients and servers to exchange WHX documents, resources,
        and other digital content.
        IDTP follows a request-response communication model. A transaction begins when a client submits a request to a server. The request data is protected using encryption, where session keys are securely exchanged and used to encrypt communication between the client and server.
        The server processes the request and returns a response describing the result of the operation. The response may also include requested resources such as documents, images, scripts, metadata, or other files.
        In the WD3 system, the Document Viewer operates as the client, while information hosts operate as servers that provide requested resources.
        IDTP is designed to support secure and efficient communication across distributed networks. It uses security mechanisms such as encryption, nonces, timestamps, and nonce caching to protect communication and help prevent replay attacks, interception, and unauthorized modification of data.
        Through bidirectional encrypted communication between clients and servers, IDTP helps protect information against eavesdropping and tampering.
        IDTP also supports high-traffic servers by using optimized communication methods, caching mechanisms, and cryptographic protections to improve reliability, performance, and data security.
                             
                Short Cuts
                Ctrl+R - Registrant
                Ctrl+G - Global
                Ctrl+D - Donate
                Ctrl+A - About
                Ctrl+P - About PyQt
                Ctrl+M - Motto
                Ctrl+Q - Quit
                             
        Hosting Tips:
            Ensure that the required service port is enabled and accessible.
            Configure your operating system firewall to allow inbound connections on the configured port.
            Verify that the service is running and listening on the expected port.

            Windows
            netstat -ano | findstr LISTENING | findstr :<PORT>

            Linux
            ss -ltnp | grep ':<PORT>'
            or
            netstat -ltnp | grep ':<PORT>'

            macOS
            sudo lsof -iTCP:<PORT> -sTCP:LISTEN -n -P
                             
        Use this code for TLS:
            openssl req -x509 -newkey rsa:4096 -keyout idtpd.key -out idtpd.crt -days 365 -nodes
            """)

        ab_text.setReadOnly(True)
        idtp_text = QTextBrowser()

        idtp_text.setPlainText("""
Internet Data Transmission Protocol (IDTP)

Internet Data Transmission Protocol (IDTP) is an application-layer protocol designed for distributed, collaborative data transfer and information-sharing systems. IDTP serves as the communication foundation of the GlobalBytes / WD3 ecosystem, enabling clients and servers to exchange WHX documents, resources, and other digital content.

IDTP follows a request-response communication model. A transaction begins when a client submits a request to a server. The request data is protected using encryption, where session keys are securely exchanged and used to encrypt communication between the client and server.

The server processes the request and returns a response describing the result of the operation. The response may also include requested resources such as documents, images, scripts, metadata, or other files.

In the WD3 system, the Document Viewer operates as the client, while information hosts operate as servers that provide requested resources.

IDTP is designed to support secure and efficient communication across distributed networks. It uses security mechanisms such as encryption, nonces, timestamps, and nonce caching to protect communication and help prevent replay attacks, interception, and unauthorized modification of data.

Through bidirectional encrypted communication between clients and servers, IDTP helps protect information against eavesdropping and tampering.

IDTP also supports high-traffic servers by using optimized communication methods, caching mechanisms, and cryptographic protections to improve reliability, performance, and data security.

        """)
        idtp_text.setReadOnly(True)

        ab_page.addWidget(logo)
        ab_page.addWidget(ab_label)
        ab_page.addWidget(ab_text)
        #ab_page.addWidget(idtp_text)

        self.pages.addWidget(home_page)
        self.pages.addWidget(idtp_page)
        self.pages.addWidget(index_page)
        self.pages.addWidget(ns_page)
        self.pages.addWidget(sync_page)
        self.pages.addWidget(stream_page)
        self.pages.addWidget(about_page)


        self.nav.currentRowChanged.connect(self.change_page)
        self.nav.setCurrentRow(0)

        right_layout.addWidget(self.pages)

        main_layout.addWidget(self.nav)
        main_layout.addLayout(right_layout)


    def create_entry(self):
        import random

        VERSION = "01"
        GLOBALBYTES_ID = "8125"

        ip = self.allowed_ip.text().strip()

        if not ip:
            return
        
        random_data = os.urandom(16).hex()

        total = f"{random_data}:{ip}"

        sha = hashlib.sha256(total.encode()).hexdigest()
        parts = []
        i = 0
        while i < len(sha):
            n = random.randint(1, 5)
            parts.append(sha[i:i+n])
            i += n

        stored_value = ":".join(parts)

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = self.table.rowCount()
        self.table.insertRow(row)

        node_id = f"{random.randint(100, 999)}"
        session_id = f"{random.randint(100, 999)}"
        protocol = "21"
        security = f"{random.randint(10, 99)}"
        checksum = f"{random.randint(10, 99)}"

        value = ".".join([
            session_id,
            node_id,
            GLOBALBYTES_ID,
            protocol,
            security,
            checksum,
            VERSION
        ])
        value = f"{value}"

        self.table.setItem(row, 0, QTableWidgetItem(ip))
        self.table.setItem(row, 1, QTableWidgetItem(stored_value))
        self.table.setItem(row, 2, QTableWidgetItem(value))
        self.table.setItem(row, 3, QTableWidgetItem(date))

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append({
            "ip": ip,
            "sha256": stored_value,
            "sharing_protocol": value,
            "date": date
        })

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        self.allowed_ip.clear()

    def load_entries(self):
        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        self.table.setRowCount(0)

        for entry in data:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(entry.get("ip", "")))
            self.table.setItem(row, 1, QTableWidgetItem(entry.get("sha256", "")))
            self.table.setItem(row, 2, QTableWidgetItem(entry.get("sharing_protocol", "")))
            self.table.setItem(row, 3, QTableWidgetItem(entry.get("date", "")))

    def request_part(self):
        ip_lbl = self.ip_label.text().strip()
        ich_lbl = self.ich_label.text().strip()
        sha_lbl = self.sha_label.text().strip()
        dfsp_lbl = self.dfsp_label.text().strip()

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = self.req_table.rowCount()
        self.req_table.insertRow(row)

        self.req_table.setItem(row, 0, QTableWidgetItem(ip_lbl))
        self.req_table.setItem(row, 1, QTableWidgetItem(ich_lbl))
        self.req_table.setItem(row, 2, QTableWidgetItem(sha_lbl))
        self.req_table.setItem(row, 3, QTableWidgetItem(dfsp_lbl))
        self.req_table.setItem(row, 4, QTableWidgetItem(date))

        if os.path.exists(REQUEST_FILE):
            with open(REQUEST_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append({
            "ip": ip_lbl,
            "ich": ich_lbl,
            "sha256": sha_lbl,
            "dfsp": dfsp_lbl,
            "date": date
        })
        VERSION = "0.1"
        ipa = requests.get("https://api.ipify.org").text.strip()
        SENDER_FILE = "data/send.json"

        idtp_packet = f"""VERSION: {VERSION}
FROM: {ipa}
ICH: {ich_lbl}
SHA256: {sha_lbl}
DFSP: {dfsp_lbl}
"""
        os.makedirs("data", exist_ok=True)

        if os.path.exists(SENDER_FILE):
            with open(SENDER_FILE, "r", encoding="utf-8") as f:
                try:
                    transactions = json.load(f)
                except json.JSONDecodeError:
                    transactions = []
        else:
            transactions = []

        transactions.append(idtp_packet)

        with open(SENDER_FILE, "w", encoding="utf-8") as f:
            json.dump(transactions, f, indent=4)

        try_send(ip_lbl, idtp_packet)

        with open(REQUEST_FILE, "w") as f:
            json.dump(data, f, indent=4)

        self.ip_label.clear()
        self.ich_label.clear()
        self.sha_label.clear()
        self.dfsp_label.clear()

    def load_transactions(self, filter_type="All"):
        TRANSACTION_FILE = "data/transaction.json"

        if not os.path.exists(TRANSACTION_FILE):
            return

        with open(TRANSACTION_FILE, "r", encoding="utf-8") as f:
            try:
                transactions = json.load(f)
            except json.JSONDecodeError:
                transactions = []

        now = datetime.now()

        filtered = []

        for tx in transactions:
            try:
                tx_date = datetime.strptime(
                    tx.get("date", ""),
                    "%Y-%m-%d %H:%M:%S"
            )
            except:
                continue

            if filter_type == "All":
                filtered.append(tx)

            elif filter_type == "This Day":
                if tx_date.date() == now.date():
                    filtered.append(tx)

            elif filter_type == "This Week":
                if tx_date >= now - timedelta(days=7):
                    filtered.append(tx)

            elif filter_type == "This Month":
                if (
                    tx_date.year == now.year and
                    tx_date.month == now.month
                ):
                    filtered.append(tx)

            elif filter_type == "This Year":
                if tx_date.year == now.year:
                    filtered.append(tx)

        self.transactions_table.setRowCount(0)

        for index, tx in enumerate(filtered):
            row = self.transactions_table.rowCount()
            self.transactions_table.insertRow(row)

            self.transactions_table.setItem(
                row, 0,
                QTableWidgetItem(tx.get("id", "Unknown"))
            )

            self.transactions_table.setItem(
                row, 1,
                QTableWidgetItem(tx.get("from", "Unknown"))
            )

            self.transactions_table.setItem(
                row, 2,
                QTableWidgetItem(tx.get("ich", "Unknown"))
            )

            self.transactions_table.setItem(
                row, 3,
                QTableWidgetItem(tx.get("dfsp", "Unknown"))
            )

            self.transactions_table.setItem(
                row, 4,
                QTableWidgetItem(tx.get("date", ""))
            )

    def search_transactions(self):
        id_text = self.search_saction.text().lower()
        ip_text = self.search_ip.text().lower()

        for row in range(self.transactions_table.rowCount()):
            id_item = self.transactions_table.item(row, 0)
            ip_item = self.transactions_table.item(row, 1)

            id_match = (
                not id_text or
                (id_item and id_text in id_item.text().lower())
            )

            ip_match = (
                not ip_text or
                (ip_item and ip_text in ip_item.text().lower())
            )

            self.transactions_table.setRowHidden(
                row,
                not (id_match and ip_match)
            )

    def load_requests(self):
        if not os.path.exists(REQUEST_FILE):
            return

        with open(REQUEST_FILE, "r") as f:
            data = json.load(f)

        self.req_table.setRowCount(0)

        for entry in data:
            row = self.req_table.rowCount()
            self.req_table.insertRow(row)

            self.req_table.setItem(row, 0, QTableWidgetItem(entry["ip"]))
            self.req_table.setItem(row, 1, QTableWidgetItem(entry["ich"]))
            self.req_table.setItem(row, 2, QTableWidgetItem(entry["sha256"]))
            self.req_table.setItem(row, 3, QTableWidgetItem(entry["dfsp"]))
            self.req_table.setItem(row, 4, QTableWidgetItem(entry["date"]))


    def change_page(self, index):
        self.pages.setCurrentIndex(index)

        name = self.nav.item(index).text()

        # update sidebar title
        self.sidebar_title.setText(name)

    def select_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Index File",
            INDEX_DIR,
            "*.dat"
        )

    def start_server(self):
        if self.server_process is None:
            self.server_process = subprocess.Popen(
                [sys.executable, "server.py"]
            )
            self.label.setText("Server Status: Running")

    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
            self.label.setText("Server Status: Stopped")

    def open_wrs(self):
        try:
            if getattr(sys, "frozen", False):
                # Running as EXE
                base_dir = os.path.dirname(sys.executable)
                target = os.path.join(base_dir, "wrs.exe")
                subprocess.Popen([target])
            else:
                # Running as Python script
                base_dir = os.path.dirname(os.path.abspath(__file__))
                target = os.path.join(base_dir, "wrs.py")
                subprocess.Popen([sys.executable, target])

        except Exception as e:
            print("Failed to launch:", e)

    def open_global(self):
        try:
            if getattr(sys, "frozen", False):
                # Running as EXE
                base_dir = os.path.dirname(sys.executable)
                target = os.path.join(base_dir, "global.exe")
                subprocess.Popen([target])
            else:
                # Running as Python script
                base_dir = os.path.dirname(os.path.abspath(__file__))
                target = os.path.join(base_dir, "global.py")
                subprocess.Popen([sys.executable, target])

        except Exception as e:
            print("Failed to launch:", e)

    def open_donate(self):
        try:
            subprocess.Popen(["python", "donate.py"])
        except Exception as e:
            print("Failed to launch:", e)

    def search_name(self):
        registrant = self.name.text().strip()

    def mining(self):
        subprocess.Popen(
            [sys.executable, "miner_ui.py"]
        )

    def registry(self):
        subprocess.Popen(
            [sys.executable, "wrs.py"]
        )

    def wrip(self):
        subprocess.Popen([sys.executable, "wrip.py"])

    def host(self):
        subprocess.Popen([sys.executable, "global.py"])

    def maintain(self):
        subprocess.Popen([sys.executable, "clean.py"])

    def hlrn(self):
        subprocess.Popen([sys.executable, "hlrn.py"])

    def open_web(self):
        webbrowser.open_new_tab(
            "https://github.com/WIRP-Consortium"
        )

    def donate(self):
        subprocess.Popen(
            [sys.executable, "donate.py"]
        )

    def about(self):

        msg = QMessageBox(self)
        msg.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )

        msg.setWindowTitle("WRANS Version 0.001")

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

    def motto(self):
        mt = QMessageBox(self)
        mt.setWindowTitle("WRANS Version 0.001")
        mt.setText(
            "About WDDD\n\n"
            "Global Information Sharing System\n\n"
        )

        map = QPixmap("assets/motto.jpg")

        if map.isNull():
            mt.setIcon(QMessageBox.Icon.Information)
        else:
            mt.setIconPixmap(
                map.scaled(
                    80,
                    80,
                    Qt.AspectRatioMode.KeepAspectRatio
                )
            )

        mt.exec()

    def about_qt(self):
        ms = QMessageBox(self)
        ms.setWindowTitle("About PyQt")

        ms.setText(
            "About PyQt\n\n"
            "This program uses PyQt6.\n\n"
            "PyQt is a set of Python bindings for the Qt application framework. "
            "It enables the development of cross-platform desktop applications "
            "using Python and provides access to the full range of Qt libraries "
            "for creating modern graphical user interfaces.\n\n"
            "PyQt is developed and maintained by Riverbank Computing Limited and "
            "is available under both commercial and GNU GPL licensing terms.\n\n"
            "For more information about PyQt, visit:\n"
            "https://www.riverbankcomputing.com/software/pyqt/\n\n"
            "Copyright © Riverbank Computing Limited and other contributors.\n\n"
            "PyQt is a trademark of Riverbank Computing Limited. "
            "Qt and the Qt logo are trademarks of The Qt Company Ltd."
        )

        pixmap = QPixmap("assets/pyqt.png")

        if pixmap.isNull():
            ms.setIcon(QMessageBox.Icon.Information)
        else:
            ms.setIconPixmap(
                pixmap.scaled(
                    80,
                    80,
                    Qt.AspectRatioMode.KeepAspectRatio
                )
            )

        ms.exec()

    def copy_hash(self):

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.current_hash)

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind(("0.0.0.0", 500))
        s.listen(1)

        print("Server listening on port 500...")

        while True:
            conn, addr = s.accept()

            try:
                print("Connected:", addr)

                data = conn.recv(1024)

                if not data:
                    conn.close()
                    continue

                message = data.decode("utf-8", errors="ignore")
                print(message)

                # Convert packet text into dictionary
                packet = {}

                for line in message.splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        packet[key.strip()] = value.strip()

                VER = packet.get("VERSION")
                fr_om = packet.get("FROM")
                ich = packet.get("ICH")
                sha = packet.get("SHA256")
                dfsp = packet.get("DFSP")
                id_record = os.urandom(16).hex()

                record = {
                    "id": id_record,
                    "version": VER,
                    "from": fr_om,
                    "ich": ich,
                    "sha256": sha,
                    "dfsp": dfsp,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                os.makedirs("data", exist_ok=True)

                if os.path.exists(TRANSACTION_FILE):
                    with open(TRANSACTION_FILE, "r", encoding="utf-8") as f:
                        try:
                            transactions = json.load(f)
                        except json.JSONDecodeError:
                            transactions = []

                else:
                    transactions = []

                transactions.append(record)

                with open(TRANSACTION_FILE, "w", encoding="utf-8") as f:
                    json.dump(transactions, f, indent=4)

                ipa = requests.get("https://api.ipify.org").text.strip()

                response = (
                    f"IP: {fr_om}\n"
                    f"FROM: {ipa}\n"
                    "STATUS: OK\n"
                    "RESOURCE: None\n"
                    f"DATA: {len(data)}\n"
                    "Transfer complete.\n"
                )

                conn.sendall(response.encode("utf-8"))

            except Exception as e:
                print("Client error:", e)

            finally:
                conn.close()

    except Exception as e:
        print("Server error:", e)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    threading.Thread(target=main, daemon=True).start()

    splash = create_splash()
    splash.show()

    splash.showMessage(
        "Loading license...",
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
        Qt.GlobalColor.black,
    )
    app.processEvents()
    time.sleep(1)
    splash.showMessage(
        "Loading IDTP...",
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
        Qt.GlobalColor.black,
    )
    app.processEvents()
    time.sleep(1)
    splash.showMessage(
        "Loading index...",
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
        Qt.GlobalColor.black,
    )
    app.processEvents()

    time.sleep(3)

    window = App()

    splash.showMessage(
        "Preparing interface...",
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
        Qt.GlobalColor.black,
    )
    app.processEvents()

    window.show()

    splash.finish(window)

    sys.exit(app.exec())
