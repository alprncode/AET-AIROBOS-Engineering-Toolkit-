from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLineEdit, QPushButton, QLabel)

class CoordinateConverterWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("Koordinat Dönüştürücü (DD -> DMS)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        ana_duzen.addWidget(baslik)
        
        # 1. Enlem Girişi
        enlem_duzeni = QHBoxLayout()
        enlem_duzeni.addWidget(QLabel("Enlem (Decimal Degree):"))
        self.enlem_girisi = QLineEdit()
        self.enlem_girisi.setPlaceholderText("Örn: 39.92077")
        enlem_duzeni.addWidget(self.enlem_girisi)
        ana_duzen.addLayout(enlem_duzeni)
        
        # 2. Boylam Girişi
        boylam_duzeni = QHBoxLayout()
        boylam_duzeni.addWidget(QLabel("Boylam (Decimal Degree):"))
        self.boylam_girisi = QLineEdit()
        self.boylam_girisi.setPlaceholderText("Örn: 32.85411")
        boylam_duzeni.addWidget(self.boylam_girisi)
        ana_duzen.addLayout(boylam_duzeni)
        
        # 3. Çevir Butonu
        self.cevir_butonu = QPushButton("DMS Formatına Çevir")
        ana_duzen.addWidget(self.cevir_butonu)
        
        # 4. Sonuç Ekranı
        self.sonuc_etiketi = QLabel("Sonuçlar:\n")
        self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: #444; margin-top: 10px;")
        ana_duzen.addWidget(self.sonuc_etiketi)
        
        ana_duzen.addStretch()

        # Buton Bağlantısı
        self.cevir_butonu.clicked.connect(self.hesapla)

    # MATEMATİKSEL DÖNÜŞTÜRME FONKSİYONU
    def dd_to_dms(self, derece_ondalik, is_enlem):
        yon = ""
        if is_enlem:
            yon = "N" if derece_ondalik >= 0 else "S"
        else:
            yon = "E" if derece_ondalik >= 0 else "W"
            
        derece_mutlak = abs(derece_ondalik)
        derece = int(derece_mutlak)
        kalan = (derece_mutlak - derece) * 60
        dakika = int(kalan)
        saniye = (kalan - dakika) * 60
        
        return f"{derece}° {dakika}' {saniye:.2f}\" {yon}"

    def hesapla(self):
        try:
            # Virgülleri noktaya çevirip sayıları alıyoruz
            enlem_text = self.enlem_girisi.text().replace(',', '.')
            boylam_text = self.boylam_girisi.text().replace(',', '.')
            
            if not enlem_text or not boylam_text:
                self.sonuc_etiketi.setText("Hata: Lütfen hem enlem hem de boylam girin!")
                self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: red; margin-top: 10px;")
                return
                
            enlem = float(enlem_text)
            boylam = float(boylam_text)
            
            # Dünya standartları kontrolü (Enlem -90/+90, Boylam -180/+180 arasıdır)
            if enlem < -90 or enlem > 90 or boylam < -180 or boylam > 180:
                raise ValueError
                
            enlem_dms = self.dd_to_dms(enlem, True)
            boylam_dms = self.dd_to_dms(boylam, False)
            
            self.sonuc_etiketi.setText(f"Enlem (DMS): {enlem_dms}\nBoylam (DMS): {boylam_dms}")
            self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: green; margin-top: 10px;")
            
        except ValueError:
            self.sonuc_etiketi.setText("Hata: Geçerli ve dünya sınırları içinde değerler girin!")
            self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: red; margin-top: 10px;")