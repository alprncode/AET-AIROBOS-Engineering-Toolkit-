from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QComboBox, QLineEdit, QPushButton, QLabel)

class UnitConverterWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- BİRİM SÖZLÜKLERİ ---
        # Hangi kategoride hangi birimlerin çıkacağını burada tanımlıyoruz
        self.birimler = {
            "Uzunluk": ["Metre", "Kilometre", "Santimetre", "Mil"],
            "Basınç": ["Pascal", "Bar", "PSI", "Atm"],
            "Hız": ["m/s", "km/h", "mph", "knot"],
            "Sıcaklık": ["Celsius", "Fahrenheit", "Kelvin"]
        }
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("Birim Dönüştürücü (Unit Converter)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        ana_duzen.addWidget(baslik)
        
        # 1. Kategori Seçimi
        self.kategori_secim = QComboBox()
        self.kategori_secim.addItems(self.birimler.keys())
        ana_duzen.addWidget(QLabel("Kategori Seçin:"))
        ana_duzen.addWidget(self.kategori_secim)
        
        # 2. Dinamik Birim Seçimi (Kategoriye göre değişecek)
        birim_duzeni = QHBoxLayout()
        
        self.giris_birim_secim = QComboBox()
        self.giris_birim_secim.addItems(self.birimler["Uzunluk"]) # İlk açılışta Uzunluk gelir
        birim_duzeni.addWidget(self.giris_birim_secim)
        
        birim_duzeni.addWidget(QLabel(" ----> "))
        
        self.cikis_birim_secim = QComboBox()
        self.cikis_birim_secim.addItems(self.birimler["Uzunluk"])
        birim_duzeni.addWidget(self.cikis_birim_secim)
        
        ana_duzen.addLayout(birim_duzeni)
        
        # 3. Sayı Girişi ve Çevir Butonu
        deger_duzeni = QHBoxLayout()
        self.giris_kutusu = QLineEdit()
        self.giris_kutusu.setPlaceholderText("Çevrilecek sayıyı girin...")
        deger_duzeni.addWidget(self.giris_kutusu)
        
        self.cevir_butonu = QPushButton("Çevir")
        deger_duzeni.addWidget(self.cevir_butonu)
        ana_duzen.addLayout(deger_duzeni)
        
        # 4. Sonuç Ekranı
        self.sonuc_etiketi = QLabel("Sonuç: ")
        self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: green; margin-top: 10px;")
        ana_duzen.addWidget(self.sonuc_etiketi)
        ana_duzen.addStretch()

        # --- SİNYALLER (Bağlantılar) ---
        # Kategori değiştiğinde kategori_degisti fonksiyonunu tetikle
        self.kategori_secim.currentTextChanged.connect(self.kategori_degisti)
        self.cevir_butonu.clicked.connect(self.hesapla)

    def kategori_degisti(self, kategori):
        """Kategori değişince alt kutulardaki birimleri temizleyip yenilerini ekler."""
        self.giris_birim_secim.clear()
        self.cikis_birim_secim.clear()
        
        yeni_birimler = self.birimler[kategori]
        self.giris_birim_secim.addItems(yeni_birimler)
        self.cikis_birim_secim.addItems(yeni_birimler)

    def hesapla(self):
        """Seçilen kategoriye ve birimlere göre matematiksel formülleri uygular."""
        try:
            # Kullanıcı virgül girerse hata vermemesi için noktaya çeviriyoruz
            girilen_metin = self.giris_kutusu.text().replace(',', '.')
            sayi = float(girilen_metin)
            
            kategori = self.kategori_secim.currentText()
            giris = self.giris_birim_secim.currentText()
            cikis = self.cikis_birim_secim.currentText()
            
            sonuc = 0.0
            
            # --- MATEMATİKSEL FORMÜLLER ---
            if kategori == "Uzunluk":
                oranlar = {"Metre": 1.0, "Kilometre": 1000.0, "Santimetre": 0.01, "Mil": 1609.34}
                sonuc = (sayi * oranlar[giris]) / oranlar[cikis]
                
            elif kategori == "Basınç":
                oranlar = {"Pascal": 1.0, "Bar": 100000.0, "PSI": 6894.76, "Atm": 101325.0}
                sonuc = (sayi * oranlar[giris]) / oranlar[cikis]
                
            elif kategori == "Hız":
                oranlar = {"m/s": 1.0, "km/h": 0.277778, "mph": 0.44704, "knot": 0.514444}
                sonuc = (sayi * oranlar[giris]) / oranlar[cikis]
                
            elif kategori == "Sıcaklık":
                # Sıcaklık orantısal değil formülseldir. Önce girilen değeri Celsius'a sabitliyoruz.
                celsius = sayi
                if giris == "Fahrenheit":
                    celsius = (sayi - 32) * 5/9
                elif giris == "Kelvin":
                    celsius = sayi - 273.15
                    
                # Ardından elde edilen Celsius'u istenen birime çeviriyoruz.
                if cikis == "Celsius":
                    sonuc = celsius
                elif cikis == "Fahrenheit":
                    sonuc = (celsius * 9/5) + 32
                elif cikis == "Kelvin":
                    sonuc = celsius + 273.15

            # Çıktıyı ekrana 4 ondalık hassasiyetle yazdırıyoruz
            self.sonuc_etiketi.setText(f"Sonuç: {sonuc:.4f} {cikis}")
            self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: green; margin-top: 10px;")
            
        except ValueError:
            self.sonuc_etiketi.setText("Hata: Lütfen geçerli bir sayı girin!")
            self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: red; margin-top: 10px;")