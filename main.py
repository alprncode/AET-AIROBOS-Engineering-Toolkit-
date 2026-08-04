import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QHBoxLayout, QListWidget, QStackedWidget, QLabel)

from modules.unit_converter import UnitConverterWidget
from modules.flight_time_calculator import FlightTimeCalculatorWidget
from modules.crc_calculator import CRCCalculatorWidget
from modules.network_test import NetworkTestWidget
from modules.coordinate_converter import CoordinateConverterWidget
from modules.serial_terminal import SerialTerminalWidget
from modules.hex_viewer import HexViewerWidget

class AETDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AIROBOS Engineering Toolkit")
        self.setGeometry(100, 100, 950, 600) # Hex ekranı sığsın diye genişliği biraz artırdık
        
        merkezi_widget = QWidget()
        self.setCentralWidget(merkezi_widget)
        
        ana_duzen = QHBoxLayout(merkezi_widget)
        
        self.sol_menu = QListWidget()
        self.sol_menu.setFixedWidth(200)
        self.sol_menu.addItems([
            "Dashboard", 
            "ULog Analyzer", 
            "CAN Log Viewer", 
            "Serial Terminal", 
            "Network Test", 
            "RTSP Test", 
            "CRC Calculator", 
            "Coordinate Converter", 
            "Hex Viewer", 
            "Unit Converter", 
            "Flight Time Calculator"
        ])
        
        self.icerik_alani = QStackedWidget()
        
        # İndeks 0
        ilk_sayfa = QLabel("AIROBOS AET Sistemine Hoş Geldiniz.\nLütfen soldaki menüden bir araç seçin.")
        ilk_sayfa.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        self.icerik_alani.addWidget(ilk_sayfa) 
        
        # Modüller (Sırasıyla İndeks 1'den 7'ye)
        self.cevirici_modulu = UnitConverterWidget()
        self.icerik_alani.addWidget(self.cevirici_modulu) 
        
        self.ucus_hesaplayici = FlightTimeCalculatorWidget()
        self.icerik_alani.addWidget(self.ucus_hesaplayici)
        
        self.crc_hesaplayici = CRCCalculatorWidget()
        self.icerik_alani.addWidget(self.crc_hesaplayici)
        
        self.ag_testi = NetworkTestWidget()
        self.icerik_alani.addWidget(self.ag_testi)
        
        self.koordinat_cevirici = CoordinateConverterWidget()
        self.icerik_alani.addWidget(self.koordinat_cevirici)
        
        self.seri_terminal = SerialTerminalWidget()
        self.icerik_alani.addWidget(self.seri_terminal)
        
        self.hex_goruntuleyici = HexViewerWidget()
        self.icerik_alani.addWidget(self.hex_goruntuleyici) 
        
        ana_duzen.addWidget(self.sol_menu)
        ana_duzen.addWidget(self.icerik_alani)

        self.sol_menu.itemClicked.connect(self.sayfa_degistir)

    def sayfa_degistir(self, item):
        secilen_isim = item.text()
        if secilen_isim == "Dashboard":
            self.icerik_alani.setCurrentIndex(0)
        elif secilen_isim == "Unit Converter":
            self.icerik_alani.setCurrentIndex(1)
        elif secilen_isim == "Flight Time Calculator":
            self.icerik_alani.setCurrentIndex(2)
        elif secilen_isim == "CRC Calculator":
            self.icerik_alani.setCurrentIndex(3)
        elif secilen_isim == "Network Test":
            self.icerik_alani.setCurrentIndex(4)
        elif secilen_isim == "Coordinate Converter":
            self.icerik_alani.setCurrentIndex(5)
        elif secilen_isim == "Serial Terminal":
            self.icerik_alani.setCurrentIndex(6)
        elif secilen_isim == "Hex Viewer":
            self.icerik_alani.setCurrentIndex(7)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = AETDashboard()
    pencere.show()
    sys.exit(app.exec())