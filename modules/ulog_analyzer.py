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
        irtifa_bilgi = self.bilgi_paneli_olustur(
            "✈️ İrtifa Tahmini (Altitude Estimate)", 
            "Açıklama: Aracın kalkış noktasına veya deniz seviyesine (MSL) göre hesaplanan dikey yüksekliğidir. Fused Altitude, otopilotun barometre ve GPS verilerini Kalman Filtresi (EKF2) ile birleştirerek oluşturduğu net irtifa değerini temsil eder."
        )
        self.scroll_duzen.addWidget(irtifa_bilgi)
        
        gl_irtifa = pg.GraphicsLayoutWidget()
        gl_irtifa.setMinimumHeight(250)
        gl_irtifa.wheelEvent = self.tekerlek_iptal 
        self.plt_alt = gl_irtifa.addPlot(title="Altitude Estimate | <span style='color: #00c3ff;'>Fused Altitude</span>")
        self.plt_alt.showGrid(x=True, y=True, alpha=0.3)
        self.scroll_duzen.addWidget(gl_irtifa)
        
        # 2. TUTUM
        tutum_bilgi = self.bilgi_paneli_olustur(
            "📐 Araç Tutumu (Roll & Pitch Angles)", 
            "Açıklama: Otonom sistemin uçuş sırasındaki yatay eksen dengesini gösterir. Roll (sağ/sol yatış) ve Pitch (ön/arka yunuslama) açılarının davranışı, rüzgar direncinin etkisini ve PID kontrol algoritmasının kararlılığını (stability) ifade eder.", 
            renk="#2ca02c"
        )
        self.scroll_duzen.addWidget(tutum_bilgi)
        
        gl_tutum = pg.GraphicsLayoutWidget()
        gl_tutum.setMinimumHeight(350)
        gl_tutum.wheelEvent = self.tekerlek_iptal 
        
        self.plt_roll = gl_tutum.addPlot(title="Roll Angle | <span style='color: #d84b20;'>Roll Estimated</span>")
        self.plt_roll.showGrid(x=True, y=True, alpha=0.3)
        gl_tutum.nextRow()
        self.plt_pitch = gl_tutum.addPlot(title="Pitch Angle | <span style='color: #2ca02c;'>Pitch Estimated</span>")
        self.plt_pitch.showGrid(x=True, y=True, alpha=0.3)
        self.scroll_duzen.addWidget(gl_tutum)

        # 3. GÜÇ VE BATARYA
        guc_bilgi = self.bilgi_paneli_olustur(
            "🔋 Güç ve Batarya Tüketimi (Power)", 
            "Açıklama: Aracın güç modülü üzerinden okunan anlık batarya voltajı (V) ve çekilen akım (A) değerleridir. Ani akım sıçramaları motorların zorlandığı anları, voltaj düşümleri ise bataryanın deşarj eğilimini gösterir.", 
            renk="#f1c40f"
        )
        self.scroll_duzen.addWidget(guc_bilgi)
        
        gl_guc = pg.GraphicsLayoutWidget()
        gl_guc.setMinimumHeight(250)
        gl_guc.wheelEvent = self.tekerlek_iptal 
        self.plt_guc = gl_guc.addPlot(title="Power | <span style='color: #d84b20;'>Voltage [V]</span> | <span style='color: #2ca02c;'>Current [A]</span>")
        self.plt_guc.showGrid(x=True, y=True, alpha=0.3)
        self.scroll_duzen.addWidget(gl_guc)
        
        # 4. MOTOR ÇIKIŞLARI (YENİ EKLENEN KISIM)
        motor_bilgi = self.bilgi_paneli_olustur(
            "⚙️ Motor Çıkışları (Actuator Outputs)", 
            "Açıklama: Uçuş kontrolcüsünün (ESC'ler üzerinden) motorlara gönderdiği anlık güç sinyalleridir (genellikle 0 ile 1 arasında veya PWM). Sürekli ayrışan veya çok yüksek çalışan bir motor çizgisi; ağırlık merkezindeki (CG) kaymayı, pervane hasarını veya iskelet titreşimlerini işaret eder.", 
            renk="#9b59b6"
        )
        self.scroll_duzen.addWidget(motor_bilgi)
        
        gl_motor = pg.GraphicsLayoutWidget()
        gl_motor.setMinimumHeight(250)
        gl_motor.wheelEvent = self.tekerlek_iptal 
        self.plt_motor = gl_motor.addPlot(title="Motor Outputs | <span style='color: #d84b20;'>Motor 1</span> | <span style='color: #2ca02c;'>Motor 2</span> | <span style='color: #00c3ff;'>Motor 3</span> | <span style='color: #f1c40f;'>Motor 4</span>")
        self.plt_motor.showGrid(x=True, y=True, alpha=0.3)
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
        self.plt_roll.clear()
        self.plt_pitch.clear()
        self.plt_guc.clear()
        self.plt_motor.clear()

        # --- 1. İRTİFA ---
        try:
            local_pos = ulog.get_dataset('vehicle_local_position')
            self.plt_alt.plot((local_pos.data['timestamp'] - ulog.start_timestamp) / 1e6, -local_pos.data['z'], pen=pg.mkPen(color='#00c3ff', width=1.5))
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
            voltage = battery.data['voltage_v']
            current = battery.data['current_a']
            self.plt_guc.plot(t_bat, voltage, pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_guc.plot(t_bat, current, pen=pg.mkPen(color='#2ca02c', width=1.5))
        except: pass

        # --- 4. MOTOR ÇIKIŞLARI ---
        try:
            # Modern PX4 versiyonlarında actuator_motors olarak gelir
            motors = ulog.get_dataset('actuator_motors')
            t_mot = (motors.data['timestamp'] - ulog.start_timestamp) / 1e6
            m1 = motors.data['control[0]']
            m2 = motors.data['control[1]']
            m3 = motors.data['control[2]']
            m4 = motors.data['control[3]']
            
            self.plt_motor.plot(t_mot, m1, pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_motor.plot(t_mot, m2, pen=pg.mkPen(color='#2ca02c', width=1.5))
            self.plt_motor.plot(t_mot, m3, pen=pg.mkPen(color='#00c3ff', width=1.5))
            self.plt_motor.plot(t_mot, m4, pen=pg.mkPen(color='#f1c40f', width=1.5))
        except:
            try:
                # Eski tip otopilot logları veya alternatif çıkışlar için
                outputs = ulog.get_dataset('actuator_outputs')
                t_out = (outputs.data['timestamp'] - ulog.start_timestamp) / 1e6
                o1 = outputs.data['output[0]']
                o2 = outputs.data['output[1]']
                o3 = outputs.data['output[2]']
                o4 = outputs.data['output[3]']
                
                self.plt_motor.plot(t_out, o1, pen=pg.mkPen(color='#d84b20', width=1.5))
                self.plt_motor.plot(t_out, o2, pen=pg.mkPen(color='#2ca02c', width=1.5))
                self.plt_motor.plot(t_out, o3, pen=pg.mkPen(color='#00c3ff', width=1.5))
                self.plt_motor.plot(t_out, o4, pen=pg.mkPen(color='#f1c40f', width=1.5))
            except Exception as e:
                print("Motor verisi çizilemedi:", e)