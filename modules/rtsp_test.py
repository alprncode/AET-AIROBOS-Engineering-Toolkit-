from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QLineEdit, QFrame)
from PySide6.QtCore import Qt

class RTSPTestWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("RTSP Video Yayın Testi")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #00c3ff;")
        ana_duzen.addWidget(baslik)
        
        # 1. URL Giriş Alanı
        url_duzeni = QHBoxLayout()
        url_duzeni.addWidget(QLabel("RTSP URL:"))
        self.url_girisi = QLineEdit()
        self.url_girisi.setPlaceholderText("Örn: rtsp://192.168.1.100:554/cam/realmonitor")
        url_duzeni.addWidget(self.url_girisi)
        ana_duzen.addLayout(url_duzeni)
        
        # 2. Kontrol Butonları
        buton_duzeni = QHBoxLayout()
        self.baslat_butonu = QPushButton("Yayını Başlat")
        self.baslat_butonu.setStyleSheet("background-color: #007acc; font-weight: bold;")
        self.durdur_butonu = QPushButton("Durdur")
        self.durdur_butonu.setStyleSheet("background-color: #8b0000; font-weight: bold;")
        self.durdur_butonu.setEnabled(False) # Başlangıçta pasif
        
        buton_duzeni.addWidget(self.baslat_butonu)
        buton_duzeni.addWidget(self.durdur_butonu)
        ana_duzen.addLayout(buton_duzeni)
        
        # 3. Video Görüntüleme Alanı (Simülasyon Ekranı)
        self.video_ekrani = QLabel("YAYIN YOK\n(Bağlantı Bekleniyor...)")
        self.video_ekrani.setAlignment(Qt.AlignCenter)
        self.video_ekrani.setFrameShape(QFrame.Box)
        self.video_ekrani.setStyleSheet("background-color: #000000; color: #555; font-size: 24px; font-weight: bold; border: 2px solid #333;")
        # 16:9 formatına uygun temsili bir boyutlandırma
        self.video_ekrani.setMinimumHeight(400)
        ana_duzen.addWidget(self.video_ekrani)
        
        # Buton Bağlantıları
        self.baslat_butonu.clicked.connect(self.yayin_baslat)
        self.durdur_butonu.clicked.connect(self.yayin_durdur)

    def yayin_baslat(self):
        url = self.url_girisi.text().strip()
        if not url:
            self.video_ekrani.setText("HATA:\nLütfen geçerli bir RTSP adresi girin!")
            self.video_ekrani.setStyleSheet("background-color: #000000; color: red; font-size: 20px; font-weight: bold; border: 2px solid #333;")
            return
            
        self.video_ekrani.setText(f"[ BAĞLANILDI ]\n\n{url}\n\n(Canlı Yayın Simülasyonu)")
        self.video_ekrani.setStyleSheet("background-color: #1a1a1a; color: #00ff00; font-size: 18px; font-weight: bold; border: 2px solid #00c3ff;")
        
        self.baslat_butonu.setEnabled(False)
        self.durdur_butonu.setEnabled(True)

    def yayin_durdur(self):
        self.video_ekrani.setText("YAYIN YOK\n(Bağlantı Kesildi)")
        self.video_ekrani.setStyleSheet("background-color: #000000; color: #555; font-size: 24px; font-weight: bold; border: 2px solid #333;")
        
        self.baslat_butonu.setEnabled(True)
        self.durdur_butonu.setEnabled(False)