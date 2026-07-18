import socket
import requests
import json
import os
import hashlib
import secrets
import sys
import subprocess
import webbrowser
import hmac
import base64
import codecs
import time
import platform
import re
import ssl
import tempfile

from cryptography.fernet import Fernet

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from pathlib import Path
from PIL import Image
import io
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QMainWindow,
    QLineEdit, QPushButton, QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTextEdit
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import *

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
    QSlider,
    QFileDialog
)
from PyQt6.QtWidgets import (
    QHBoxLayout, QListWidget, QStackedWidget
)
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtGui import QTextFormat
from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtWidgets import QToolButton, QMenu
from Crypto.PublicKey import RSA

from PyQt6.QtCore import QUrl

from PyQt6.QtMultimedia import (
    QMediaPlayer,
    QAudioOutput
)

from PyQt6.QtMultimediaWidgets import QVideoWidget

PORT = 443
VERSION = "0.01"
TYPE = "DATA"
PORT2 = 443

HOST = "0.0.0.0"
CLIENT = "WWC SCRUTARI"
#HOST = "127.0.0.1"

REGISTRY_FILE = os.path.join("data", "registry.dat")

CACHE_DIR = "cache"

CERT_FILE = "idtpd.crt"

PRIVATE_PEM = "keys/private.pem"
PUBLIC_PEM = "keys/public.pem"

tls_context = ssl.create_default_context()

# for self-signed certificate
tls_context.check_hostname = False
tls_context.verify_mode = ssl.CERT_NONE

os.makedirs("keys", exist_ok=True)

os.makedirs(CACHE_DIR, exist_ok=True)
if not os.path.exists(PRIVATE_PEM) and not os.path.exists(PUBLIC_PEM):
    key = RSA.generate(3072)

    private_key = key.export_key()
    public_key = key.publickey().export_key()

# Save keys to files
    with open("keys/private.pem", "wb") as f:
        f.write(private_key)

    with open("keys/public.pem", "wb") as f:
        f.write(public_key)

with open(PRIVATE_PEM, "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
    )

# Load public key
with open(PUBLIC_PEM, "rb") as f:
    my_public_key = f.read().decode("utf-8")

# Get public IP
ipa = requests.get("https://api.ipify.org").text.strip()

def idtp_packet(ver, msg_type, ich, to, ip_addr,
                registrant,agent, method, resource, nonce, checksum, public_key, client_key, mac, signature, timestamp, character, iv, data):
    return f"""VER: {ver}
TYPE: {msg_type}
ICH: {ich}
TO: {to}
IP: {ip_addr}
REGISTRANT: {registrant}
AGENT: {agent}
METHOD: {method}
RESOURCE: {resource}
NONCE: {nonce}
CHK: {checksum}
CHTR: {character}
PUBLIC_KEY: {public_key}
CLIENT_KEY:
{client_key}
MAC: {mac}
SIGNATURE: {signature}
TIMESTAMP: {timestamp}
IV: {iv}

DATA:
{data}
"""

def aes_encrypt(key, iv, data):
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, data.encode(), None)
    return base64.b64encode(ciphertext).decode()

def parse_response(response):

    data = {}

    if response.startswith("IDTP:"):

        lines = response.splitlines()

        if lines:
            first = lines[0]

            if "/ ERROR" in first:
                data["TYPE"] = "ERROR"

        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()

        if data.get("TYPE") == "ERROR":
            print("IDTP ERROR")
            print("CODE:", data.get("CODE"))
            print("MESSAGE:", data.get("MESSAGE"))

            return data


    parts = response.split("|")

    if len(parts) != 3:
        print("Invalid response format")
        return {}

    encrypted_key_b64, iv_b64, encrypted_data_b64 = parts


    try:

        aes_key = private_key.decrypt(
            base64.b64decode(encrypted_key_b64),
            padding.OAEP(
                mgf=padding.MGF1(
                    algorithm=hashes.SHA256()
                ),
                algorithm=hashes.SHA256(),
                label=None
            )
        )


        iv = base64.b64decode(iv_b64)
        ciphertext = base64.b64decode(encrypted_data_b64)


        aesgcm = AESGCM(aes_key)

        plaintext = aesgcm.decrypt(
            iv,
            ciphertext,
            None
        )


    except Exception as e:
        print("Response decrypt failed:", e)
        return {}


    response_text = plaintext.decode("utf-8")


    if "\nDATA:\n" in response_text:
        header, body = response_text.split(
            "\nDATA:\n",
            1
        )
    else:
        header = response_text
        body = ""


    for line in header.splitlines():

        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()


    data["DATA"] = body.strip()


    if data.get("TYPE") == "ERROR":
        print("IDTP ERROR")
        print("CODE:", data.get("CODE"))
        print("MESSAGE:", data.get("MESSAGE"))
        data["MESSAGE"] = body.strip()


    return data

