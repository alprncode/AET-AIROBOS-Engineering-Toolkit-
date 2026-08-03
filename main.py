import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QHBoxLayout, QListWidget, QStackedWidget, QLabel)

from modules.unit_converter import UnitConverterWidget

class AETDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AIROBOS Engineering Toolkit")
        self.setGeometry(100, 100, 900, 600)
        
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
        
        ilk_sayfa = QLabel("AIROBOS AET Sistemine Hoş Geldiniz.\nLütfen soldaki menüden bir araç seçin.")
        ilk_sayfa.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        
        self.icerik_alani.addWidget(ilk_sayfa) # İndeks 0 (Dashboard)
        
        self.cevirici_modulu = UnitConverterWidget()
        self.icerik_alani.addWidget(self.cevirici_modulu) # İndeks 1 (Unit Converter)
        
        ana_duzen.addWidget(self.sol_menu)
        ana_duzen.addWidget(self.icerik_alani)

        # KABLO: Menüye tıklandığında sayfa_degistir fonksiyonunu çalıştır
        self.sol_menu.itemClicked.connect(self.sayfa_degistir)

    # İŞLEM: Menüden seçilen isme göre sağ tarafın içeriğini değiştir
    def sayfa_degistir(self, item):
        secilen_isim = item.text()
        if secilen_isim == "Dashboard":
            self.icerik_alani.setCurrentIndex(0)
        elif secilen_isim == "Unit Converter":
            self.icerik_alani.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = AETDashboard()
    pencere.show()
    sys.exit(app.exec())