import serial.tools.list_ports
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QComboBox, QPushButton, QLabel, QTextEdit, QLineEdit)

class SerialTerminalWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("Seri Port Terminali (Gerçek Donanım Taraması)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #00c3ff;")
        ana_duzen.addWidget(baslik)
        
        # 1. Bağlantı Ayarları (Port ve Baudrate)
        ayar_duzeni = QHBoxLayout()
        
        ayar_duzeni.addWidget(QLabel("Port:"))
        self.port_secim = QComboBox()
        ayar_duzeni.addWidget(self.port_secim)
        
        # Gerçek zamanlı tarama butonu
        self.yenile_butonu = QPushButton("Donanımları Tara")
        self.yenile_butonu.setStyleSheet("background-color: #d84b20; font-weight: bold;")
        ayar_duzeni.addWidget(self.yenile_butonu)
        
        ayar_duzeni.addWidget(QLabel("Baudrate:"))
        self.baud_secim = QComboBox()
        self.baud_secim.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_secim.setCurrentText("115200")
        ayar_duzeni.addWidget(self.baud_secim)
        
        self.baglan_butonu = QPushButton("Bağlan")
        self.baglan_butonu.setStyleSheet("background-color: #007acc; font-weight: bold;")
        ayar_duzeni.addWidget(self.baglan_butonu)
        
        ana_duzen.addLayout(ayar_duzeni)
        
        # 2. Gelen Veri (Log) Ekranı
        ana_duzen.addWidget(QLabel("Gelen Veri:"))
        self.terminal_ekrani = QTextEdit()
        self.terminal_ekrani.setReadOnly(True)
        self.terminal_ekrani.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 14px;")
        ana_duzen.addWidget(self.terminal_ekrani)
        
        # 3. Veri Gönderme Alanı
        gonder_duzeni = QHBoxLayout()
        self.veri_girisi = QLineEdit()
        self.veri_girisi.setPlaceholderText("Gönderilecek komutu buraya yazın...")
        gonder_duzeni.addWidget(self.veri_girisi)
        
        self.gonder_butonu = QPushButton("Gönder")
        gonder_duzeni.addWidget(self.gonder_butonu)
        ana_duzen.addLayout(gonder_duzeni)
        
        # 4. Durum Değişkeni ve Buton Bağlantıları
        self.bagli_mi = False
        self.yenile_butonu.clicked.connect(self.portlari_tara)
        self.baglan_butonu.clicked.connect(self.baglanti_degistir)
        self.gonder_butonu.clicked.connect(self.veri_gonder)
        
        # Arayüz açıldığında portları otomatik olarak bir kez tara
        self.portlari_tara()

    def portlari_tara(self):
        self.port_secim.clear()
        # İşletim sistemindeki bağlı COM portlarını buluyoruz
        portlar = serial.tools.list_ports.comports()
        
        if not portlar:
            self.port_secim.addItem("Port Bulunamadı")
        else:
            for port in portlar:
                # Bulunan gerçek COM portlarını listeye ekliyoruz
                self.port_secim.addItem(port.device)
        
        self.terminal_ekrani.append("--- Sistemdeki donanımlar tarandı ---")

    def baglanti_degistir(self):
        port = self.port_secim.currentText()
        baud = self.baud_secim.currentText()
        
        if port == "Port Bulunamadı" or not port:
            self.terminal_ekrani.append("HATA: Bağlanılacak geçerli bir port (donanım) yok!")
            return
            
        if not self.bagli_mi:
            self.terminal_ekrani.append(f"[{port}] {baud} baud hızında bağlanılıyor... (Simülasyon)")
            self.terminal_ekrani.append("Bağlantı başarılı. Veri bekleniyor...\n")
            self.baglan_butonu.setText("Bağlantıyı Kes")
            self.baglan_butonu.setStyleSheet("background-color: #8b0000; font-weight: bold;")
            self.bagli_mi = True
        else:
            self.terminal_ekrani.append(f"[{port}] Bağlantı kesildi.\n")
            self.baglan_butonu.setText("Bağlan")
            self.baglan_butonu.setStyleSheet("background-color: #007acc; font-weight: bold;")
            self.bagli_mi = False

    def veri_gonder(self):
        if not self.bagli_mi:
            self.terminal_ekrani.append("HATA: Önce bir porta bağlanmalısınız!")
            return
            
        komut = self.veri_girisi.text()
        if komut:
            self.terminal_ekrani.append(f"-> GİDEN: {komut}")
            self.veri_girisi.clear()