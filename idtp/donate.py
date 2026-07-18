import sys
import webbrowser
import qrcode

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QHBoxLayout
)

from PyQt6.QtGui import QGuiApplication, QPixmap
from PyQt6.QtCore import Qt

class ThankYouWindow(QMainWindow):
    def __init__(self, msg="Thank you ❤️"):
        super().__init__()

        self.setWindowTitle("Thank You")
        self.resize(350, 180)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()

        label = QLabel(msg)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)

        btn = QPushButton("Close")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)

        central.setLayout(layout)

class DonateWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Donate Bitcoin")
        self.resize(1280, 720)

        self.address = "bc1qc9t0p20xkpmsx40zfcadlczlhmj8chfre4nz7c"
        self.xmr_address = "8AarbY63XYrdDJVD2DRZPKFFQeiH4ekYqibANnaU2wGeBKoLUpqGnUkN3xyfMj2uQPfxAcYPhuzfCcWd7VPHgSwd8ovYKYZ"
        self.btc_rate_usd = 60000

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Support the Project")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        main_layout.addWidget(title)

        sect = QLabel("WORLD DECENTRALISED DOCUMENT DATA")
        sect.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sect.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(sect)

        addr = QLabel(self.address)
        addr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(addr)

        section1 = QLabel("Scan this wallet QR")
        section1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(section1)

        self.qr_normal = QLabel()
        self.qr_normal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.qr_normal)

        self.generate_qr(self.address, self.qr_normal)
      
        section2 = QLabel("Select amount (USD → BTC QR)")
        section2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(section2)

        self.amount_box = QComboBox()
        self.amount_box.addItems(["5 USD", "10 USD", "20 USD", "50 USD"])
        main_layout.addWidget(self.amount_box)

        self.qr_payment = QLabel()
        self.qr_payment.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.qr_payment)

        gen_btn = QPushButton("Generate Payment QR")
        gen_btn.clicked.connect(self.generate_payment_qr)
        main_layout.addWidget(gen_btn)

        btn_row = QHBoxLayout()

        copy_btn = QPushButton("Copy Address")
        copy_btn.clicked.connect(self.copy_address)

        electrum_btn = QPushButton("Open ")
        electrum_btn.clicked.connect(self.open_electrum)

        btn_row.addWidget(copy_btn)
        btn_row.addWidget(electrum_btn)

        main_layout.addLayout(btn_row)

        xmr_section = QLabel("Monero (XMR) Donation")
        xmr_section.setAlignment(Qt.AlignmentFlag.AlignCenter)
        xmr_section.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(xmr_section)

        self.qr_xmr = QLabel()
        self.qr_xmr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.qr_xmr)

        self.generate_qr(f"monero:{self.xmr_address}", self.qr_xmr)

        xmr_btn = QPushButton("Copy XMR Address")
        xmr_btn.clicked.connect(self.copy_xmr_address)
        main_layout.addWidget(xmr_btn)

        central.setLayout(main_layout)

    def generate_qr(self, data, label_widget):
        img = qrcode.make(data)
        img.save("qr.png")

        pix = QPixmap("qr.png")
        label_widget.setPixmap(
            pix.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        )

    def copy_xmr_address(self):
        QGuiApplication.clipboard().setText(self.xmr_address)
        self.show_thanks("XMR address copied")

    def generate_xmr_payment_qr(self, xmr_amount):
        uri = f"monero:{self.xmr_address}?tx_amount={xmr_amount}"
        self.generate_qr(uri, self.qr_xmr)

    def copy_address(self):
        QGuiApplication.clipboard().setText(self.address)
        self.show_thanks("Address copied")

    def open_electrum(self):
        webbrowser.open(f"bitcoin:{self.address}")
        self.show_thanks("Opened in Electrum")

    def generate_payment_qr(self):
        usd = int(self.amount_box.currentText().split()[0])
        btc = usd / self.btc_rate_usd

        uri = f"bitcoin:{self.address}?amount={btc:.8f}"

        self.generate_qr(uri, self.qr_payment)

        self.show_thanks(f"Payment QR generated for ${usd}")
      
    def show_thanks(self, msg):
        self.win = ThankYouWindow(msg)
        self.win.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DonateWindow()
    window.show()
    sys.exit(app.exec())
