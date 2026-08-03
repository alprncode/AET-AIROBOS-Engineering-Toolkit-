import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QHBoxLayout, QListWidget, QStackedWidget, QLabel)

class AETDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        # Pencere başlığını ve boyutlarını belirliyoruz
        self.setWindowTitle("AIROBOS Engineering Toolkit")
        self.setGeometry(100, 100, 900, 600)
        
        # Ana pencere için merkezi zemin oluşturuyoruz
        merkezi_widget = QWidget()
        self.setCentralWidget(merkezi_widget)
        
        # Yatay hizalama düzeni (Sol menü ve Sağ içerik yan yana dursun diye)
        ana_duzen = QHBoxLayout(merkezi_widget)
        
        # SOL MENÜ: Projede istenen tüm araçların listesi
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
        
        # SAĞ İÇERİK ALANI: Menüden seçilen aracın gösterileceği yer
        self.icerik_alani = QStackedWidget()
        
        # İlk açılışta görünecek karşılama ekranı
        ilk_sayfa = QLabel("AIROBOS AET Sistemine Hoş Geldiniz.\nLütfen soldaki menüden bir araç seçin.")
        ilk_sayfa.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        self.icerik_alani.addWidget(ilk_sayfa)
        
        # Sol menüyü ve sağ içeriği yan yana düzene ekliyoruz
        ana_duzen.addWidget(self.sol_menu)
        ana_duzen.addWidget(self.icerik_alani)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = AETDashboard()
    pencere.show()
    sys.exit(app.exec())