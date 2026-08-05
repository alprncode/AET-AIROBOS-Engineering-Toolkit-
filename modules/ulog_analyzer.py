import pyqtgraph as pg
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFileDialog, QMessageBox)
from pyulog import ULog

class ULogAnalyzerWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("ULog Analyzer (Bağımsız ve Temiz Grafikler)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #00c3ff;")
        ana_duzen.addWidget(baslik)
        
        # 1. Kontrol Paneli
        kontrol_duzeni = QHBoxLayout()
        self.yukle_butonu = QPushButton("Gerçek ULog Dosyası Seç (.ulg, .ulog)")
        self.yukle_butonu.setStyleSheet("padding: 10px; font-weight: bold; background-color: #d84b20; color: white;")
        kontrol_duzeni.addWidget(self.yukle_butonu)
        ana_duzen.addLayout(kontrol_duzeni)
        
        # 2. PyQtGraph 
        pg.setConfigOption('background', '#181818')
        pg.setConfigOption('foreground', '#e0e0e0')
        
        self.grafik_alani = pg.GraphicsLayoutWidget()
        ana_duzen.addWidget(self.grafik_alani)
        
        # A) İrtifa Grafiği - Yazılar HTML ile başlığa taşındı
        self.plt_alt = self.grafik_alani.addPlot(title="Altitude Estimate | Fused Altitude | Barometer")
        self.plt_alt.setLabel('left', 'İrtifa', units='m')
        self.plt_alt.showGrid(x=True, y=True, alpha=0.3)
        # addLegend() kaldırıldı!
        
        self.grafik_alani.nextRow()
        
        # B) Roll (Yuvarlanma) Grafiği
        self.plt_roll = self.grafik_alani.addPlot(title="Roll Angle | Roll Estimated")
        self.plt_roll.setLabel('left', 'Roll', units='deg')
        self.plt_roll.showGrid(x=True, y=True, alpha=0.3)
        
        self.grafik_alani.nextRow()
        
        # C) Pitch (Yunuslama) Grafiği
        self.plt_pitch = self.grafik_alani.addPlot(title="Pitch Angle | Pitch Estimated")
        self.plt_pitch.setLabel('left', 'Pitch', units='deg')
        self.plt_pitch.setLabel('bottom', 'Uçuş Süresi', units='s')
        self.plt_pitch.showGrid(x=True, y=True, alpha=0.3)
        
        # DİKKAT: setXLink() komutları silindi. Artık tüm grafikler bağımsız hareket edecek!
        
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
        ulog = ULog(dosya_yolu)
        
        # Eski çizimleri temizle
        self.plt_alt.clear()
        self.plt_roll.clear()
        self.plt_pitch.clear()
        
        # 1. İRTİFA VERİSİ
        try:
            local_pos = ulog.get_dataset('vehicle_local_position')
            t_local = (local_pos.data['timestamp'] - ulog.start_timestamp) / 1e6
            z_data = -local_pos.data['z']
            self.plt_alt.plot(t_local, z_data, name='Fused Altitude', pen=pg.mkPen(color='#00c3ff', width=1.5))
        except:
            pass
            
        try:
            baro_data = ulog.get_dataset('sensor_baro')
            t_baro = (baro_data.data['timestamp'] - ulog.start_timestamp) / 1e6
            baro_alt = baro_data.data['altitude']
            self.plt_alt.plot(t_baro, baro_alt, name='Barometer', pen=pg.mkPen(color='#ff00ff', width=1.5))
        except:
            pass

        # 2. TUTUM (ATTITUDE) VERİSİ VE MATEMATİKSEL DÖNÜŞÜMLER
        try:
            attitude = ulog.get_dataset('vehicle_attitude')
            t_att = (attitude.data['timestamp'] - ulog.start_timestamp) / 1e6
            
            q0 = attitude.data['q[0]']
            q1 = attitude.data['q[1]']
            q2 = attitude.data['q[2]']
            q3 = attitude.data['q[3]']
            
            sinr_cosp = 2.0 * (q0 * q1 + q2 * q3)
            cosr_cosp = 1.0 - 2.0 * (q1 * q1 + q2 * q2)
            roll_rad = np.arctan2(sinr_cosp, cosr_cosp)
            
            sinp = 2.0 * (q0 * q2 - q3 * q1)
            sinp = np.clip(sinp, -1.0, 1.0) 
            pitch_rad = np.arcsin(sinp)
            
            roll_deg = np.degrees(roll_rad)
            pitch_deg = np.degrees(pitch_rad)
            
            self.plt_roll.plot(t_att, roll_deg, name='Roll Estimated', pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_pitch.plot(t_att, pitch_deg, name='Pitch Estimated', pen=pg.mkPen(color='#2ca02c', width=1.5))
            
        except Exception as e:
            print("Tutum verisi bulunamadı veya hata:", e)