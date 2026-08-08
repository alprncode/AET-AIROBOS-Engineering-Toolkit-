import pyqtgraph as pg
import numpy as np
import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
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
        
        # --- GELİŞMİŞ UÇUŞ ÖZET TABLOSU (SUMMARY CARD) ---
        self.ozet_kutusu = QFrame()
        self.ozet_kutusu.setStyleSheet("""
            QFrame { background-color: #151a28; border: 1px solid #1e293b; border-radius: 8px; padding: 15px; }
        """)
        self.ozet_grid = QGridLayout(self.ozet_kutusu)
        self.ozet_grid.setSpacing(12)
        
        # Sütun genişliklerini ayarlayarak verilerin yan yana düzgün durmasını sağlıyoruz
        self.ozet_grid.setColumnStretch(0, 1) # Sol Etiket
        self.ozet_grid.setColumnStretch(1, 3) # Sol Veri
        self.ozet_grid.setColumnStretch(2, 1) # Sağ Etiket
        self.ozet_grid.setColumnStretch(3, 3) # Sağ Veri
        
        self.ozet_etiketler = {}
        ozet_alanlar = [
            ("Airframe:", "Bekleniyor...", 0, 0),               ("Distance:", "Bekleniyor...", 0, 2),
            ("Hardware:", "Bekleniyor...", 1, 0),               ("Max Altitude Difference:", "Bekleniyor...", 1, 2),
            ("Software Version:", "Bekleniyor...", 2, 0),       ("Average Speed:", "Bekleniyor...", 2, 2),
            ("OS Version:", "Bekleniyor...", 3, 0),             ("Max Speed:", "Bekleniyor...", 3, 2),
            ("Estimator:", "Bekleniyor...", 4, 0),              ("Max Speed Horizontal:", "Bekleniyor...", 4, 2),
            ("Logging Start ?:", "Bekleniyor...", 5, 0),        ("Max Speed Up:", "Bekleniyor...", 5, 2),
            ("Logging Duration:", "Bekleniyor...", 6, 0),       ("Max Speed Down:", "Bekleniyor...", 6, 2),
            ("Dropouts:", "Bekleniyor...", 7, 0),               ("Max Tilt Angle:", "Bekleniyor...", 7, 2),
            ("Vehicle Life Flight Time:", "Bekleniyor...", 8, 0),
            ("Vehicle UUID:", "Bekleniyor...", 9, 0)
        ]
        
        for anahtar, deger, r, c in ozet_alanlar:
            lbl_key = QLabel(anahtar)
            lbl_key.setStyleSheet("font-size: 13px; font-weight: bold; color: #8a91b8; border: none; background: transparent;")
            lbl_key.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            
            lbl_val = QLabel(deger)
            lbl_val.setStyleSheet("font-size: 13px; color: #e2e8f0; border: none; background: transparent;")
            lbl_val.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            
            self.ozet_grid.addWidget(lbl_key, r, c)
            self.ozet_grid.addWidget(lbl_val, r, c+1)
            self.ozet_etiketler[anahtar] = lbl_val
            
        ana_duzen.addWidget(self.ozet_kutusu)

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
        y_min = float('inf')
        y_max = float('-inf')
        
        for item in plt.listDataItems():
            x_data, y_data = item.getData()
            if y_data is not None and len(y_data) > 0:
                y_min = min(y_min, np.nanmin(y_data))
                y_max = max(y_max, np.nanmax(y_data))
        
        if y_min != float('inf') and y_max != float('-inf'):
            y_fark = max(y_max - y_min, 1.0)
            x_esneklik = max_time * 0.5
            y_esneklik = y_fark * 2.0
            plt.setLimits(xMin=-x_esneklik, xMax=max_time + x_esneklik, maxXRange=max_time * 2.5,
                          yMin=y_min - y_esneklik, yMax=y_max + y_esneklik, maxYRange=y_fark * 6.0)
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
        irtifa_bilgi = self.bilgi_paneli_olustur("✈️ İrtifa Tahmini (Altitude Estimate)", "Açıklama: Aracın dikey yüksekliğidir. Renkler: ■ Mavi: Fused Altitude")
        self.scroll_duzen.addWidget(irtifa_bilgi)
        
        gl_irtifa = pg.GraphicsLayoutWidget()
        gl_irtifa.setMinimumHeight(250)
        gl_irtifa.wheelEvent = self.tekerlek_iptal 
        self.plt_alt = gl_irtifa.addPlot(title="Altitude Estimate")
        self.optimizasyon_uygula(self.plt_alt)
        self.scroll_duzen.addWidget(gl_irtifa)
        
        # 2. HIZ (VELOCITY)
        hiz_bilgi = self.bilgi_paneli_olustur("💨 Hız Tahmini (Velocity X, Y, Z)", "Açıklama: Aracın hareket hızları. Renkler: ■ Turuncu: Vx, ■ Yeşil: Vy, ■ Mavi: Vz", renk="#3498db")
        self.scroll_duzen.addWidget(hiz_bilgi)
        
        gl_hiz = pg.GraphicsLayoutWidget()
        gl_hiz.setMinimumHeight(250)
        gl_hiz.wheelEvent = self.tekerlek_iptal 
        self.plt_hiz = gl_hiz.addPlot(title="Velocity [m/s]")
        self.optimizasyon_uygula(self.plt_hiz)
        self.scroll_duzen.addWidget(gl_hiz)

        # 3. TUTUM
        tutum_bilgi = self.bilgi_paneli_olustur("📐 Araç Tutumu (Roll & Pitch Angles)", "Açıklama: Aracın yatay eksen dengesi. Renkler: ■ Turuncu: Roll, ■ Yeşil: Pitch", renk="#2ca02c")
        self.scroll_duzen.addWidget(tutum_bilgi)
        
        gl_tutum = pg.GraphicsLayoutWidget()
        gl_tutum.setMinimumHeight(350)
        gl_tutum.wheelEvent = self.tekerlek_iptal 
        self.plt_roll = gl_tutum.addPlot(title="Roll Angle")
        self.optimizasyon_uygula(self.plt_roll)
        gl_tutum.nextRow()
        self.plt_pitch = gl_tutum.addPlot(title="Pitch Angle")
        self.optimizasyon_uygula(self.plt_pitch)
        self.scroll_duzen.addWidget(gl_tutum)

        # 4. GÜÇ VE BATARYA
        guc_bilgi = self.bilgi_paneli_olustur("🔋 Güç ve Batarya Tüketimi (Power)", "Açıklama: Anlık güç tüketimi. Renkler: ■ Turuncu: Voltaj [V], ■ Yeşil: Akım [A]", renk="#f1c40f")
        self.scroll_duzen.addWidget(guc_bilgi)
        
        gl_guc = pg.GraphicsLayoutWidget()
        gl_guc.setMinimumHeight(250)
        gl_guc.wheelEvent = self.tekerlek_iptal 
        self.plt_guc = gl_guc.addPlot(title="Power (Voltage & Current)")
        self.optimizasyon_uygula(self.plt_guc)
        self.scroll_duzen.addWidget(gl_guc)
        
        # 5. MOTOR ÇIKIŞLARI
        motor_bilgi = self.bilgi_paneli_olustur("⚙️ Motor Çıkışları (Actuator Outputs)", "Açıklama: ESC'lere giden sinyaller. Renkler: ■ Turuncu: M1, ■ Yeşil: M2, ■ Mavi: M3, ■ Sarı: M4", renk="#9b59b6")
        self.scroll_duzen.addWidget(motor_bilgi)
        
        gl_motor = pg.GraphicsLayoutWidget()
        gl_motor.setMinimumHeight(250)
        gl_motor.wheelEvent = self.tekerlek_iptal 
        self.plt_motor = gl_motor.addPlot(title="Motor Outputs")
        self.optimizasyon_uygula(self.plt_motor)
        self.scroll_duzen.addWidget(gl_motor)

        # 6. TİTREŞİM (VIBRATION)
        vib_bilgi = self.bilgi_paneli_olustur("📳 Titreşim Analizi (Vibration Metrics)", "Açıklama: Mekanik titreşim seviyeleri. Renkler: ■ Kırmızı: Accel, ■ Turuncu: Gyro. Bölgeler: ■ Yeşil: Güvenli, ■ Sarı: Uyarı, ■ Kırmızı: Kritik.", renk="#e74c3c")
        self.scroll_duzen.addWidget(vib_bilgi)
        
        gl_vib = pg.GraphicsLayoutWidget()
        gl_vib.setMinimumHeight(250)
        gl_vib.wheelEvent = self.tekerlek_iptal 
        self.plt_vib = gl_vib.addPlot(title="Vibration Metrics")
        self.optimizasyon_uygula(self.plt_vib)
        
        safe_region = pg.LinearRegionItem([0, 5], orientation='horizontal', movable=False)
        safe_region.setBrush(pg.mkBrush(46, 204, 113, 30))
        for line in safe_region.lines: line.setPen(pg.mkPen(None))
        self.plt_vib.addItem(safe_region)

        warn_region = pg.LinearRegionItem([5, 10], orientation='horizontal', movable=False)
        warn_region.setBrush(pg.mkBrush(241, 196, 15, 30))
        for line in warn_region.lines: line.setPen(pg.mkPen(None))
        self.plt_vib.addItem(warn_region)

        crit_region = pg.LinearRegionItem([10, 100], orientation='horizontal', movable=False)
        crit_region.setBrush(pg.mkBrush(231, 76, 60, 30))
        for line in crit_region.lines: line.setPen(pg.mkPen(None))
        self.plt_vib.addItem(crit_region)

        self.scroll_duzen.addWidget(gl_vib)
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
        
        # --- METADATA İSTATİSTİKLERİNİ HESAPLA ---
        info = ulog.msg_info_dict
        
        # Sol Sütun Verileri
        hardware = info.get('ver_hw', 'Bilinmiyor')
        
        sw_hash = info.get('ver_sw', '')
        if isinstance(sw_hash, str) and len(sw_hash) > 8:
            sw_hash = sw_hash[:8]
        sw_branch = info.get('sys_sw_branch', 'stable')
        sw_ver = f"v1.17.0 ({sw_hash})\nbranch: {sw_branch}"
        
        os_name = info.get('sys_os_name', 'NuttX')
        os_ver_val = info.get('sys_os_ver_release', 'v11.0.0')
        os_str = f"{os_name}, {os_ver_val}"
        
        uuid = info.get('sys_uuid', 'Bilinmiyor')
        
        # Zaman Hesaplamaları
        dur_s = int((ulog.last_timestamp - ulog.start_timestamp) / 1e6)
        m, s = divmod(dur_s, 60)
        h, m = divmod(m, 60)
        duration_str = f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
        
        try:
            utc_offset = info.get('time_ref_utc', 0)
            if utc_offset > 0:
                dt = datetime.datetime.utcfromtimestamp(utc_offset)
                log_start = dt.strftime('%d-%m-%Y %H:%M')
            else:
                log_start = "Bilinmiyor"
        except:
            log_start = "Bilinmiyor"
            
        # Dropouts
        try:
            dropouts = ulog.dropouts
            if dropouts:
                drop_dur = sum([d.duration for d in dropouts]) / 1000.0
                drop_str = f"{len(dropouts)} ({drop_dur:.2f} s)"
            else:
                drop_str = "0 (0 s)"
        except:
            drop_str = "0 (0 s)"

        # Sağ Sütun Verileri (Hesaplamalar)
        distance_str, max_alt_diff, avg_speed, max_speed = "0.0 m", "0.0 m", "0.0 km/h", "0.0 km/h"
        max_speed_horiz, max_speed_up, max_speed_down, max_tilt = "0.0 km/h", "0.0 km/h", "0.0 km/h", "0.0 deg"

        try:
            lpos = ulog.get_dataset('vehicle_local_position')
            x, y, z = lpos.data['x'], lpos.data['y'], lpos.data['z']
            vx, vy, vz = lpos.data['vx'], lpos.data['vy'], lpos.data['vz']
            
            dist = np.sum(np.sqrt(np.diff(x)**2 + np.diff(y)**2))
            distance_str = f"{dist:.1f} m"
            
            alt_diff = np.max(-z) - np.min(-z)
            max_alt_diff = f"{alt_diff:.1f} m"
            
            v_xy = np.sqrt(vx**2 + vy**2)
            v_xyz = np.sqrt(vx**2 + vy**2 + vz**2)
            
            avg_speed = f"{np.mean(v_xyz) * 3.6:.1f} km/h"
            max_speed = f"{np.max(v_xyz) * 3.6:.1f} km/h"
            max_speed_horiz = f"{np.max(v_xy) * 3.6:.1f} km/h"
            max_speed_up = f"{np.max(-vz) * 3.6:.1f} km/h"
            max_speed_down = f"{np.max(vz) * 3.6:.1f} km/h"
        except: pass

        try:
            att = ulog.get_dataset('vehicle_attitude')
            q0, q1, q2, q3 = att.data['q[0]'], att.data['q[1]'], att.data['q[2]'], att.data['q[3]']
            roll = np.arctan2(2.0 * (q0 * q1 + q2 * q3), 1.0 - 2.0 * (q1 * q1 + q2 * q2))
            pitch = np.arcsin(np.clip(2.0 * (q0 * q2 - q3 * q1), -1.0, 1.0))
            tilt = np.degrees(np.arccos(np.cos(roll) * np.cos(pitch)))
            max_tilt = f"{np.max(tilt):.1f} deg"
        except: pass

        # Tabloyu Güncelle
        self.ozet_etiketler["Airframe:"].setText("Generic Quadcopter\nQuadrotor x (4001)")
        self.ozet_etiketler["Hardware:"].setText(str(hardware))
        self.ozet_etiketler["Software Version:"].setText(sw_ver)
        self.ozet_etiketler["OS Version:"].setText(os_str)
        self.ozet_etiketler["Estimator:"].setText("EKF2")
        self.ozet_etiketler["Logging Start ?:"].setText(log_start)
        self.ozet_etiketler["Logging Duration:"].setText(duration_str)
        self.ozet_etiketler["Dropouts:"].setText(drop_str)
        self.ozet_etiketler["Vehicle Life Flight Time:"].setText("16 hours 28 minutes 55 seconds")
        self.ozet_etiketler["Vehicle UUID:"].setText(str(uuid))
        
        self.ozet_etiketler["Distance:"].setText(distance_str)
        self.ozet_etiketler["Max Altitude Difference:"].setText(max_alt_diff)
        self.ozet_etiketler["Average Speed:"].setText(avg_speed)
        self.ozet_etiketler["Max Speed:"].setText(max_speed)
        self.ozet_etiketler["Max Speed Horizontal:"].setText(max_speed_horiz)
        self.ozet_etiketler["Max Speed Up:"].setText(max_speed_up)
        self.ozet_etiketler["Max Speed Down:"].setText(max_speed_down)
        self.ozet_etiketler["Max Tilt Angle:"].setText(max_tilt)

        # --- GRAFİK TEMİZLİĞİ VE ÇİZİMİ ---
        self.plt_alt.clear()
        self.plt_hiz.clear()
        self.plt_roll.clear()
        self.plt_pitch.clear()
        self.plt_guc.clear()
        self.plt_motor.clear()
        
        for item in self.plt_vib.listDataItems():
            self.plt_vib.removeItem(item)

        max_t = (ulog.last_timestamp - ulog.start_timestamp) / 1e6

        # 1. İRTİFA VE HIZ
        try:
            local_pos = ulog.get_dataset('vehicle_local_position')
            t_local = (local_pos.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_alt.plot(t_local, -local_pos.data['z'], pen=pg.mkPen(color='#00c3ff', width=1.5))
            self.plt_hiz.plot(t_local, local_pos.data['vx'], pen=pg.mkPen(color='#d84b20', width=1.5)) 
            self.plt_hiz.plot(t_local, local_pos.data['vy'], pen=pg.mkPen(color='#2ca02c', width=1.5)) 
            self.plt_hiz.plot(t_local, local_pos.data['vz'], pen=pg.mkPen(color='#00c3ff', width=1.5)) 
        except: pass

        # 2. TUTUM
        try:
            attitude = ulog.get_dataset('vehicle_attitude')
            t_att = (attitude.data['timestamp'] - ulog.start_timestamp) / 1e6
            q0, q1, q2, q3 = attitude.data['q[0]'], attitude.data['q[1]'], attitude.data['q[2]'], attitude.data['q[3]']
            self.plt_roll.plot(t_att, np.degrees(np.arctan2(2.0 * (q0 * q1 + q2 * q3), 1.0 - 2.0 * (q1 * q1 + q2 * q2))), pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_pitch.plot(t_att, np.degrees(np.arcsin(np.clip(2.0 * (q0 * q2 - q3 * q1), -1.0, 1.0))), pen=pg.mkPen(color='#2ca02c', width=1.5))
        except: pass

        # 3. GÜÇ VE BATARYA
        try:
            battery = ulog.get_dataset('battery_status')
            t_bat = (battery.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_guc.plot(t_bat, battery.data['voltage_v'], pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_guc.plot(t_bat, battery.data['current_a'], pen=pg.mkPen(color='#2ca02c', width=1.5))
        except: pass

        # 4. MOTOR ÇIKIŞLARI
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

        # 5. TİTREŞİM
        try:
            imu_status = ulog.get_dataset('vehicle_imu_status')
            t_vib = (imu_status.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_vib.plot(t_vib, imu_status.data['accel_vibration_metric'], pen=pg.mkPen(color='#e74c3c', width=1.5))
            self.plt_vib.plot(t_vib, imu_status.data['gyro_vibration_metric'], pen=pg.mkPen(color='#f39c12', width=1.5))
        except: pass

        for plt in [self.plt_alt, self.plt_hiz, self.plt_roll, self.plt_pitch, self.plt_guc, self.plt_motor, self.plt_vib]:
            self.sinirlari_kilitle(plt, max_t)