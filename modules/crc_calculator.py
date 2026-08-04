import binascii
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QComboBox, QPushButton, QLabel, QTextEdit)

class CRCCalculatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("CRC Hesaplayıcı (Veri Doğrulama)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        ana_duzen.addWidget(baslik)
        
        # 1. CRC Algoritması Seçimi
        algoritma_duzeni = QHBoxLayout()
        algoritma_duzeni.addWidget(QLabel("Algoritma Seçin:"))
        self.algoritma_secim = QComboBox()
        self.algoritma_secim.addItems(["CRC32 (Standart)", "CRC16 (Temel Toplam)", "CRC8 (Temel Toplam)"])
        algoritma_duzeni.addWidget(self.algoritma_secim)
        ana_duzen.addLayout(algoritma_duzeni)
        
        # 2. Veri Giriş Alanı (Geniş Metin Kutusu)
        ana_duzen.addWidget(QLabel("Doğrulanacak Veri (Metin Formatında):"))
        self.veri_girisi = QTextEdit()
        self.veri_girisi.setPlaceholderText("Haberleşme paketini veya test metnini buraya girin...")
        self.veri_girisi.setMaximumHeight(120)
        ana_duzen.addWidget(self.veri_girisi)
        
        # 3. Hesapla Butonu
        self.hesapla_butonu = QPushButton("CRC Değerini Hesapla (Hex)")
        ana_duzen.addWidget(self.hesapla_butonu)
        
        # 4. Sonuç Ekranı
        self.sonuc_etiketi = QLabel("Hesaplanan Değer: \n")
        self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: #444; margin-top: 10px;")
        ana_duzen.addWidget(self.sonuc_etiketi)
        
        ana_duzen.addStretch()

        # Buton Bağlantısı
        self.hesapla_butonu.clicked.connect(self.hesapla)

    def hesapla(self):
        # Girilen metni bilgisayarın anlayacağı byte formatına (UTF-8) çeviriyoruz
        metin = self.veri_girisi.toPlainText()
        veri_byte = metin.encode('utf-8')
        algoritma = self.algoritma_secim.currentText()
        
        if not metin:
            self.sonuc_etiketi.setText("Hata: Lütfen doğrulanacak bir veri girin!")
            self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: red; margin-top: 10px;")
            return
            
        try:
            sonuc_hex = ""
            
            if "CRC32" in algoritma:
                # Gerçek donanım standartlarındaki CRC32 algoritması
                crc32_degeri = binascii.crc32(veri_byte) & 0xFFFFFFFF
                sonuc_hex = f"0x{crc32_degeri:08X}"
                
            elif "CRC16" in algoritma:
                # Basitleştirilmiş checksum (Temsili)
                crc16_degeri = sum(veri_byte) & 0xFFFF
                sonuc_hex = f"0x{crc16_degeri:04X}"
                
            elif "CRC8" in algoritma:
                # Basitleştirilmiş checksum (Temsili)
                crc8_degeri = sum(veri_byte) & 0xFF
                sonuc_hex = f"0x{crc8_degeri:02X}"
            
            # Çıktıyı formatlayıp ekrana veriyoruz
            self.sonuc_etiketi.setText(f"{algoritma} Sonucu:\n{sonuc_hex}")
            self.sonuc_etiketi.setStyleSheet("font-size: 18px; font-weight: bold; color: green; margin-top: 10px;")
            
        except Exception as e:
            self.sonuc_etiketi.setText(f"Hesaplama Hatası: İşlem yapılamadı.")
            self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: red; margin-top: 10px;")