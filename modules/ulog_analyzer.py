from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QListWidget, QProgressBar)

class ULogAnalyzerWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("ULog Analyzer (Telemetri ve Uçuş Verisi)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #00c3ff;")
        ana_duzen.addWidget(baslik)
        
        # 1. Kontrol Paneli
        kontrol_duzeni = QHBoxLayout()
        self.yukle_butonu = QPushButton("ULog Dosyası Yükle (Simülasyon)")
        self.yukle_butonu.setStyleSheet("padding: 10px; font-weight: bold;")
        kontrol_duzeni.addWidget(self.yukle_butonu)
        ana_duzen.addLayout(kontrol_duzeni)
        
        # 2. İlerleme Çubuğu (Yükleme efekti)
        self.ilerleme = QProgressBar()
        self.ilerleme.setValue(0)
        self.ilerleme.setStyleSheet("QProgressBar { border: 1px solid #444; border-radius: 3px; text-align: center; color: white; } QProgressBar::chunk { background-color: #007acc; }")
        ana_duzen.addWidget(self.ilerleme)
        
        # 3. Analiz Sonuçları Ekranı
        ana_duzen.addWidget(QLabel("Uçuş Metrikleri Özet Raporu:"))
        self.analiz_ekrani = QListWidget()
        self.analiz_ekrani.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 14px;")
        ana_duzen.addWidget(self.analiz_ekrani)
        
        # Buton Bağlantısı
        self.yukle_butonu.clicked.connect(self.log_analiz_et)

    def log_analiz_et(self):
        # Barı doldur ve ekranı temizle
        self.ilerleme.setValue(100)
        self.analiz_ekrani.clear()
        
        # Uçuş sonrası ayrıştırılmış örnek telemetri verileri
        simulasyon_verileri = [
            "--- ULog Dosyası Başarıyla Ayrıştırıldı ---",
            "Uçuş Süresi: 14 Dakika 22 Saniye",
            "Maksimum İrtifa (Altitude): 124.5 Metre",
            "Ortalama Hız: 12.4 m/s",
            "Batarya Tüketimi: %42 (Başlangıç: 16.4V, Bitiş: 14.2V)",
            "GPS Durumu: 3D Fix (14 Uydu)",
            "Hata Logları: 0 Kritik Hata, 2 Uyarı (Rüzgar Direnci)",
            "--- Analiz Tamamlandı ---"
        ]
        
        self.analiz_ekrani.addItems(simulasyon_verileri)