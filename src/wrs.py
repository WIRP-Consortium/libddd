import sys
import os
import json
import socket
import threading
import time
import hashlib
import subprocess
import webbrowser
import traceback
import secrets
import requests
from collections import deque

from cryptography.fernet import Fernet
from find import get_codes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from Crypto.PublicKey import RSA
from PyQt6.QtGui import QIcon

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QLineEdit,
    QMessageBox,
    QComboBox,
    QFileDialog,
    QTextEdit
)
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
# CONFIG

PORT = 9000

DATA_DIR = "data"

CHAIN_FILE = os.path.join(DATA_DIR, "chain.dat")
REGISTRY_FILE = os.path.join(DATA_DIR, "registry.dat")
BLOCKS_FILE = os.path.join(DATA_DIR, "blocks.dat")
INDEX_DIR = os.path.join(DATA_DIR, "indexes")
ICH_FILE = os.path.join(DATA_DIR, "internet.ich")
PEERS_FILE = os.path.join(DATA_DIR, "peers.json")
LICENSE_FILE = os.path.join(DATA_DIR, "license.key")
VERSION = "0.001"

DEFAULT_PEERS = []

ALLOWED_EXTENSIONS = [
    ".rev",
    ".ind",
    ".pri",
    ".gov",
    ".wd",
    ".xyz",
    ".shop",
    ".home",
    ".in",
    ".us",
    ".mx",
    ".ae"
]

EXPIRY = [
    ("1year", 365 * 24 * 60 * 60),
    ("2year", 2 * 365 * 24 * 60 * 60),
    ("4year", 4 * 365 * 24 * 60 * 60),
    ("5year", 5 * 365 * 24 * 60 * 60),
    ("10year", 10 * 365 * 24 * 60 * 60),
]

# INIT
registry_lock = threading.Lock()
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

if not os.path.exists(REGISTRY_FILE):
    open(REGISTRY_FILE, "w").close()

if not os.path.exists(PEERS_FILE):
    with open(PEERS_FILE, "w") as f:
        json.dump(DEFAULT_PEERS, f)

if not os.path.exists(BLOCKS_FILE):
    open(BLOCKS_FILE, "w").close()
# LICENSE

def load_license():
    with open(LICENSE_FILE, "rb") as f:
        return f.read()

def safe_write(path, data):

    tmp = path + ".tmp"

    with open(tmp, "w", encoding="utf-8") as f:
        f.write(data)

    os.replace(tmp, path)

def register_user(ich_hash):
    country_code, continent_code = get_codes()
    return country_code

def load_registry():

    records = []

    if not os.path.exists(REGISTRY_FILE):
        return records

    try:

        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                try:
                    records.append(json.loads(line))

                except:
                    continue

    except:
        pass

    return records

