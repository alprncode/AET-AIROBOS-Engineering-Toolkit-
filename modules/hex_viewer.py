from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QTextEdit)

class HexViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("Hex Viewer (Ham Veri Analiz Aracı)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        ana_duzen.addWidget(baslik)
        
        # 1. Veri Giriş Alanı
        ana_duzen.addWidget(QLabel("İncelenecek Metin veya Ham Veri:"))
        self.veri_girisi = QTextEdit()
        self.veri_girisi.setPlaceholderText("Örn: AIROBOS test verisi...")
        self.veri_girisi.setMaximumHeight(100)
        ana_duzen.addWidget(self.veri_girisi)
        
        # 2. Çevir Butonu
        self.cevir_butonu = QPushButton("Hex Formatında Döküm Çıkar")
        ana_duzen.addWidget(self.cevir_butonu)
        
        # 3. Hex Döküm (Hex Dump) Ekranı
        ana_duzen.addWidget(QLabel("Hex Dökümü (Address | Hex | ASCII):"))
        self.hex_ekrani = QTextEdit()
        self.hex_ekrani.setReadOnly(True)
        # Profesyonel görünüm için siyah arkaplan, gri yazı ve sabit genişlikli font kullanıyoruz
        self.hex_ekrani.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas; font-size: 14px;")
        ana_duzen.addWidget(self.hex_ekrani)
        
        # Buton bağlantısı
        self.cevir_butonu.clicked.connect(self.hex_cevir)

    def hex_cevir(self):
        metin = self.veri_girisi.toPlainText()
        if not metin:
            self.hex_ekrani.setText("HATA: Lütfen analiz edilecek bir veri girin.")
            return
        
        # Veriyi byte formatına çeviriyoruz
        byte_verisi = metin.encode('utf-8')
        satirlar = []
        
        # Veriyi 16 byte'lık satırlara bölerek klasik Hex Dump görünümü oluşturuyoruz
        for i in range(0, len(byte_verisi), 16):
            parca = byte_verisi[i:i+16]
            
            # Adres kısmı (Örn: 00000000, 00000010)
            adres = f"{i:08X}"
            
            # Hex değerleri (Örn: 41 49 52 4F)
            hex_kismi = " ".join(f"{b:02X}" for b in parca)
            hex_kismi = hex_kismi.ljust(47) # Hizalama için boşluk ekliyoruz
            
            # ASCII metin karşılığı (Okunmayan karakterler yerine nokta koyuyoruz)
            ascii_kismi = "".join(chr(b) if 32 <= b <= 126 else "." for b in parca)
            
            # Hepsini birleştirip satıra ekliyoruz
            satirlar.append(f"{adres}  {hex_kismi}  |{ascii_kismi}|")
            
        self.hex_ekrani.setText("\n".join(satirlar))