def try_send(ip, packet):
    try:
        raw_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        raw_socket.settimeout(5)

        print(f"Connecting TLS to {ip}:{PORT}")

        raw_socket.connect((ip, PORT))

        conn = tls_context.wrap_socket(
            raw_socket,
            server_hostname=ip
        )

        print(
            "TLS version:",
            conn.version()
        )

        conn.sendall(
            packet.encode("utf-8")
        )

        raw = recv_all(conn)

        print("RAW SERVER RESPONSE LENGTH:", len(raw))
        print(raw[:200])

        conn.close()

        if not raw:
            return False

        response = raw.decode(
            "utf-8",
            errors="ignore"
        )

        parsed = parse_response(response)

        print("TYPE:", parsed.get("TYPE"))
        print("RESOURCE:", parsed.get("RESOURCE"))
        print("DATA:", parsed.get("DATA"))

        return parsed


    except ssl.SSLError as e:
        print("TLS error:", e)
        return False


    except socket.timeout:
        print("Timeout")
        return False


    except Exception as e:
        print("Connection failed:", e)
        return False

def recv_all(conn, key):
    filename = hashlib.sha256(key.encode()).hexdigest()
    path = os.path.join(CACHE_DIR, filename)

    # return cached copy if it exists
    if os.path.exists(path):
        print("Cache hit")
        with open(path, "rb") as f:
            return f.read()

    print("Cache miss - receiving")

    # receive and save
    with open(path, "wb") as f:
        while True:
            chunk = conn.recv(1024 * 1024)  # 1 MB
            if not chunk:
                break
            f.write(chunk)

    # load if needed
    with open(path, "rb") as f:
        return f.read()

def find_user(name):
    if not os.path.exists(REGISTRY_FILE):
        print(f"Registry file not found: {REGISTRY_FILE}")
        return None

    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if item.get("fullname") == name:
                    return item

    except Exception as e:
        print("Failed to read registry:", e)

    return None

def recv_all(conn):
    buffer = b""
    while True:
        part = conn.recv(4096)
        if not part:
            break
        buffer += part
    return buffer

