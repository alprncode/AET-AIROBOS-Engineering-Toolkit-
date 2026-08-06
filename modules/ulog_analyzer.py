import pyqtgraph as pg
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFileDialog, QMessageBox,
                               QScrollArea, QFrame)
from PySide6.QtCore import Qt
from pyulog import ULog

class ULogAnalyzerWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("ULog Dashboard (Kapsamlı Uçuş Analizi)")
        baslik.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 5px; color: #00c3ff;")
        ana_duzen.addWidget(baslik)
        
        # 1. Kontrol Paneli
        kontrol_duzeni = QHBoxLayout()
        self.yukle_butonu = QPushButton("Gerçek ULog Dosyası Seç (.ulg, .ulog)")
        self.yukle_butonu.setStyleSheet("padding: 10px; font-weight: bold; background-color: #d84b20; color: white; border-radius: 4px;")
        kontrol_duzeni.addWidget(self.yukle_butonu)
        ana_duzen.addLayout(kontrol_duzeni)
        
        # 2. KAYDIRILABİLİR ALAN (SCROLL AREA) İNŞASI
        self.scroll_alani = QScrollArea()
        self.scroll_alani.setWidgetResizable(True)
        self.scroll_alani.setStyleSheet("QScrollArea { border: none; background-color: #121212; }")
        
        # Scroll alanının içindeki ana taşıyıcı widget
        self.scroll_icerik = QWidget()
        self.scroll_duzen = QVBoxLayout(self.scroll_icerik)
        self.scroll_duzen.setSpacing(20) # Grafikler arası boşluk
        self.scroll_duzen.setContentsMargins(0, 0, 15, 0)
        
        self.scroll_alani.setWidget(self.scroll_icerik)
        ana_duzen.addWidget(self.scroll_alani)
        
        # Pyqtgraph ayarları
        pg.setConfigOption('background', '#181818')
        pg.setConfigOption('foreground', '#e0e0e0')
        
        # Grafikleri ve Açıklamaları Tutacak Sözlük
        self.grafikler = {}
        
        # Başlangıçta arayüzü hazırla (Boş grafikler)
        self.arayuzu_olustur()
        
        # Buton Bağlantısı
        self.yukle_butonu.clicked.connect(self.gercek_dosya_sec_ve_ciz)

    def bilgi_paneli_olustur(self, baslik, aciklama):
        """Grafiklerin üstüne eklenecek şık açıklama panelleri üretir"""
        kutu = QFrame()
        kutu.setStyleSheet("background-color: #1e1e1e; border-left: 4px solid #00c3ff; border-radius: 3px; padding: 10px;")
        duzen = QVBoxLayout(kutu)
        duzen.setContentsMargins(10, 5, 10, 5)
        
        lbl_baslik = QLabel(baslik)
        lbl_baslik.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff; border: none;")
        
        lbl_aciklama = QLabel(aciklama)
        lbl_aciklama.setStyleSheet("font-size: 12px; color: #aaaaaa; border: none;")
        lbl_aciklama.setWordWrap(True)
        
        duzen.addWidget(lbl_baslik)
        duzen.addWidget(lbl_aciklama)
        return kutu

    def arayuzu_olustur(self):
        # 1. BÖLÜM: İRTİFA
        irtifa_bilgi = self.bilgi_paneli_olustur(
            "İrtifa Tahmini (Altitude Estimate)", 
            "Açıklama: Aracın deniz seviyesine (MSL) veya kalkış noktasına göre hesaplanan yüksekliğidir. Fused Altitude, barometre ve GPS'in filtrelenmiş net sonucudur. Barometre grafiğindeki ani oynamalar hava akımı kaynaklı olabilir."
        )
        self.scroll_duzen.addWidget(irtifa_bilgi)
        
        gl_irtifa = pg.GraphicsLayoutWidget()
        gl_irtifa.setMinimumHeight(300) # Her grafiğe minimum boyut veriyoruz ki ezilmesinler
        self.plt_alt = gl_irtifa.addPlot(title="Altitude Estimate | Fused Altitude | Barometer")
        self.plt_alt.showGrid(x=True, y=True, alpha=0.3)
        self.scroll_duzen.addWidget(gl_irtifa)
        
        # 2. BÖLÜM: TUTUM (ATTITUDE)
        tutum_bilgi = self.bilgi_paneli_olustur(
            "Araç Tutumu (Roll & Pitch Angles)", 
            "Açıklama: Otonom sistemin yatay eksendeki dengesini gösterir. Roll (sağa/sola yatma) ve Pitch (öne/arkaya eğilme) açılarının Setpoint (istenen) değerden sapması, PID ayarlarının veya rüzgar direncinin kalitesini gösterir."
        )
        self.scroll_duzen.addWidget(tutum_bilgi)
        
        gl_tutum = pg.GraphicsLayoutWidget()
        gl_tutum.setMinimumHeight(400)
        
        self.plt_roll = gl_tutum.addPlot(title="Roll Angle | Roll Estimated")
        self.plt_roll.showGrid(x=True, y=True, alpha=0.3)
        gl_tutum.nextRow()
        
        self.plt_pitch = gl_tutum.addPlot(title="Pitch Angle | Pitch Estimated")
        self.plt_pitch.showGrid(x=True, y=True, alpha=0.3)
        self.scroll_duzen.addWidget(gl_tutum)
        
        # Boşluk doldurucu (Aşağıdaki alanı iter)
        self.scroll_duzen.addStretch()

    def gercek_dosya_sec_ve_ciz(self):
        dosya_yolu, _ = QFileDialog.getOpenFileName(
            self, "ULog Dosyasını Seçin", "", "ULog (*.ulog *.ulg);;Tüm Dosyalar (*.*)"
        )
        if dosya_yolu:
            try:
                self.yukle_butonu.setText("Uçuş Verileri İşleniyor, Lütfen Bekleyin...")
                self.yukle_butonu.setEnabled(False)
                self.grafik_ciz(dosya_yolu)
                self.yukle_butonu.setText("Gerçek ULog Dosyası Seç (.ulg, .ulog)")
                self.yukle_butonu.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya okunamadı:\n{str(e)}")
                self.yukle_butonu.setText("Gerçek ULog Dosyası Seç (.ulg, .ulog)")
                self.yukle_butonu.setEnabled(True)

    def grafik_ciz(self, dosya_yolu):
        ulog = ULog(dosya_yolu)
        
        self.plt_alt.clear()
        self.plt_roll.clear()
        self.plt_pitch.clear()
        
        # İRTİFA
        try:
            local_pos = ulog.get_dataset('vehicle_local_position')
            t_local = (local_pos.data['timestamp'] - ulog.start_timestamp) / 1e6
            z_data = -local_pos.data['z']
            self.plt_alt.plot(t_local, z_data, pen=pg.mkPen(color='#00c3ff', width=1.5))
        except: pass
            
        try:
            baro_data = ulog.get_dataset('sensor_baro')
            t_baro = (baro_data.data['timestamp'] - ulog.start_timestamp) / 1e6
            baro_alt = baro_data.data['altitude']
            self.plt_alt.plot(t_baro, baro_alt, pen=pg.mkPen(color='#ff00ff', width=1.5))
        except: pass

        # TUTUM
        try:
            attitude = ulog.get_dataset('vehicle_attitude')
            t_att = (attitude.data['timestamp'] - ulog.start_timestamp) / 1e6
            q0, q1, q2, q3 = attitude.data['q[0]'], attitude.data['q[1]'], attitude.data['q[2]'], attitude.data['q[3]']
            
            roll_rad = np.arctan2(2.0 * (q0 * q1 + q2 * q3), 1.0 - 2.0 * (q1 * q1 + q2 * q2))
            pitch_rad = np.arcsin(np.clip(2.0 * (q0 * q2 - q3 * q1), -1.0, 1.0))
            
            self.plt_roll.plot(t_att, np.degrees(roll_rad), pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_pitch.plot(t_att, np.degrees(pitch_rad), pen=pg.mkPen(color='#2ca02c', width=1.5))
        except: pass