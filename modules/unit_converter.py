from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QComboBox, QLineEdit, QPushButton, QLabel)

class UnitConverterWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("Birim Dönüştürücü (Unit Converter)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        ana_duzen.addWidget(baslik)
        
        self.kategori_secim = QComboBox()
        self.kategori_secim.addItems(["Uzunluk", "Basınç", "Hız", "Sıcaklık"])
        ana_duzen.addWidget(QLabel("Kategori Seçin:"))
        ana_duzen.addWidget(self.kategori_secim)
        
        birim_duzeni = QHBoxLayout()
        self.giris_birim_secim = QComboBox()
        self.giris_birim_secim.addItems(["Metre", "Kilometre", "Santimetre", "Mil"])
        birim_duzeni.addWidget(self.giris_birim_secim)
        
        birim_duzeni.addWidget(QLabel(" ----> "))
        
        self.cikis_birim_secim = QComboBox()
        self.cikis_birim_secim.addItems(["Metre", "Kilometre", "Santimetre", "Mil"])
        birim_duzeni.addWidget(self.cikis_birim_secim)
        
        ana_duzen.addLayout(birim_duzeni)
        
        deger_duzeni = QHBoxLayout()
        self.giris_kutusu = QLineEdit()
        self.giris_kutusu.setPlaceholderText("Çevrilecek sayıyı girin...")
        deger_duzeni.addWidget(self.giris_kutusu)
        
        self.cevir_butonu = QPushButton("Çevir")
        deger_duzeni.addWidget(self.cevir_butonu)
        
        ana_duzen.addLayout(deger_duzeni)
        
        self.sonuc_etiketi = QLabel("Sonuç: ")
        self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: green; margin-top: 10px;")
        ana_duzen.addWidget(self.sonuc_etiketi)
        ana_duzen.addStretch()

        # BUTONA BASILDIĞINDA AŞAĞIDAKİ MATEMATİĞİ ÇALIŞTIR
        self.cevir_butonu.clicked.connect(self.hesapla)

    def hesapla(self):
        try:
            # Kutudaki yazıyı ondalıklı sayıya (float) çeviriyoruz
            sayi = float(self.giris_kutusu.text())
            giris = self.giris_birim_secim.currentText()
            cikis = self.cikis_birim_secim.currentText()
            
            # Tüm uzunlukları standartlaştırmak için (Metre = 1.0) referans alıyoruz
            uzunluk_oranlari = {
                "Metre": 1.0, 
                "Kilometre": 1000.0, 
                "Santimetre": 0.01, 
                "Mil": 1609.34
            }
            
            # Önce girilen değeri metreye, sonra hedef birime bölerek dönüştürüyoruz
            metre_karsiligi = sayi * uzunluk_oranlari[giris]
            sonuc = metre_karsiligi / uzunluk_oranlari[cikis]
            
            # Sonucu 4 virgül hassasiyetiyle yeşil renkte ekrana yazdırıyoruz
            self.sonuc_etiketi.setText(f"Sonuç: {sonuc:.4f} {cikis}")
            self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: green; margin-top: 10px;")
            
        except ValueError:
            # Harf girilirse programın çökmesini engellemek için Hata (Exception) yönetimi
            self.sonuc_etiketi.setText("Hata: Lütfen geçerli bir sayı girin!")
            self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: red; margin-top: 10px;")