def main(name, msg, method):
    try:

        if method == "/":
            method = "/"

        ext = Path(method).suffix.lstrip(".")

        result_data = find_user(name)

        if not result_data:
            print("User not found")
            return

        aes_key = os.urandom(32)
        iv = os.urandom(12)

        encrypted_msg = aes_encrypt(aes_key, iv, msg)

        public_key_txt = result_data.get("public_key", "UNKNOWN")
        public_key_txt = public_key_txt.replace("\\n", "\n").strip()

        public_key = serialization.load_pem_public_key(
            public_key_txt.encode("utf-8")
        )

        enc_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        enc_aes_key_b64 = base64.b64encode(enc_aes_key).decode()

        registered_name = result_data.get("fullname")
        ich = result_data.get("ich", "UNKNOWN")
        public_key_txt = result_data.get("public_key", "UNKNOWN")
        destination_ip = result_data.get("ip")
        timestamp = time.time()

        nonce = secrets.token_hex(16)

        body = enc_aes_key_b64 + "|" + base64.b64encode(iv).decode() + "|" + encrypted_msg

        checksum = hmac.new(aes_key, body.encode(), hashlib.sha256).hexdigest()

        dat = nonce + destination_ip + ich + encrypted_msg
        mac = hmac.new(aes_key, dat.encode(), hashlib.sha256).hexdigest()
        count = len(body)

        data_to_sign = nonce + "|" + str(timestamp) + "|" + body

        signature = private_key.sign(
            data_to_sign.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        signature_b64 = base64.b64encode(signature).decode()

        if not destination_ip:
            print("User has no registered IP")
            return
        
        system_name = platform.system()
        agent = f"{CLIENT}/{system_name}"

        packet = idtp_packet(
            ver=VERSION,
            msg_type=TYPE,
            ich=ich,
            to=destination_ip,
            ip_addr=ipa,
            registrant=registered_name,
            agent=agent,
            method=method,
            resource=ext,
            nonce=nonce,
            checksum=checksum,
            public_key=enc_aes_key_b64,
            client_key=my_public_key,
            mac=mac,
            signature=signature_b64,
            timestamp=str(int(timestamp)),
            character=str(count),
            iv=base64.b64encode(iv).decode(),
            data=body
        )

        response = try_send(destination_ip, packet)

        if response and response.get("TYPE") and response.get("DATA"):
            print("Delivery attempt completed")
        else:
            print("Delivery failed")

        return response

    except KeyboardInterrupt:
        print("\nExiting...")
        return

class EditApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.history = []
        self.forward_history = []
        self.current_page = None
        self.title = QLabel("")

        self.setWindowTitle("WWC Scrutari")
        self.resize(1280, 720)

        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        file_menu.addAction("Register").triggered.connect(self.registry)
        file_menu.addAction("Host").triggered.connect(self.host)
        file_menu.addAction("HLRN").triggered.connect(self.hlrn)
        file_menu.addAction("Exit").triggered.connect(self.close)

        wddd_menu = menubar.addMenu("WD3")
        wddd_menu.addAction("Visit on Github").triggered.connect(self.open_web)
        wddd_menu.addAction("Donate").triggered.connect(self.donate)

        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About GlobalBytes").triggered.connect(self.about)
        help_menu.addAction("About PyQt").triggered.connect(self.about_qt)
        help_menu.addAction("WDDD Motto").triggered.connect(self.motto)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.output = QWidget()
        self.output_layout = QVBoxLayout()
        self.output.setLayout(self.output_layout)

        label = QLabel("Recipient:")
        mesg = QLabel("Enter message:")
        fl_method = QLabel("Enter File Method")
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)

        secure_action = QAction(
            QIcon("icons/lock.png"),
            "Secure",
            self
        )

        secure_action = QAction("🔒")

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_page)
        refresh_button.setMaximumWidth(80)

        self.recipient = QLineEdit()
        self.msg = QLineEdit()
        self.method = QLineEdit()

        self.recipient.addAction(
            secure_action,
            QLineEdit.ActionPosition.LeadingPosition
        )

        send_button = QPushButton("Send")

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        back_button.setMaximumWidth(80)

        forward_button = QPushButton("Forward")
        forward_button.clicked.connect(self.go_forward)
        forward_button.setMaximumWidth(80)

        more_button = QToolButton()
        #more_button.setText("⋮")
        more_button.setText("More")

        menu = QMenu()

        about_action = menu.addAction("About")
        about_action.triggered.connect(self.about)

        connection = menu.addAction("Connection")
        connection.triggered.connect(self.connect)

        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        more_button.setMenu(menu)
        more_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        #layout.addWidget(label)
        top_layout = QHBoxLayout()

        #top_layout.addWidget(connection)
        top_layout.addWidget(back_button)
        top_layout.addWidget(forward_button)
        top_layout.addWidget(refresh_button)
        top_layout.addWidget(self.recipient, 1)
        top_layout.addWidget(more_button)

        layout.addLayout(top_layout)

        layout.addWidget(line)

        layout.addWidget(self.output)

        central.setLayout(layout)

    def refresh_page(self):
        if not self.current_page:
            return

        name = self.recipient.text().strip()

        response = main(
            name,
            self.current_page,
            self.current_page
        )

        if response:
            self.show_smrl(
                response.get("DATA", ""),
                name
            )

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
        self.update_time(self.player.position(), duration)

    def position_changed(self, position):
        self.slider.setValue(position)
        self.update_time(position, self.player.duration())

    def update_time(self, pos, dur):
        def fmt(ms):
            s = ms // 1000
            m = s // 60
            s %= 60
            return f"{m:02}:{s:02}"

        self.time.setText(f"{fmt(pos)} / {fmt(dur)}")

    def go_forward(self):
        if not self.forward_history:
            return

        if self.current_page:
            self.history.append(self.current_page)

        next_page = self.forward_history.pop()
        self.current_page = next_page

        name = self.recipient.text().strip()

        response = main(name, next_page, next_page)

        if response:
            self.show_smrl(response.get("DATA", ""), name)

    def go_back(self):

        if not self.history:
            return
        
        if self.current_page:
            self.forward_history.append(self.current_page)

        previous = self.history.pop()
        self.current_page = previous

        name = self.recipient.text().strip()

        self.current_page = previous

        response = main(
            name,
            previous,
            previous
        )

        if response:
            self.show_smrl(
                response.get("DATA", ""),
                name
            )

    def link_click(self, name, filename):
        print("Requesting file:", filename)

        if self.current_page:
            self.history.append(self.current_page)

        self.forward_history.clear()

        self.current_page = filename

        response = main(
            name,
            filename,
            filename
        )

        if response:
            self.show_smrl(
                response.get("DATA", ""),
                name
            )

    def show_smrl(self, data, name):

        data = (
            data
            .replace("<smrl>", "")
            .replace("</smrl>", "")
            .strip()
        )

        try:
            root = ET.fromstring(f"<root>{data}</root>")
        except ET.ParseError:
            print("Invalid SMRL")
            return


        while self.output_layout.count():
            item = self.output_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


        for elem in root:

            tag = elem.tag.lower()
            value = (elem.text or "").strip()

            if tag == "img":

                src = elem.attrib.get("src")

                if src:

                    print("Loading:", src)

                    img_response = main(
                        name,
                        src,
                        src
                    )


                    if img_response:

                        img_data = img_response.get(
                            "DATA",
                            ""
                        )


                        try:

                            image_bytes = base64.b64decode(
                                img_data
                            )

                            pixmap = QPixmap()


                            if pixmap.loadFromData(
                                image_bytes
                            ):

                                label = QLabel()

                                label.setPixmap(
                                    pixmap.scaled(
                                        500,
                                        500,
                                        Qt.AspectRatioMode.KeepAspectRatio
                                    )
                                )

                                self.output_layout.addWidget(
                                    label
                                )


                        except Exception as e:
                            print(
                                "Image error:",
                                e
                            )


                continue

            if tag == "audio":

                src = elem.attrib.get("src")

                if src:

                    print("Loading:", src)

                    audio_response = main(
                        name,
                        src,
                        src
                    )

                    if audio_response:

                        audio_data = audio_response.get("DATA", "")

                        try:

                            audio_bytes = base64.b64decode(audio_data)

                            temp = tempfile.NamedTemporaryFile(
                                delete=False,
                                suffix=".mp3"
                            )

                            temp.write(audio_bytes)
                            temp.close()

                            player = QMediaPlayer(self)
                            output = QAudioOutput(self)
                            output.setVolume(1.0)

                            player.setAudioOutput(output)
                            player.setSource(
                                 QUrl.fromLocalFile(temp.name)
                            )


                # Controls
                            play = QPushButton("▶")
                            pause = QPushButton("⏸")
                            stop = QPushButton("⏹")

                            slider = QSlider(Qt.Orientation.Horizontal)
                            slider.setRange(0, 0)

                            time_label = QLabel("00:00 / 00:00")

                            player.durationChanged.connect(
                                lambda duration: slider.setRange(0, duration)
                            )

                            player.positionChanged.connect(
                                lambda position: (
                                    slider.setValue(position),
                                    time_label.setText(
                                        f"{position//60000:02}:{(position//1000)%60:02} / "
                                        f"{player.duration()//60000:02}:{(player.duration()//1000)%60:02}"
                                    )
                                )
                            )

                            play.clicked.connect(player.play)
                            pause.clicked.connect(player.pause)
                            stop.clicked.connect(player.stop)

                            play.setFixedWidth(40)
                            pause.setFixedWidth(40)
                            stop.setFixedWidth(40)
                            slider.setFixedWidth(180)
                            stop.setFixedWidth(40)


                            row = QHBoxLayout()
                            row.addWidget(play)
                            row.addWidget(pause)
                            row.addWidget(stop)
                            row.addWidget(slider)
                            row.addWidget(time_label)

                            container = QWidget()
                            container.setLayout(row)

                            self.output_layout.addWidget(container)


                # Keep alive
                            if not hasattr(self, "players"):
                                self.players = []

                            self.players.append(
                                (player, output, temp.name)
                            )

                        except Exception as e:
                            print("Audio error:", e)

                continue

            if not value:
                continue


            lbl = QLabel(value)
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

            if tag == "head1":
                lbl.setStyleSheet(
                    "font-size:20px;font-weight:bold;"
                )

            elif tag == "title":
                self.title.setText(value)

            elif tag == "link":

                redir = elem.attrib.get("redir")

                lbl.setStyleSheet(
                    "color:blue;text-decoration:underline;"
                )

                lbl.setCursor(
                    Qt.CursorShape.PointingHandCursor
                )

                if redir:
                    lbl.mousePressEvent = (
                        lambda e, f=redir:
                        self.link_click(name, f)
                    )


            self.output_layout.addWidget(lbl)

    def send(self):
        name = self.recipient.text().strip()
        msg = self.msg.text().strip()
        method = self.method.text().strip()

        self.current_page = method
        self.history.clear()

        response = main(name, msg, method)

        if response:
            while self.output_layout.count():
                item = self.output_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                    
            data = response.get("DATA", "")
            resor = response.get("RESOURCE", "")

            print("RAW RESPONSE:\n", resor)

            resor = resor.replace("\\", "/").strip()

            ext = Path(resor).suffix.lower().lstrip(".")

            ext = response.get("TYPE", "").lower()

            print("DETECTED EXT:", ext)

            if ext == "smrl":

    # clean root wrapper safely
                data = data.replace("<smrl>", "").replace("</smrl>", "").strip()

                try:
                    root = ET.fromstring(f"<root>{data}</root>")
                except ET.ParseError:
                    root = None

                if root is None:
                    return

    # clear layout
                while self.output_layout.count():
                    item = self.output_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

    # read in order as it appears in XML
                for elem in root:
                    tag = elem.tag.lower()
                    value = (elem.text or "").strip()

                    if tag == "img":

                        src = elem.attrib.get("src")

                        if src:

                            print("Loading:", src)

                            img_response = main(
                                name,
                                src,
                                src
                            )


                            if img_response:

                                img_data = img_response.get(
                                    "DATA",
                                    ""
                                )


                                try:

                                    image_bytes = base64.b64decode(
                                        img_data
                                    )

                                    pixmap = QPixmap()


                                    if pixmap.loadFromData(
                                        image_bytes
                                    ):

                                        label = QLabel()

                                        label.setPixmap(
                                            pixmap.scaled(
                                                500,
                                                500,
                                                Qt.AspectRatioMode.KeepAspectRatio
                                            )
                                        )

                                        self.output_layout.addWidget(
                                            label
                                        )


                                except Exception as e:
                                    print(
                                        "Image error:",
                                        e
                                    )

                            continue

                    if tag == "audio":

                        src = elem.attrib.get("src")

                        if src:

                            print("Loading:", src)

                            audio_response = main(
                                name,
                                src,
                                src
                            )

                            if audio_response:

                                audio_data = audio_response.get("DATA", "")

                                try:

                                    audio_bytes = base64.b64decode(audio_data)

                                    temp = tempfile.NamedTemporaryFile(
                                        delete=False,
                                        suffix=".mp3"
                                    )

                                    temp.write(audio_bytes)
                                    temp.close()

                                    player = QMediaPlayer(self)
                                    output = QAudioOutput(self)
                                    output.setVolume(1.0)

                                    player.setAudioOutput(output)
                                    player.setSource(
                                        QUrl.fromLocalFile(temp.name)
                                    )


                # Controls
                                    play = QPushButton("▶")
                                    pause = QPushButton("⏸")
                                    stop = QPushButton("⏹")

                                    slider = QSlider(Qt.Orientation.Horizontal)
                                    slider.setRange(0, 0)

                                    time_label = QLabel("00:00 / 00:00")

                                    player.durationChanged.connect(
                                        lambda duration: slider.setRange(0, duration)
                                    )

                                    player.positionChanged.connect(
                                        lambda position: (
                                            slider.setValue(position),
                                            time_label.setText(
                                                f"{position//60000:02}:{(position//1000)%60:02} / "
                                                f"{player.duration()//60000:02}:{(player.duration()//1000)%60:02}"
                                            )
                                        )
                                    )

                                    slider.sliderMoved.connect(
                                        player.setPosition
                                    )

                                    play.clicked.connect(player.play)
                                    pause.clicked.connect(player.pause)
                                    stop.clicked.connect(player.stop)

                                    slider.setFixedWidth(180)
                                    stop.setFixedWidth(40)
                                    play.setFixedWidth(40)
                                    pause.setFixedWidth(40)

                                    row = QHBoxLayout()
                                    row.addWidget(play)
                                    row.addWidget(pause)
                                    row.addWidget(stop)
                                    row.addWidget(slider)
                                    row.addWidget(time_label)

                                    container = QWidget()
                                    container.setLayout(row)

                                    self.output_layout.addWidget(container)


                # Keep alive
                                    if not hasattr(self, "players"):
                                        self.players = []

                                    self.players.append(
                                        (player, output, temp.name)
                                    )

                                except Exception as e:
                                    print("Audio error:", e)

                        continue

                    if not value:
                        continue

                    lbl = QLabel(value)
                    lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

                    if tag == "head1":
                        lbl.setStyleSheet("font-size:20px; font-weight:bold;")
                        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

                    elif tag == "title":
                        self.title.setText(value)

                    elif tag == "image":
                        img_data = response.get("DATA", "")

                        image_bytes = base64.b64decode(img_data)

                        pixmap = QPixmap()
                        pixmap.loadFromData(image_bytes)

                        img_label = QLabel()
                        img_label.setPixmap(
                            pixmap.scaled(
                                500,
                                500,
                                Qt.AspectRatioMode.KeepAspectRatio
                            )
                        )

                        self.output_layout.addWidget(img_label)

                    elif tag == "link":
                        redir = elem.attrib.get("redir")
                        lbl.setStyleSheet("color:blue;")
                        lbl.setCursor(
                            Qt.CursorShape.PointingHandCursor
                        )
                        if redir:
                            lbl.mousePressEvent = (
                                lambda e, f=redir:
                                self.link_click(name, f)
                            )

                    self.output_layout.addWidget(lbl)

        else:
            if hasattr(self, "output_layout"):
                while self.output_layout.count():
                    item = self.output_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

    def connect(self):
        msg = QMessageBox(self)
        msg.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )

        msg.setWindowTitle("IDTP Version 0.01")

        msg.setText(
            "IDTP Version 0.1\n\n"
            "Internet Data Transmission Protocol \n\n"
            "IDTP is secure protocol.\n"
            "Your data is encrypted"
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

    def open_wrs(self):
        try:
            subprocess.Popen(["python", "wrs.py"])
        except Exception as e:
            print("Failed to launch wrs.py:", e)

    def open_global(self):
        try:
            subprocess.Popen(["python", "global.py"])
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

    def motto(self):
        mt = QMessageBox(self)
        mt.setWindowTitle("WRANS Version 0.001")
        mt.setText(
            "About WDDD\n\n"
            "Global Information Sharing System\n\n"
        )

        map = QPixmap("motto.jpg")

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
        ms.setWindowTitle("WRANS Version 0.001")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditApp()
    window.show()

    sys.exit(app.exec())
