import pyqtgraph as pg
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFileDialog, QMessageBox)
from pyulog import ULog

class ULogAnalyzerWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("ULog Analyzer (İnteraktif İrtifa Grafiği)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #00c3ff;")
        ana_duzen.addWidget(baslik)
        
        # 1. Kontrol Paneli
        kontrol_duzeni = QHBoxLayout()
        self.yukle_butonu = QPushButton("Gerçek ULog Dosyası Seç (.ulg, .ulog)")
        self.yukle_butonu.setStyleSheet("padding: 10px; font-weight: bold; background-color: #d84b20; color: white;")
        kontrol_duzeni.addWidget(self.yukle_butonu)
        ana_duzen.addLayout(kontrol_duzeni)
        
        # 2. PyQtGraph İnteraktif Grafik Alanı (Dark Mode Entegrasyonu)
        pg.setConfigOption('background', '#181818') # Arayüzle uyumlu arkaplan
        pg.setConfigOption('foreground', '#e0e0e0') # Eksen ve metin renkleri
        
        self.grafik_alani = pg.PlotWidget()
        self.grafik_alani.setTitle("Altitude Estimate (Fare Tekerleği ile Yakınlaştır / Basılı Tutup Sürükle)", color="#00c3ff", size="12pt")
        self.grafik_alani.setLabel('left', 'İrtifa', units='Metre')
        self.grafik_alani.setLabel('bottom', 'Uçuş Süresi', units='Saniye')
        self.grafik_alani.showGrid(x=True, y=True, alpha=0.3)
        self.grafik_alani.addLegend() # Çizgi renklerinin ne anlama geldiğini gösteren kutu
        
        ana_duzen.addWidget(self.grafik_alani)
        
        # Buton Bağlantısı
        self.yukle_butonu.clicked.connect(self.gercek_dosya_sec_ve_ciz)

    def gercek_dosya_sec_ve_ciz(self):
        dosya_yolu, _ = QFileDialog.getOpenFileName(
            self, 
            "Analiz Edilecek ULog Dosyasını Seçin", 
            "", 
            "ULog Dosyaları (*.ulog *.ulg);;Tüm Dosyalar (*.*)"
        )
        
        if dosya_yolu:
            try:
                self.yukle_butonu.setText("Analiz Ediliyor, Lütfen Bekleyin...")
                self.yukle_butonu.setEnabled(False)
                
                self.grafik_ciz(dosya_yolu)
                
                self.yukle_butonu.setText("Gerçek ULog Dosyası Seç (.ulg, .ulog)")
                self.yukle_butonu.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "ULog Okuma Hatası", f"Dosya ayrıştırılırken hata oluştu:\n{str(e)}")
                self.yukle_butonu.setText("Gerçek ULog Dosyası Seç (.ulg, .ulog)")
                self.yukle_butonu.setEnabled(True)

    def grafik_ciz(self, dosya_yolu):
        # Gerçek ulog dosyasını okuyoruz
        ulog = ULog(dosya_yolu)
        
        # Eski çizimleri tamamen temizle
        self.grafik_alani.clear()
        
        veri_cizildi_mi = False

        # 1. Veri: Fused Altitude (Uçuş kontrolcüsünün hesapladığı net irtifa)
        try:
            local_pos = ulog.get_dataset('vehicle_local_position')
            t_local = (local_pos.data['timestamp'] - ulog.start_timestamp) / 1e6
            z_data = -local_pos.data['z']
            
            # Mavi renkte, belirgin kalınlıkta çizdir
            kalem_fused = pg.mkPen(color='#00c3ff', width=2)
            self.grafik_alani.plot(t_local, z_data, name='Fused Altitude Estimation', pen=kalem_fused)
            veri_cizildi_mi = True
        except Exception:
            pass

        # 2. Veri: Barometre İrtifası (Sadece barometre sensöründen gelen ham veri)
        try:
            baro_data = ulog.get_dataset('sensor_baro')
            t_baro = (baro_data.data['timestamp'] - ulog.start_timestamp) / 1e6
            baro_alt = baro_data.data['altitude']
            
            # Pembe renkte çizdir
            kalem_baro = pg.mkPen(color='#ff00ff', width=2)
            self.grafik_alani.plot(t_baro, baro_alt, name='Barometer Altitude', pen=kalem_baro)
            veri_cizildi_mi = True
        except Exception:
            pass

        if not veri_cizildi_mi:
            QMessageBox.warning(self, "Veri Bulunamadı", "Bu ULog dosyasında İrtifa (Altitude) verisi bulunamadı.")