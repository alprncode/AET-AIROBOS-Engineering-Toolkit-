from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLineEdit, QPushButton, QLabel)

class FlightTimeCalculatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("Tahmini Uçuş Süresi Hesaplayıcı")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        ana_duzen.addWidget(baslik)
        
        # 1. Batarya Kapasitesi Girişi (mAh)
        batarya_duzeni = QHBoxLayout()
        batarya_duzeni.addWidget(QLabel("Batarya Kapasitesi (mAh):"))
        self.batarya_girisi = QLineEdit()
        self.batarya_girisi.setPlaceholderText("Örn: 5000")
        batarya_duzeni.addWidget(self.batarya_girisi)
        ana_duzen.addLayout(batarya_duzeni)
        
        # 2. Akım Tüketimi Girişi (Amper)
        akim_duzeni = QHBoxLayout()
        akim_duzeni.addWidget(QLabel("Ortalama Akım Tüketimi (A):"))
        self.akim_girisi = QLineEdit()
        self.akim_girisi.setPlaceholderText("Örn: 15.5")
        akim_duzeni.addWidget(self.akim_girisi)
        ana_duzen.addLayout(akim_duzeni)
        
        # 3. Hesapla Butonu
        self.hesapla_butonu = QPushButton("Uçuş Süresini Hesapla")
        ana_duzen.addWidget(self.hesapla_butonu)
        
        # 4. Sonuç Ekranı
        self.sonuc_etiketi = QLabel("Tahmini Süre: \n")
        self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: #444; margin-top: 10px;")
        ana_duzen.addWidget(self.sonuc_etiketi)
        
        ana_duzen.addStretch()

        # Butona tıklandığında hesaplama fonksiyonunu çalıştır
        self.hesapla_butonu.clicked.connect(self.hesapla)

    def hesapla(self):
        try:
            # Virgül ile girilen sayıları noktaya çeviriyoruz
            kapasite_mah = float(self.batarya_girisi.text().replace(',', '.'))
            akim_a = float(self.akim_girisi.text().replace(',', '.'))
            
            # Akımın 0 veya eksi girilmesini engelliyoruz
            if akim_a <= 0:
                self.sonuc_etiketi.setText("Hata: Akım değeri 0'dan büyük olmalıdır!")
                self.sonuc_etiketi.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")
                return
            
            # Kapasiteyi Ah'ye çevirip akıma bölerek saat buluyoruz, 60 ile çarpıp dakikaya çeviriyoruz
            kapasite_ah = kapasite_mah / 1000.0
            dakika = (kapasite_ah / akim_a) * 60
            
            # Güvenlik Payı (%20 batarya acil durum inişi için saklanır)
            guvenli_dakika = dakika * 0.8
            
            # Sonucu formatlayıp ekrana yazdırıyoruz
            sonuc_metni = (f"Maksimum Uçuş Süresi: {dakika:.1f} dakika\n"
                           f"Güvenli Uçuş Süresi (%20 Pay ile): {guvenli_dakika:.1f} dakika")
            
            self.sonuc_etiketi.setText(sonuc_metni)
            self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: green; margin-top: 10px;")
            
        except ValueError:
            self.sonuc_etiketi.setText("Hata: Lütfen geçerli sayısal değerler girin!")
            self.sonuc_etiketi.setStyleSheet("font-size: 16px; font-weight: bold; color: red; margin-top: 10px;")