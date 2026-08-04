import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QHBoxLayout, QVBoxLayout, QListWidget, 
                               QStackedWidget, QLabel)
from PySide6.QtCore import Qt

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
        self.setWindowTitle("AIROBOS Engineering Toolkit v1.0")
        self.setGeometry(100, 100, 1000, 650) # Ekranı ferahlatmak için biraz büyüttük
        
        # --- GLOBAL TASARIM (QSS) ---
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QListWidget {
                background-color: #1e1e1e;
                border: none;
                border-right: 1px solid #333;
                font-size: 15px;
                outline: none;
            }
            QListWidget::item {
                padding: 15px 10px;
                border-bottom: 1px solid #2a2a2a;
            }
            QListWidget::item:hover {
                background-color: #2c3e50;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
                border-left: 4px solid #00c3ff;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005f9e;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #444;
                padding: 5px;
                border-radius: 3px;
                color: white;
            }
        """)
        
        merkezi_widget = QWidget()
        self.setCentralWidget(merkezi_widget)
        
        ana_duzen = QHBoxLayout(merkezi_widget)
        ana_duzen.setContentsMargins(0, 0, 0, 0) # Kenar boşluklarını sıfırladık
        ana_duzen.setSpacing(0)
        
        # SOL MENÜ
        self.sol_menu = QListWidget()
        self.sol_menu.setFixedWidth(220)
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
        self.icerik_alani.setStyleSheet("background-color: #181818; padding: 20px;")
        
        # --- YENİ DASHBOARD (İLK AÇILIŞ EKRANI) ---
        dashboard_widget = QWidget()
        dash_layout = QVBoxLayout(dashboard_widget)
        
        dash_baslik = QLabel("AIROBOS\nENGINEERING TOOLKIT")
        dash_baslik.setAlignment(Qt.AlignCenter)
        dash_baslik.setStyleSheet("font-size: 32px; font-weight: 900; color: #00c3ff; letter-spacing: 2px;")
        
        dash_alt_baslik = QLabel("Sistem durumu: Aktif | Modüller yüklendi...")
        dash_alt_baslik.setAlignment(Qt.AlignCenter)
        dash_alt_baslik.setStyleSheet("font-size: 14px; color: #888; margin-bottom: 20px;")
        
        dash_bilgi = QLabel("Lütfen çalışmak istediğiniz aracı sol menüden seçin.\nTüm modüller endüstriyel standartlarda geliştirilmiştir.")
        dash_bilgi.setAlignment(Qt.AlignCenter)
        dash_bilgi.setStyleSheet("font-size: 16px; color: #bbb; line-height: 1.5;")
        
        dash_layout.addStretch()
        dash_layout.addWidget(dash_baslik)
        dash_layout.addWidget(dash_alt_baslik)
        dash_layout.addWidget(dash_bilgi)
        dash_layout.addStretch()
        
        self.icerik_alani.addWidget(dashboard_widget) # İndeks 0
        
        # --- MODÜLLER ---
        self.cevirici_modulu = UnitConverterWidget()
        self.icerik_alani.addWidget(self.cevirici_modulu) # İndeks 1
        
        self.ucus_hesaplayici = FlightTimeCalculatorWidget()
        self.icerik_alani.addWidget(self.ucus_hesaplayici) # İndeks 2
        
        self.crc_hesaplayici = CRCCalculatorWidget()
        self.icerik_alani.addWidget(self.crc_hesaplayici) # İndeks 3
        
        self.ag_testi = NetworkTestWidget()
        self.icerik_alani.addWidget(self.ag_testi) # İndeks 4
        
        self.koordinat_cevirici = CoordinateConverterWidget()
        self.icerik_alani.addWidget(self.koordinat_cevirici) # İndeks 5
        
        self.seri_terminal = SerialTerminalWidget()
        self.icerik_alani.addWidget(self.seri_terminal) # İndeks 6
        
        self.hex_goruntuleyici = HexViewerWidget()
        self.icerik_alani.addWidget(self.hex_goruntuleyici) # İndeks 7
        
        ana_duzen.addWidget(self.sol_menu)
        ana_duzen.addWidget(self.icerik_alani)

        self.sol_menu.itemClicked.connect(self.sayfa_degistir)
        self.sol_menu.setCurrentRow(0) # Program açıldığında Dashboard seçili gelsin

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