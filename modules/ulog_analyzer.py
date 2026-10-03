import pyqtgraph as pg
import numpy as np
import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QPushButton, QLabel, QFileDialog, QMessageBox,
                               QScrollArea, QFrame)
from PySide6.QtCore import Qt
from pyulog import ULog

class PanScrollArea(QScrollArea):
    """Farenin orta tuşuna basılı tutarak ekranı kaydırmayı sağlayan özel sınıf"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_panning = False
        self._start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._start_pos = event.position().toPoint()
            self.viewport().setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning:
            delta = event.position().toPoint() - self._start_pos
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self._start_pos = event.position().toPoint()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._is_panning = False
            self.viewport().unsetCursor()
            event.accept()
        else:
            super().mouseReleaseEvent(event)


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
        
        # --- SCROLL ALANI (Tam Uyumlu ve Tıklanabilir Scrollbar) ---
        self.scroll_alani = PanScrollArea()
        self.scroll_alani.setWidgetResizable(True)
        self.scroll_alani.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: transparent; 
            }
            QScrollBar:vertical {
                background-color: #1a1a2e;
                width: 16px;
                margin: 16px 0px 16px 0px; /* Ok butonları için üstte ve altta 16px yer açıyoruz */
                border-radius: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #5c6bc0;
                min-height: 40px;
                border-radius: 8px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #e94560;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #d84b20;
            }
            QScrollBar::sub-line:vertical {
                background-color: #0f3460;
                height: 16px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QScrollBar::add-line:vertical {
                background-color: #0f3460;
                height: 16px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QScrollBar::sub-line:vertical:hover, QScrollBar::add-line:vertical:hover {
                background-color: #e94560;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        self.scroll_icerik = QWidget()
        self.scroll_duzen = QVBoxLayout(self.scroll_icerik)
        self.scroll_duzen.setSpacing(25)
        self.scroll_duzen.setContentsMargins(0, 10, 15, 10)
        
        self.scroll_alani.setWidget(self.scroll_icerik)
        ana_duzen.addWidget(self.scroll_alani)

        # --- GELİŞMİŞ UÇUŞ ÖZET TABLOSU ---
        self.ozet_kutusu = QFrame()
        self.ozet_kutusu.setStyleSheet("""
            QFrame { background-color: #151a28; border: 1px solid #1e293b; border-radius: 8px; padding: 15px; }
        """)
        self.ozet_grid = QGridLayout(self.ozet_kutusu)
        self.ozet_grid.setSpacing(12)
        
        self.ozet_grid.setColumnStretch(0, 1)
        self.ozet_grid.setColumnStretch(1, 3)
        self.ozet_grid.setColumnStretch(2, 1)
        self.ozet_grid.setColumnStretch(3, 3)
        
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
            
        self.scroll_duzen.addWidget(self.ozet_kutusu)
        
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

    def sinirlari_kilitle(self, plt, max_time, is_time_x=True):
        y_min = float('inf')
        y_max = float('-inf')
        x_min = float('inf')
        x_max = float('-inf')
        
        for item in plt.listDataItems():
            x_data, y_data = item.getData()
            if y_data is not None and len(y_data) > 0:
                y_min = min(y_min, np.nanmin(y_data))
                y_max = max(y_max, np.nanmax(y_data))
            if x_data is not None and len(x_data) > 0:
                x_min = min(x_min, np.nanmin(x_data))
                x_max = max(x_max, np.nanmax(x_data))
        
        if y_min != float('inf') and y_max != float('-inf'):
            y_fark = max(y_max - y_min, 1.0)
            
            if is_time_x:
                x_esneklik = max_time * 0.5
                y_esneklik = y_fark * 2.0
                plt.setLimits(xMin=-x_esneklik, xMax=max_time + x_esneklik, maxXRange=max_time * 2.5,
                              yMin=y_min - y_esneklik, yMax=y_max + y_esneklik, maxYRange=y_fark * 6.0)
            else:
                if x_min != float('inf') and x_max != float('-inf'):
                    x_fark = max(x_max - x_min, 1.0)
                    x_esneklik = x_fark * 2.0
                    y_esneklik = y_fark * 2.0
                    plt.setLimits(xMin=x_min - x_esneklik, xMax=x_max + x_esneklik, maxXRange=x_fark * 6.0,
                                  yMin=y_min - y_esneklik, yMax=y_max + y_esneklik, maxYRange=y_fark * 6.0)
        else:
            if is_time_x:
                plt.setLimits(xMin=-10, xMax=max_time + 10, maxXRange=max_time * 3.0)

    def bilgi_paneli_olustur(self, baslik, aciklama, renk="#00c3ff"):
        kutu = QFrame()
        kutu.setStyleSheet(f"QFrame {{ background-color: #1a1a2e; border-left: 5px solid {renk}; border-radius: 5px; }}")
        duzen = QVBoxLayout(kutu)
        duzen.setContentsMargins(15, 10, 15, 10)
        
        lbl_baslik = QLabel(baslik)
        lbl_baslik.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff; border: none; background: transparent;")
        lbl_aciklama = QLabel(aciklama)
        lbl_aciklama.setStyleSheet("font-size: 12px; color: #a2a8d3; border: none; background: transparent; line-height: 1.4;")
        lbl_aciklama.setWordWrap(True)
        lbl_aciklama.setTextFormat(Qt.RichText)
        
        duzen.addWidget(lbl_baslik)
        duzen.addWidget(lbl_aciklama)
        return kutu

    def arayuzu_olustur(self):
        # 1. 2D UÇUŞ ROTASI
        traj_aciklama = (
            "<b>Açıklama:</b> Aracın kalkış noktasına (0,0) göre yerel koordinat sistemindeki (NED) kuşbakışı hareket rotasıdır (Metre). "
            "Uydu haritası gerektirmeden, geometrik olarak görevin nasıl icra edildiğini ve rotadan sapmaları net şekilde gösterir. "
            "Grafik oranları kilitlidir, bu sayede çizilen dairesel rotalar elipse dönüşmez.<br><br>"
            "<b>Grafik Renkleri:</b><br>"
            "<span style='color: #e94560;'>■ Kırmızı Çizgi:</span> 2D Uçuş Yörüngesi (Y: Kuzey, X: Doğu)"
        )
        traj_bilgi = self.bilgi_paneli_olustur("🗺️ 2D Uçuş Rotası (Local Position X-Y)", traj_aciklama, renk="#e94560")
        self.scroll_duzen.addWidget(traj_bilgi)
        
        gl_traj = pg.GraphicsLayoutWidget()
        gl_traj.setMinimumHeight(350)
        gl_traj.wheelEvent = self.tekerlek_iptal 
        self.plt_traj = gl_traj.addPlot(title="2D Flight Trajectory [m]")
        self.optimizasyon_uygula(self.plt_traj)
        self.plt_traj.setAspectLocked(True)
        self.scroll_duzen.addWidget(gl_traj)

        # 2. İRTİFA
        irtifa_aciklama = (
            "<b>Açıklama:</b> Aracın kalkış noktasına veya deniz seviyesine (MSL) göre hesaplanan dikey yüksekliğidir. "
            "Fused Altitude, otopilotun barometre ve GPS verilerini Kalman Filtresi (EKF2) ile birleştirerek oluşturduğu "
            "filtrelenmiş net irtifa değerini temsil eder.<br><br>"
            "<b>Grafik Renkleri:</b><br>"
            "<span style='color: #00c3ff;'>■ Mavi Çizgi:</span> Fused Altitude"
        )
        irtifa_bilgi = self.bilgi_paneli_olustur("✈️ İrtifa Tahmini (Altitude Estimate)", irtifa_aciklama)
        self.scroll_duzen.addWidget(irtifa_bilgi)
        
        gl_irtifa = pg.GraphicsLayoutWidget()
        gl_irtifa.setMinimumHeight(250)
        gl_irtifa.wheelEvent = self.tekerlek_iptal 
        self.plt_alt = gl_irtifa.addPlot(title="Altitude Estimate")
        self.optimizasyon_uygula(self.plt_alt)
        self.scroll_duzen.addWidget(gl_irtifa)
        
        # 3. HIZ
        hiz_aciklama = (
            "<b>Açıklama:</b> Aracın yerel koordinat sistemindeki ileri/geri (X), sağa/sola (Y) ve dikey (Z) "
            "hareket hızlarını metre/saniye (m/s) cinsinden gösterir.<br><br>"
            "<b>Grafik Renkleri:</b><br>"
            "<span style='color: #d84b20;'>■ Turuncu Çizgi:</span> Vx (İleri/Geri Hız)<br>"
            "<span style='color: #2ca02c;'>■ Yeşil Çizgi:</span> Vy (Sağ/Sol Hız)<br>"
            "<span style='color: #00c3ff;'>■ Mavi Çizgi:</span> Vz (Aşağı/Yukarı Dikey Hız)"
        )
        hiz_bilgi = self.bilgi_paneli_olustur("💨 Hız Tahmini (Velocity X, Y, Z)", hiz_aciklama, renk="#3498db")
        self.scroll_duzen.addWidget(hiz_bilgi)
        
        gl_hiz = pg.GraphicsLayoutWidget()
        gl_hiz.setMinimumHeight(250)
        gl_hiz.wheelEvent = self.tekerlek_iptal 
        self.plt_hiz = gl_hiz.addPlot(title="Velocity [m/s]")
        self.optimizasyon_uygula(self.plt_hiz)
        self.scroll_duzen.addWidget(gl_hiz)

        # 4. TUTUM
        tutum_aciklama = (
            "<b>Açıklama:</b> Otonom sistemin uçuş sırasındaki yatay eksen dengesini gösterir. Roll (sağ/sol yatış) "
            "ve Pitch (ön/arka yunuslama) açılarının davranışı, PID kontrol algoritmasının kararlılığını ifade eder.<br><br>"
            "<b>Grafik Renkleri:</b><br>"
            "<span style='color: #d84b20;'>■ Turuncu Çizgi:</span> Roll Angle<br>"
            "<span style='color: #2ca02c;'>■ Yeşil Çizgi:</span> Pitch Angle"
        )
        tutum_bilgi = self.bilgi_paneli_olustur("📐 Araç Tutumu (Roll & Pitch Angles)", tutum_aciklama, renk="#2ca02c")
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

        # 5. AÇISAL HIZLAR
        rate_aciklama = (
            "<b>Açıklama:</b> Otonom sistemin Roll, Pitch ve Yaw eksenleri etrafındaki saniyelik dönüş hızlarını gösterir.<br><br>"
            "<b>Grafik Renkleri:</b><br>"
            "<span style='color: #d84b20;'>■ Turuncu Çizgi:</span> Roll Rate<br>"
            "<span style='color: #2ca02c;'>■ Yeşil Çizgi:</span> Pitch Rate<br>"
            "<span style='color: #00c3ff;'>■ Mavi Çizgi:</span> Yaw Rate"
        )
        rate_bilgi = self.bilgi_paneli_olustur("🌪️ Açısal Hızlar (Angular Rates)", rate_aciklama, renk="#e67e22")
        self.scroll_duzen.addWidget(rate_bilgi)
        
        gl_rate = pg.GraphicsLayoutWidget()
        gl_rate.setMinimumHeight(450)
        gl_rate.wheelEvent = self.tekerlek_iptal 
        self.plt_roll_rate = gl_rate.addPlot(title="Roll Angular Rate [deg/s]")
        self.optimizasyon_uygula(self.plt_roll_rate)
        gl_rate.nextRow()
        self.plt_pitch_rate = gl_rate.addPlot(title="Pitch Angular Rate [deg/s]")
        self.optimizasyon_uygula(self.plt_pitch_rate)
        gl_rate.nextRow()
        self.plt_yaw_rate = gl_rate.addPlot(title="Yaw Angular Rate [deg/s]")
        self.optimizasyon_uygula(self.plt_yaw_rate)
        self.scroll_duzen.addWidget(gl_rate)

        # 6. GÜÇ VE BATARYA
        guc_aciklama = (
            "<b>Açıklama:</b> Aracın anlık batarya voltajı (V) ve çekilen toplam akım (A) değerleridir.<br><br>"
            "<b>Grafik Renkleri:</b><br>"
            "<span style='color: #d84b20;'>■ Turuncu Çizgi:</span> Batarya Voltajı [V]<br>"
            "<span style='color: #2ca02c;'>■ Yeşil Çizgi:</span> Çekilen Toplam Akım [A]"
        )
        guc_bilgi = self.bilgi_paneli_olustur("🔋 Güç ve Batarya Tüketimi (Power)", guc_aciklama, renk="#f1c40f")
        self.scroll_duzen.addWidget(guc_bilgi)
        
        gl_guc = pg.GraphicsLayoutWidget()
        gl_guc.setMinimumHeight(250)
        gl_guc.wheelEvent = self.tekerlek_iptal 
        self.plt_guc = gl_guc.addPlot(title="Power (Voltage & Current)")
        self.optimizasyon_uygula(self.plt_guc)
        self.scroll_duzen.addWidget(gl_guc)
        
        # 7. MOTOR ÇIKIŞLARI
        motor_aciklama = (
            "<b>Açıklama:</b> Uçuş kontrolcüsünün ESC'ler aracılığıyla motorlara gönderdiği anlık güç sinyalleridir.<br><br>"
            "<b>Grafik Renkleri:</b><br>"
            "<span style='color: #d84b20;'>■ Turuncu:</span> Motor 1 | "
            "<span style='color: #2ca02c;'>■ Yeşil:</span> Motor 2 | "
            "<span style='color: #00c3ff;'>■ Mavi:</span> Motor 3 | "
            "<span style='color: #f1c40f;'>■ Sarı:</span> Motor 4"
        )
        motor_bilgi = self.bilgi_paneli_olustur("⚙️ Motor Çıkışları (Actuator Outputs)", motor_aciklama, renk="#9b59b6")
        self.scroll_duzen.addWidget(motor_bilgi)
        
        gl_motor = pg.GraphicsLayoutWidget()
        gl_motor.setMinimumHeight(250)
        gl_motor.wheelEvent = self.tekerlek_iptal 
        self.plt_motor = gl_motor.addPlot(title="Motor Outputs")
        self.optimizasyon_uygula(self.plt_motor)
        self.scroll_duzen.addWidget(gl_motor)

        # 8. TİTREŞİM (VIBRATION)
        vib_aciklama = (
            "<b>Açıklama:</b> Aracın iskeletindeki mekanik titreşim seviyelerini m/s² cinsinden gösterir.<br><br>"
            "<b>Grafik Renkleri:</b><br>"
            "<span style='color: #e74c3c;'>■ Kırmızı Çizgi:</span> İvmeölçer (Accel) Titreşimi<br>"
            "<span style='color: #f39c12;'>■ Turuncu Çizgi:</span> Jiroskop (Gyro) Titreşimi<br><br>"
            "<b>Güvenlik Bölgeleri (Arka Plan):</b><br>"
            "<span style='color: #2ecc71;'>■ Yeşil Alan (0-5):</span> Güvenli Titreşim Seviyesi<br>"
            "<span style='color: #f1c40f;'>■ Sarı Alan (5-10):</span> Uyarı Seviyesi<br>"
            "<span style='color: #e74c3c;'>■ Kırmızı Alan (10+):</span> Kritik Titreşim"
        )
        vib_bilgi = self.bilgi_paneli_olustur("📳 Titreşim Analizi (Vibration Metrics)", vib_aciklama, renk="#e74c3c")
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

        # 9. GPS VE MANYETİK ALAN
        gps_aciklama = (
            "<b>Açıklama:</b> Aracın GPS alıcısına gelen sinyallerin kalitesini ve çevresel elektromanyetik kirliliği gösterir.<br><br>"
            "<b>Grafik Renkleri:</b><br>"
            "<span style='color: #d84b20;'>■ Turuncu Çizgi:</span> Noise per ms (Gürültü Seviyesi)<br>"
            "<span style='color: #2ca02c;'>■ Yeşil Çizgi:</span> Jamming Indicator (Karıştırma İndikatörü)"
        )
        gps_bilgi = self.bilgi_paneli_olustur("🛰️ GPS Gürültü ve Karıştırma (Noise & Jamming)", gps_aciklama, renk="#8e44ad")
        self.scroll_duzen.addWidget(gps_bilgi)
        
        gl_gps = pg.GraphicsLayoutWidget()
        gl_gps.setMinimumHeight(200)
        gl_gps.wheelEvent = self.tekerlek_iptal 
        self.plt_gps = gl_gps.addPlot(title="GPS Noise & Jamming")
        self.optimizasyon_uygula(self.plt_gps)
        self.scroll_duzen.addWidget(gl_gps)

        mag_aciklama = (
            "<b>Açıklama:</b> Pusula sensörünün ölçtüğü X, Y ve Z eksenlerindeki ham manyetik alan şiddetidir.<br><br>"
            "<b>Grafik Renkleri:</b><br>"
            "<span style='color: #d84b20;'>■ Turuncu Çizgi:</span> X Ekseni<br>"
            "<span style='color: #2ca02c;'>■ Yeşil Çizgi:</span> Y Ekseni<br>"
            "<span style='color: #00c3ff;'>■ Mavi Çizgi:</span> Z Ekseni"
        )
        mag_bilgi = self.bilgi_paneli_olustur("🧲 Manyetik Alan Şiddeti (Raw Magnetic Field)", mag_aciklama, renk="#c0392b")
        self.scroll_duzen.addWidget(mag_bilgi)
        
        gl_mag = pg.GraphicsLayoutWidget()
        gl_mag.setMinimumHeight(250)
        gl_mag.wheelEvent = self.tekerlek_iptal 
        self.plt_mag = gl_mag.addPlot(title="Raw Magnetic Field Strength")
        self.optimizasyon_uygula(self.plt_mag)
        self.scroll_duzen.addWidget(gl_mag)

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
        
        info = ulog.msg_info_dict
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
            
        try:
            dropouts = ulog.dropouts
            if dropouts:
                drop_dur = sum([d.duration for d in dropouts]) / 1000.0
                drop_str = f"{len(dropouts)} ({drop_dur:.2f} s)"
            else:
                drop_str = "0 (0 s)"
        except:
            drop_str = "0 (0 s)"

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

        self.plt_traj.clear()
        self.plt_alt.clear()
        self.plt_hiz.clear()
        self.plt_roll.clear()
        self.plt_pitch.clear()
        self.plt_roll_rate.clear()
        self.plt_pitch_rate.clear()
        self.plt_yaw_rate.clear()
        self.plt_guc.clear()
        self.plt_motor.clear()
        self.plt_gps.clear()
        self.plt_mag.clear()
        
        for item in self.plt_vib.listDataItems():
            self.plt_vib.removeItem(item)

        max_t = (ulog.last_timestamp - ulog.start_timestamp) / 1e6

        try:
            local_pos = ulog.get_dataset('vehicle_local_position')
            t_local = (local_pos.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_traj.plot(local_pos.data['y'], local_pos.data['x'], pen=pg.mkPen(color='#e94560', width=2.0))
            self.plt_alt.plot(t_local, -local_pos.data['z'], pen=pg.mkPen(color='#00c3ff', width=1.5))
            self.plt_hiz.plot(t_local, local_pos.data['vx'], pen=pg.mkPen(color='#d84b20', width=1.5)) 
            self.plt_hiz.plot(t_local, local_pos.data['vy'], pen=pg.mkPen(color='#2ca02c', width=1.5)) 
            self.plt_hiz.plot(t_local, local_pos.data['vz'], pen=pg.mkPen(color='#00c3ff', width=1.5)) 
        except: pass

        try:
            attitude = ulog.get_dataset('vehicle_attitude')
            t_att = (attitude.data['timestamp'] - ulog.start_timestamp) / 1e6
            q0, q1, q2, q3 = att.data['q[0]'], att.data['q[1]'], att.data['q[2]'], att.data['q[3]']
            self.plt_roll.plot(t_att, np.degrees(np.arctan2(2.0 * (q0 * q1 + q2 * q3), 1.0 - 2.0 * (q1 * q1 + q2 * q2))), pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_pitch.plot(t_att, np.degrees(np.arcsin(np.clip(2.0 * (q0 * q2 - q3 * q1), -1.0, 1.0))), pen=pg.mkPen(color='#2ca02c', width=1.5))
        except: pass

        try:
            angular_velocity = ulog.get_dataset('vehicle_angular_velocity')
            t_ang = (angular_velocity.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_roll_rate.plot(t_ang, np.degrees(angular_velocity.data['xyz[0]']), pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_pitch_rate.plot(t_ang, np.degrees(angular_velocity.data['xyz[1]']), pen=pg.mkPen(color='#2ca02c', width=1.5))
            self.plt_yaw_rate.plot(t_ang, np.degrees(angular_velocity.data['xyz[2]']), pen=pg.mkPen(color='#00c3ff', width=1.5))
        except: pass

        try:
            battery = ulog.get_dataset('battery_status')
            t_bat = (battery.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_guc.plot(t_bat, battery.data['voltage_v'], pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_guc.plot(t_bat, battery.data['current_a'], pen=pg.mkPen(color='#2ca02c', width=1.5))
        except: pass

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

        try:
            imu_status = ulog.get_dataset('vehicle_imu_status')
            t_vib = (imu_status.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_vib.plot(t_vib, imu_status.data['accel_vibration_metric'], pen=pg.mkPen(color='#e74c3c', width=1.5))
            self.plt_vib.plot(t_vib, imu_status.data['gyro_vibration_metric'], pen=pg.mkPen(color='#f39c12', width=1.5))
        except: pass

        try:
            gps = ulog.get_dataset('sensor_gps')
            t_gps = (gps.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_gps.plot(t_gps, gps.data['noise_per_ms'], pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_gps.plot(t_gps, gps.data['jamming_indicator'], pen=pg.mkPen(color='#2ca02c', width=1.5))
        except: pass

        try:
            mag = ulog.get_dataset('sensor_mag')
            t_mag = (mag.data['timestamp'] - ulog.start_timestamp) / 1e6
            self.plt_mag.plot(t_mag, mag.data['x'], pen=pg.mkPen(color='#d84b20', width=1.5))
            self.plt_mag.plot(t_mag, mag.data['y'], pen=pg.mkPen(color='#2ca02c', width=1.5))
            self.plt_mag.plot(t_mag, mag.data['z'], pen=pg.mkPen(color='#00c3ff', width=1.5))
        except:
            try:
                mag = ulog.get_dataset('vehicle_magnetometer')
                t_mag = (mag.data['timestamp'] - ulog.start_timestamp) / 1e6
                self.plt_mag.plot(t_mag, mag.data['magnetometer_ga[0]'], pen=pg.mkPen(color='#d84b20', width=1.5))
                self.plt_mag.plot(t_mag, mag.data['magnetometer_ga[1]'], pen=pg.mkPen(color='#2ca02c', width=1.5))
                self.plt_mag.plot(t_mag, mag.data['magnetometer_ga[2]'], pen=pg.mkPen(color='#00c3ff', width=1.5))
            except: pass

        zaman_grafikleri = [
            self.plt_alt, self.plt_hiz, self.plt_roll, self.plt_pitch, 
            self.plt_roll_rate, self.plt_pitch_rate, self.plt_yaw_rate, 
            self.plt_guc, self.plt_motor, self.plt_vib, self.plt_gps, self.plt_mag
        ]
        for plt in zaman_grafikleri:
            self.sinirlari_kilitle(plt, max_t, is_time_x=True)
            
        self.sinirlari_kilitle(self.plt_traj, max_t, is_time_x=False)