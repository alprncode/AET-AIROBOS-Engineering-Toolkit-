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
        ana_duzen.setSpacing(15)
        
        # --- BAŞLIK ALANI ---
        baslik_kutusu = QFrame()
        baslik_kutusu.setStyleSheet("QFrame { background-color: #1a1a2e; border: 1px solid #16213e; border-radius: 8px; border-bottom: 3px solid #0f3460; }")
        baslik_duzeni = QHBoxLayout(baslik_kutusu)
        
        baslik = QLabel("🚀 AET ULog Dashboard")
        baslik.setStyleSheet("font-size: 22px; font-weight: 900; color: #e94560; border: none; background: transparent;")
        baslik_duzeni.addWidget(baslik)
        
        alt_baslik = QLabel("Gelişmiş Otonom Sistem Uçuş Analizi")
        alt_baslik.setStyleSheet("font-size: 14px; color: #a2a8d3; border: none; background: transparent;")
        baslik_duzeni.addWidget(alt_baslik, alignment=Qt.AlignRight | Qt.AlignVCenter)
        
        ana_duzen.addWidget(baslik_kutusu)
        
        # --- BUTON ---
        kontrol_duzeni = QHBoxLayout()
        self.yukle_butonu = QPushButton("📁 Bir Ulog Dosyası Seç (.ulg .ulog)")
        self.yukle_butonu.setStyleSheet("""
            QPushButton { font-size: 15px; font-weight: bold; color: white; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e94560, stop:1 #0f3460); border-radius: 6px; padding: 12px; }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff5c77, stop:1 #1a4b8c); border: 1px solid #00c3ff; }
            QPushButton:pressed { background: #0f3460; }
        """)
        kontrol_duzeni.addWidget(self.yukle_butonu)
        ana_duzen.addLayout(kontrol_duzeni)
        
        # --- SCROLL ALANI ---
        self.scroll_alani = QScrollArea()
        self.scroll_alani.setWidgetResizable(True)
        self.scroll_alani.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_icerik = QWidget()
        self.scroll_duzen = QVBoxLayout(self.scroll_icerik)
        self.scroll_duzen.setSpacing(25)
        self.scroll_duzen.setContentsMargins(0, 10, 15, 10)
        
        self.scroll_alani.setWidget(self.scroll_icerik)
        ana_duzen.addWidget(self.scroll_alani)
        
        pg.setConfigOption('background', '#121212')
        pg.setConfigOption('foreground', '#e0e0e0')
        
        self.arayuzu_olustur()
        self.yukle_butonu.clicked.connect(self.gercek_dosya_sec_ve_ciz)

    def tekerlek_iptal(self, olay):
        olay.ignore() 

    def optimizasyon_uygula(self, plt):
        plt.showGrid(x=True, y=True, alpha=0.3)
        plt.setClipToView(True)
        plt.setDownsampling(auto=True, mode='peak')

    def sinirlari_kilitle(self, plt, max_time):
        """Grafiğin kaybolmasını engellerken, kullanıcıya çok daha esnek bir gezinti alanı sunar"""
        y_min = float('inf')
        y_max = float('-inf')
        
        for item in plt.listDataItems():
            x_data, y_data = item.getData()
            if y_data is not None and len(y_data) > 0:
                y_min = min(y_min, np.nanmin(y_data))
                y_max = max(y_max, np.nanmax(y_data))
        
        if y_min != float('inf') and y_max != float('-inf'):
            y_fark = max(y_max - y_min, 1.0)
            
            # X ekseninde sağa/sola %50 oranında devasa bir boşluk
            x_esneklik = max_time * 0.5
            # Y ekseninde yukarı/aşağı grafiğin boyutu kadar (%200) büyük bir boşluk
            y_esneklik = y_fark * 2.0
            
            plt.setLimits(
                xMin=-x_esneklik, 
                xMax=max_time + x_esneklik, 
                maxXRange=max_time * 2.5,  # Maksimum zoom out kapasitesi artırıldı
                yMin=y_min - y_esneklik, 
                yMax=y_max + y_esneklik, 
                maxYRange=y_fark * 6.0   # Y ekseninde daha da uzağa çıkabilme izni verildi
            )
        else:
            plt.setLimits(xMin=-10, xMax=max_time + 10, maxXRange=max_time * 3.0)

    def bilgi_paneli_olustur(self, baslik, aciklama, renk="#00c3ff"):
        kutu = QFrame()
        kutu.setStyleSheet(f"QFrame {{ background-color: #1a1a2e; border-left: 5px solid {renk}; border-radius: 5px; }}")
        duzen = QVBoxLayout(kutu)
        duzen.setContentsMargins(15, 10, 15, 10)
        
        lbl_baslik = QLabel(baslik)
        lbl_baslik.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff; border: none; background: transparent;")
        lbl_aciklama = QLabel(aciklama)
        lbl_aciklama.setStyleSheet("font-size: 12px; color: #a2a8d3; border: none; background: transparent;")
        lbl_aciklama.setWordWrap(True)
        
        duzen.addWidget(lbl_baslik)
        duzen.addWidget(lbl_aciklama)
        return kutu

    def arayuzu_olustur(self):
        # 1. İRTİFA
        irtifa_bilgi = self.bilgi_paneli_olustur("✈️ İrtifa Tahmini (Altitude Estimate)", "Açıklama: Aracın kalkış noktasına veya deniz seviyesine (MSL) göre hesaplanan dikey yüksekliğidir.")
        self.scroll_duzen.addWidget(irtifa_bilgi)
        
        gl_irtifa = pg.GraphicsLayoutWidget()
        gl_irtifa.setMinimumHeight(250)
        gl_irtifa.wheelEvent = self.tekerlek_iptal 
        self.plt_alt = gl_irtifa.addPlot(title="Altitude Estimate | Fused Altitude")
        self.optimizasyon_uygula(self.plt_alt)
        self.scroll_duzen.addWidget(gl_irtifa)
        
        # 2. HIZ (VELOCITY)
        hiz_bilgi = self.bilgi_paneli_olustur("💨 Hız Tahmini (Velocity X, Y, Z)", "Açıklama: Aracın yerel koordinat sistemindeki ileri/geri (X), sağa/sola (Y) ve dikey (Z) hareket hızlarını gösterir.", renk="#3498db")
        self.scroll_duzen.addWidget(hiz_bilgi)
        
        gl_hiz = pg.GraphicsLayoutWidget()
        gl_hiz.setMinimumHeight(250)
        gl_hiz.wheelEvent = self.tekerlek_iptal 
        self.plt_hiz = gl_hiz.addPlot(title="Velocity [m/s] | Vx (İleri) | Vy (Yan) | Vz (Dikey)")
        self.optimizasyon_uygula(self.plt_hiz)
        self.scroll_duzen.addWidget(gl_hiz)

        # 3. TUTUM
        tutum_bilgi = self.bilgi_paneli_olustur("📐 Araç Tutumu (Roll & Pitch Angles)", "Açıklama: Otonom sistemin uçuş sırasındaki yatay eksen dengesini gösterir.", renk="#2ca02c")
        self.scroll_duzen.addWidget(tutum_bilgi)
        
        gl_tutum = pg.GraphicsLayoutWidget()
        gl_tutum.setMinimumHeight(350)
        gl_tutum.wheelEvent = self.tekerlek_iptal 
        self.plt_roll = gl_tutum.addPlot(title="Roll Angle | Roll Estimated")
        self.optimizasyon_uygula(self.plt_roll)
        gl_tutum.nextRow()
        self.plt_pitch = gl_tutum.addPlot(title="Pitch Angle | Pitch Estimated")
        self.optimizasyon_uygula(self.plt_pitch)
        self.scroll_duzen.addWidget(gl_tutum)

        # 4. GÜÇ VE BATARYA
        guc_bilgi = self.bilgi_paneli_olustur("🔋 Güç ve Batarya Tüketimi (Power)", "Açıklama: Aracın güç modülü üzerinden okunan anlık batarya voltajı (V) ve çekilen akım (A) değerleridir.", renk="#f1c40f")
        self.scroll_duzen.addWidget(guc_bilgi)
        
        gl_guc = pg.GraphicsLayoutWidget()
        gl_guc.setMinimumHeight(250)
        gl_guc.wheelEvent = self.tekerlek_iptal 
        self.plt_guc = gl_guc.addPlot(title="Power | Voltage [V] | Current [A]")
        self.optimizasyon_uygula(self.plt_guc)
        self.scroll_duzen.addWidget(gl_guc)
        
        # 5. MOTOR ÇIKIŞLARI
        motor_bilgi = self.bilgi_paneli_olustur("⚙️ Motor Çıkışları (Actuator Outputs)", "Açıklama: Uçuş kontrolcüsünün motorlara gönderdiği anlık güç sinyalleridir.", renk="#9b59b6")
        self.scroll_duzen.addWidget(motor_bilgi)
        
        gl_motor = pg.GraphicsLayoutWidget()
        gl_motor.setMinimumHeight(250)
        gl_motor.wheelEvent = self.tekerlek_iptal 
        self.plt_motor = gl_motor.addPlot(title="Motor Outputs | Motor 1 | Motor 2 | Motor 3 | Motor 4")
        self.optimizasyon_uygula(self.plt_motor)
        self.scroll_duzen.addWidget(gl_motor)

        self.scroll_duzen.addStretch()

    def gercek_dosya_sec_ve_ciz(self):
        dosya_yolu, _ = QFileDialog.getOpenFileName(self, "Bir ULog Dosyası Seçin", "", "ULog (*.ulog *.ulg);;Tüm Dosyalar (*.*)")
        if dosya_yolu:
            try:
                self.yukle_butonu.setText("⏳ Uçuş Verileri İşleniyor...")
                self.yukle_butonu.setEnabled(False)
                self.grafik_ciz(dosya_yolu)
                self.yukle_butonu.setText("📁 Bir Ulog Dosyası Seç (.ulg .ulog)")
                self.yukle_butonu.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya okunamadı:\n{str(e)}")
                self.yukle_butonu.setText("📁 Bir Ulog Dosyası Seç (.ulg .ulog)")
                self.yukle_butonu.setEnabled(True)

    def grafik_ciz(self, dosya_yolu):
        ulog = ULog(dosya_yolu)
        
        self.plt_alt.clear()
        self.plt_hiz.clear()
        self.plt_roll.clear()
        self.plt_pitch.clear()
        self.plt_guc.clear()
        self.plt_motor.clear()

        max_t = (ulog.last_timestamp - ulog.start_timestamp) / 1e6

        # --- 1. İRTİFA VE HIZ ---
        try:
            local_pos = ulog.get_dataset('vehicle_local_position')
            t_local = (local_pos.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_alt.plot(t_local, -local_pos.data['z'], pen=pg.mkPen(color='#00c3ff', width=1.5))
            self.plt_hiz.plot(t_local, local_pos.data['vx'], pen=pg.mkPen(color='#d84b20', width=1.5)) 
            self.plt_hiz.plot(t_local, local_pos.data['vy'], pen=pg.mkPen(color='#2ca02c', width=1.5)) 
            self.plt_hiz.plot(t_local, local_pos.data['vz'], pen=pg.mkPen(color='#00c3ff', width=1.5)) 
        except: pass

        # --- 2. TUTUM ---
        try:
            attitude = ulog.get_dataset('vehicle_attitude')
            t_att = (attitude.data['timestamp'] - ulog.start_timestamp) / 1e6
            q0, q1, q2, q3 = attitude.data['q[0]'], attitude.data['q[1]'], attitude.data['q[2]'], attitude.data['q[3]']
            self.plt_roll.plot(t_att, np.degrees(np.arctan2(2.0 * (q0 * q1 + q2 * q3), 1.0 - 2.0 * (q1 * q1 + q2 * q2))), pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_pitch.plot(t_att, np.degrees(np.arcsin(np.clip(2.0 * (q0 * q2 - q3 * q1), -1.0, 1.0))), pen=pg.mkPen(color='#2ca02c', width=1.5))
        except: pass

        # --- 3. GÜÇ VE BATARYA ---
        try:
            battery = ulog.get_dataset('battery_status')
            t_bat = (battery.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_guc.plot(t_bat, battery.data['voltage_v'], pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_guc.plot(t_bat, battery.data['current_a'], pen=pg.mkPen(color='#2ca02c', width=1.5))
        except: pass

        # --- 4. MOTOR ÇIKIŞLARI ---
        try:
            motors = ulog.get_dataset('actuator_motors')
            t_mot = (motors.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_motor.plot(t_mot, motors.data['control[0]'], pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_motor.plot(t_mot, motors.data['control[1]'], pen=pg.mkPen(color='#2ca02c', width=1.5))
            self.plt_motor.plot(t_mot, motors.data['control[2]'], pen=pg.mkPen(color='#00c3ff', width=1.5))
            self.plt_motor.plot(t_mot, motors.data['control[3]'], pen=pg.mkPen(color='#f1c40f', width=1.5))
        except:
            try:
                outputs = ulog.get_dataset('actuator_outputs')
                t_out = (outputs.data['timestamp'] - ulog.start_timestamp) / 1e6
                self.plt_motor.plot(t_out, outputs.data['output[0]'], pen=pg.mkPen(color='#d84b20', width=1.5))
                self.plt_motor.plot(t_out, outputs.data['output[1]'], pen=pg.mkPen(color='#2ca02c', width=1.5))
                self.plt_motor.plot(t_out, outputs.data['output[2]'], pen=pg.mkPen(color='#00c3ff', width=1.5))
                self.plt_motor.plot(t_out, outputs.data['output[3]'], pen=pg.mkPen(color='#f1c40f', width=1.5))
            except: pass

        for plt in [self.plt_alt, self.plt_hiz, self.plt_roll, self.plt_pitch, self.plt_guc, self.plt_motor]:
            self.sinirlari_kilitle(plt, max_t)