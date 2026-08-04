from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QTableWidget, 
                               QTableWidgetItem, QHeaderView)

class CANLogViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("CAN Log Viewer (Haberleşme Analizi)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #00c3ff;")
        ana_duzen.addWidget(baslik)
        
        # 1. CAN Veri Tablosu
        self.tablo = QTableWidget(0, 4) # 0 satır, 4 sütun başlangıç
        self.tablo.setHorizontalHeaderLabels(["Zaman Damgası", "CAN ID", "DLC", "Veri Paketleri (Hex)"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                gridline-color: #444;
                border: 1px solid #444;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #00c3ff;
                padding: 4px;
                font-weight: bold;
                border: 1px solid #444;
            }
        """)
        ana_duzen.addWidget(self.tablo)
        
        # 2. Kontrol Butonları
        buton_duzeni = QHBoxLayout()
        self.ornek_yukle_butonu = QPushButton("Örnek Log Yükle (Simülasyon)")
        self.temizle_butonu = QPushButton("Tabloyu Temizle")
        self.temizle_butonu.setStyleSheet("background-color: #8b0000; color: white; font-weight: bold;")
        
        buton_duzeni.addWidget(self.ornek_yukle_butonu)
        buton_duzeni.addWidget(self.temizle_butonu)
        ana_duzen.addLayout(buton_duzeni)
        
        # Buton Bağlantıları
        self.ornek_yukle_butonu.clicked.connect(self.ornek_log_yukle)
        self.temizle_butonu.clicked.connect(lambda: self.tablo.setRowCount(0))

    def ornek_log_yukle(self):
        # Gerçek bir CAN Bus ağı simülasyonu verileri
        ornek_veriler = [
            ("0.0010", "0x123", "8", "FF 00 1A 2B 3C 4D 5E 6F"),
            ("0.0052", "0x1A4", "4", "01 02 03 04 -  -  -  -"),
            ("0.0105", "0x01A", "8", "00 00 00 00 00 00 00 00"),
            ("0.0121", "0x123", "8", "FE 00 1A 2B 3C 4D 5E 6F"),
            ("0.0180", "0x2B0", "2", "AA BB -  -  -  -  -  -"),
            ("0.0223", "0x1A4", "4", "01 02 03 05 -  -  -  -")
        ]
        
        self.tablo.setRowCount(len(ornek_veriler))
        for satir_indeksi, satir_verisi in enumerate(ornek_veriler):
            for sutun_indeksi, hucre_verisi in enumerate(satir_verisi):
                self.tablo.setItem(satir_indeksi, sutun_indeksi, QTableWidgetItem(hucre_verisi))