def load_ich():

    if not os.path.exists(ICH_FILE):
        raise Exception("internet.ich not found")

    if not os.path.exists(LICENSE_FILE):
        raise Exception("license.key not found")

    key = load_license()

    cipher = Fernet(key)

    with open(ICH_FILE, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    data = json.loads(decrypted_data.decode("utf-8"))

    return data["public"]

def initial_sync():
    for host, port in list(PEERS):
        download_chain_from_peer(host, port)


    for line in raw_chain.splitlines():
        try:
            obj = json.loads(line.strip())
            key = obj["name"] + obj["ext"]

            if key not in existing:
                with open(REGISTRY_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(obj) + "\n")
                existing.add(key)

        except:
            continue


# PEERS

def load_peers():

    try:

        with open(PEERS_FILE, "r") as f:
            raw = json.load(f)

        peers = set()

        for host, port in raw:
            peers.add((host, int(port)))

        peers.add(("127.0.0.1", PORT))

        return peers

    except:
        return set(DEFAULT_PEERS)

PEERS = load_peers()

def save_peers():

    try:

        with open(PEERS_FILE, "w") as f:
            json.dump(list(PEERS), f)

    except:
        pass

def add_peer(host, port):

    global PEERS

    peer = (host, int(port))

    if peer not in PEERS:
        PEERS.add(peer)
        save_peers()

# HASH

def generate_64bit_hash(name, ext):

    value = f"{name}{ext}{time.time()}"

    return hashlib.sha256(value.encode()).hexdigest()[:32]

# EXPIRY

def get_expiry_seconds(label):

    for name, seconds in EXPIRY:

        if name == label:
            return seconds

    return None

# CHECK LOCAL DUPLICATE

def local_name_exists(entry):

    try:

        with open(REGISTRY_FILE, "r", encoding="utf-8", errors="ignore") as f:

            for line in f:

                try:

                    obj = json.loads(line.strip())

                    existing = obj.get("name", "") + obj.get("ext", "")

                    if existing == entry:
                        return True

                except:
                    continue

    except:
        pass

    return False

# INDEX FILE
def get_next_index_file():

    files = os.listdir(INDEX_DIR)

    numbers = []

    for f in files:

        if f.startswith("index_") and f.endswith(".dat"):

            try:
                num = int(f.replace("index_", "").replace(".dat", ""))
                numbers.append(num)

            except:
                pass

    next_num = max(numbers, default=0) + 1

    return os.path.join(INDEX_DIR, f"index_{next_num}.dat")

# SAVE REGISTRATION
def is_online():
    try:
        requests.get("https://ipwho.is/", timeout=3)
        return True
    except requests.RequestException:
        return False
    
def compute_record_hash(record):
    safe_copy = dict(record)
    safe_copy.pop("signature", None)

    encoded = json.dumps(safe_copy, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()

request_times = deque(maxlen=1000)

def update_traffic():
    now = time.time()
    request_times.append(now)

def get_difficulty():
    """
    Adaptive difficulty based on requests per second
    """
    now = time.time()

    # keep only last 10 seconds
    recent = [t for t in request_times if now - t <= 10]

    rps = len(recent) / 10

    if rps < 5:
        return 3
    elif rps < 20:
        return 4
    elif rps < 50:
        return 5
    else:
        return 6
    
def verify_pow(data, nonce, difficulty):
    target = "0" * difficulty
    h = hashlib.sha256(f"{data}{nonce}".encode()).hexdigest()
    return h.startswith(target)

def save_registration(data):

    from find import get_codes
    country_code, continent_code, ip = get_codes()

    entry = data["name"] + data["ext"]

    hash64 = generate_64bit_hash(data["name"], data["ext"])

    fulname = f"{data['name']}{hash64}{data['ext']}"
    fullname = fulname.lower()
    wd3_name = f"{fullname}"

    private_key = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key.public_key()

    # Serialize public key (ECC ONLY)
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    # sign FULL identity-relevant data (better cryptographically correct)
    message = wd3_name.encode("utf-8")

    signature = private_key.sign(
        message,
        ec.ECDSA(hashes.SHA256())
    ).hex()

    try:
        ich_hash = load_ich()
    except Exception:
        return "ICH ERROR"

    with registry_lock:
        records = load_registry()

    block_height = len(records) + 1

    key = RSA.generate(2048)

    asprivatekey = key.export_key().decode("utf-8")
    aspublickey = key.publickey().export_key().decode("utf-8")

    record = {
        "tp": "doc",
        "ext": data["ext"],
        "ich": ich_hash,
        "timestamp": data["timestamp"],
        "expiry": data["expiry"],
        "fullname": wd3_name,
        "sign": signature,
        "public_key": aspublickey,
        "ip": ip,
        "bh": block_height
    }

    with registry_lock:
        records = load_registry()
        records.append(record)

        output = "\n".join(json.dumps(r) for r in records)
        safe_write(REGISTRY_FILE, output)

    index_file = get_next_index_file()

    with open(index_file, "w", encoding="utf-8") as f:
        json.dump({
            "fullname": fullname,
            "hash": hash64,
            "name": data["name"],
            "ich": ich_hash,
            "type": "doc",
            "public_key": public_bytes,
            "private_key": private_bytes,
            "asymmetric_private": asprivatekey,
            "asymmetric_public": aspublickey,
            "signature": signature,
            "expiry": data["expiry"],
            "block_height": block_height
        }, f)

    return record

# BROADCAST

def broadcast(data, exclude=None):

    msg = json.dumps(data)

    for host, port in list(PEERS):

        if exclude and (host, port) == exclude:
            continue

        try:

            s = socket.socket()
            s.settimeout(3)

            s.connect((host, port))

            s.send(msg.encode())

            s.close()

        except:
            pass

# PEER DISCOVERY

def peer_discovery():

    while True:

        for host, port in list(PEERS):

            try:

                s = socket.socket()
                s.settimeout(3)

                s.connect((host, port))

                payload = {
                    "type": "peer_request"
                }

                s.send(json.dumps(payload).encode())

                raw = s.recv(65536).decode()

                s.close()

                peers = json.loads(raw)

                for p_host, p_port in peers:
                    add_peer(p_host, p_port)

            except:
                pass

        time.sleep(15)


def download_chain_from_peer(host, port):
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((host, port))

        s.send(json.dumps({"type": "get_registry"}).encode())

        raw = s.recv(10_000_000).decode()
        s.close()

        if raw:
            merge_registry(raw)

    except Exception:
        pass

def peer_resync():

    while True:

        for host, port in list(PEERS):

            download_chain_from_peer(host, port)

        time.sleep(60)

def merge_registry(raw_registry):
    with registry_lock:
        existing = load_registry()

        seen = set()
        for r in existing:
            key = r.get("fullname") or r.get("record_hash")
            if key:
                seen.add(key)

        for line in raw_registry.splitlines():
            try:
                obj = json.loads(line.strip())

                key = obj.get("fullname") or obj.get("record_hash")
                if not key:
                    continue

                if key not in seen:
                    existing.append(obj)
                    seen.add(key)

            except:
                continue

        safe_write(REGISTRY_FILE,
            "\n".join(json.dumps(r) for r in existing)
        )
# SERVER

def server():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT))
    s.listen(10)

    print(f"NODE RUNNING ON {PORT}")

    while True:
        client = None
        try:
            client, addr = s.accept()
            client.settimeout(5)

            add_peer(addr[0], PORT)

            raw = client.recv(65536).decode(errors="ignore").strip()

            if not raw:
                client.send(b"EMPTY REQUEST")
                client.close()
                continue

            try:
                data = json.loads(raw)
            except Exception as e:
                client.send(f"INVALID JSON: {e}".encode())
                client.close()
                continue

            req_type = data.get("type")

            # GET REGISTRY
            if req_type == "get_registry":
                try:
                    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                        client.send(f.read().encode())
                except Exception as e:
                    client.send(f"ERROR: {e}".encode())

                client.close()
                continue

            # PEER REQUEST
            if req_type == "peer_request":
                try:
                    client.send(json.dumps(list(PEERS)).encode())
                except Exception as e:
                    client.send(f"ERROR: {e}".encode())

                client.close()
                continue

            # SYNC
            if req_type == "sync":
                try:
                    record = data.get("record")

                    if record:
                        with registry_lock:
                            records = load_registry()

                            key = record.get("fullname")
                            exists = any(r.get("fullname") == key for r in records)

                            if not exists:
                                records.append(record)
                                safe_write(
                                    REGISTRY_FILE,
                                    "\n".join(json.dumps(r) for r in records)
                                )

                    client.send(b"SYNCED")

                except Exception as e:
                    client.send(f"SYNC ERROR: {e}".encode())

                client.close()
                continue

            if req_type == "register":
                try:
                    if data.get("ext") not in ALLOWED_EXTENSIONS:
                        client.send(b"INVALID EXTENSION")
                        client.close()
                        continue

                    country_code, continent_code, ip = get_codes()

                    record = save_registration(data)

                    broadcast(
                        {"type": "sync", "record": record},
                        exclude=addr
                    )

                    client.send(json.dumps({
                        "status": "ok",
                        "fullname": record["fullname"]
                    }).encode())
                    client.close()  
                    continue

                except Exception as e:
                    print("REGISTER ERROR:", repr(e))
                    try:
                        client.send(f"ERROR: {e}".encode())
                    except:
                        pass
                    client.close()
                    continue

            client.send(b"UNKNOWN REQUEST")
            client.close()

        except Exception as e:
            print("SERVER LOOP ERROR:", repr(e))
            traceback.print_exc()

            try:
                if client:
                    client.send(f"SERVER ERROR: {e}".encode())
                    client.close()
            except:
                pass

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class App(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("GlobalBytes")
        self.setWindowIcon(QIcon(resource_path("assets/wd3.ico")))

        self.resize(1280, 700)

        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        select_action = file_menu.addAction("Select Index File")
        select_action.triggered.connect(self.select_file)

        edit_action = file_menu.addAction("Edit Name")
        edit_action.triggered.connect(self.open_edit)

        host_action = file_menu.addAction("Host")
        host_action.triggered.connect(self.open_host)

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        tool_menu = menubar.addMenu("Tool")

        mine = tool_menu.addAction("Start Mining")
        mine.triggered.connect(self.mining)

        maintain = tool_menu.addAction("Start Mining")
        maintain.triggered.connect(self.maintain)

        wddd_menu = menubar.addMenu("WD3")

        wddd = wddd_menu.addAction("Visit on Github")
        wddd.triggered.connect(self.open_web)

        donate = wddd_menu.addAction("Donate")
        donate.triggered.connect(self.donate)

        help_menu = menubar.addMenu("Help")

        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.about)

        about_action = help_menu.addAction("About Index file")
        about_action.triggered.connect(self.about_app)

        central = QWidget()

        if not os.path.exists(REGISTRY_FILE):
            self.label = QLabel()
            self.label.setText("no registry file")
            return

        self.setCentralWidget(central)

        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("WD3 REGISTRATION")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:22px;font-weight:bold;")

        layout.addWidget(title)

        sect = QLabel("WORLD DISTRIBUTED DATA DIRECTORY")
        sect.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sect.setStyleSheet("font-size:18px;font-weight:bold;")

        if not is_online():
            self.label = QLabel()
            self.label.setText("Check Your Internet Connection")
            central.setLayout(layout)
            return

        layout.addWidget(sect)

        layout.addWidget(QLabel("Name"))

        self.name = QLineEdit()

        layout.addWidget(self.name)

        layout.addWidget(QLabel("Extension"))

        self.ext = QComboBox()

        self.ext.addItems(ALLOWED_EXTENSIONS)

        layout.addWidget(self.ext)

        layout.addWidget(QLabel("Select Expiry"))

        self.exp = QComboBox()

        self.exp.addItems([name for name, _ in EXPIRY])

        layout.addWidget(self.exp)

        btn = QPushButton("Register")

        btn.clicked.connect(self.register_name)

        layout.addWidget(btn)

        self.status = QTextEdit()

        self.status.setReadOnly(True)

        layout.addWidget(self.status)

        central.setLayout(layout)

    def register_name(self):

        threading.Thread(
            target=self._register_worker,
            daemon=True
        ).start()

    def _register_worker(self):
        name = self.name.text().strip()
        ext = self.ext.currentText()
        exp_label = self.exp.currentText()

        if not name:
            self.status.append("Enter Name")
            return

        expiry_seconds = get_expiry_seconds(exp_label)

        if expiry_seconds is None:
            self.status.append("Invalid expiry")
            return

        created_time = int(time.time())

        self.status.append("Registering...")

        hash64 = generate_64bit_hash(name, ext)
        fullname = f"{name}{hash64}{ext}"

        payload = {
            "type": "register",
            "name": name,
            "ext": ext,
            "fullname": fullname,
            "expiry": created_time + expiry_seconds,
            "timestamp": created_time
        }

        response = self.send_to_network(payload)
        try:
            parsed = response if isinstance(response, dict) else json.loads(response)

            if parsed.get("status") == "ok":
                self.status.append(f"✅ Registered: {parsed.get('fullname')}")
            else:
                self.status.append(f"❌ Error: {parsed}")

        except Exception:
            
            self.status.append(f"⚠️ Raw response: {response}")

    def send_to_network(self, payload):
        data = json.dumps(payload)

        last_error = None

        for host, port in list(PEERS):
            try:
                s = socket.socket()
                s.settimeout(5)

                print(f"Connecting to {host}:{port}")

                s.connect((host, port))
                s.send(data.encode())

                res = b""
                while True:
                    part = s.recv(4096)
                    if not part:
                        break
                    res += part

                s.close()

                response = res.decode(errors="ignore")
                print("Received:", response)

                try:
                    parsed = json.loads(response)

                    return parsed if isinstance(parsed, dict) else {"raw": response}

                except:
                    last_error = response
                    continue

            except Exception as e:
                print("Connection error:", e)
                last_error = str(e)

        return {
            "status": "error",
            "message": last_error or "No peers available"
        }
                

    def select_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Index File",
            INDEX_DIR,
            "*.dat"
        )

        if not file_path:
            return

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        QMessageBox.information(self, "INDEX CONTENT", content)

    def open_edit(self):

        subprocess.Popen([sys.executable, "edit.py"])

    def open_host(self):

        subprocess.Popen([sys.executable, "global.py"])

    def mining(self):

        subprocess.Popen([sys.executable, "miner_ui.py"])

    def open_web(self):

        webbrowser.open_new_tab("https://github.com/WIRP-Consortium")

    def donate(self):

        subprocess.Popen([sys.executable, "donate.py"])

    def maintain(self):
        subprocess.Popen([sys.executable, "clean.py"])

    def about(self):

        QMessageBox.information(
            self,
            "WRANS Version 0.001",
            "WD3 Version 0.001\n"
            "World Decentralised Document Data is a simple\n"
            "document sharing protocol that helps host your docs\n"
            "anonymously on the internet"
        )

    def about_app(self):

        QMessageBox.information(
            self,
            "About",
            "WRANS System\nEach index file stores only one name"
        )

threading.Thread(target=server, daemon=True).start()

threading.Thread(target=peer_discovery, daemon=True).start()

threading.Thread(target=peer_resync, daemon=True).start()

app = QApplication(sys.argv)

window = App()

window.show()

sys.exit(app.exec())
