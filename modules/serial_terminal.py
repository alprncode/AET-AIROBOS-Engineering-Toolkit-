from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QComboBox, QPushButton, QLabel, QTextEdit, QLineEdit)

class SerialTerminalWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("Seri Port Terminali (Serial Terminal)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        ana_duzen.addWidget(baslik)
        
        # 1. Bağlantı Ayarları (Port ve Baudrate)
        ayar_duzeni = QHBoxLayout()
        
        ayar_duzeni.addWidget(QLabel("Port:"))
        self.port_secim = QComboBox()
        self.port_secim.addItems(["COM1", "COM2", "COM3", "COM4", "COM5"]) # Temsili portlar
        ayar_duzeni.addWidget(self.port_secim)
        
        ayar_duzeni.addWidget(QLabel("Baudrate:"))
        self.baud_secim = QComboBox()
        self.baud_secim.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_secim.setCurrentText("115200") # Otonom sistemlerde sık kullanılan hız
        ayar_duzeni.addWidget(self.baud_secim)
        
        self.baglan_butonu = QPushButton("Bağlan")
        self.baglan_butonu.setStyleSheet("font-weight: bold; color: blue;")
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
        self.baglan_butonu.clicked.connect(self.baglanti_degistir)
        self.gonder_butonu.clicked.connect(self.veri_gonder)

    def baglanti_degistir(self):
        port = self.port_secim.currentText()
        baud = self.baud_secim.currentText()
        
        if not self.bagli_mi:
            self.terminal_ekrani.append(f"[{port}] {baud} baud hızında bağlanılıyor... (Simülasyon)")
            self.terminal_ekrani.append("Bağlantı başarılı. Veri bekleniyor...\n")
            self.baglan_butonu.setText("Bağlantıyı Kes")
            self.baglan_butonu.setStyleSheet("font-weight: bold; color: red;")
            self.bagli_mi = True
        else:
            self.terminal_ekrani.append(f"[{port}] Bağlantı kesildi.\n")
            self.baglan_butonu.setText("Bağlan")
            self.baglan_butonu.setStyleSheet("font-weight: bold; color: blue;")
            self.bagli_mi = False

    def veri_gonder(self):
        if not self.bagli_mi:
            self.terminal_ekrani.append("HATA: Önce bir porta bağlanmalısınız!")
            return
            
        komut = self.veri_girisi.text()
        if komut:
            self.terminal_ekrani.append(f"-> GİDEN: {komut}")
            self.veri_girisi.clear()