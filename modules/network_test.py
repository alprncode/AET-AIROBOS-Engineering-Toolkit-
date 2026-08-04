import subprocess
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLineEdit, QPushButton, QLabel, QTextEdit)

class NetworkTestWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        ana_duzen = QVBoxLayout(self)
        
        baslik = QLabel("Ağ Testi (Ping Aracı)")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        ana_duzen.addWidget(baslik)
        
        # 1. IP / URL Giriş Alanı
        ip_duzeni = QHBoxLayout()
        ip_duzeni.addWidget(QLabel("Hedef IP veya Adres:"))
        self.ip_girisi = QLineEdit()
        self.ip_girisi.setPlaceholderText("Örn: 192.168.1.1 veya google.com")
        ip_duzeni.addWidget(self.ip_girisi)
        ana_duzen.addLayout(ip_duzeni)
        
        # 2. Ping Butonu
        self.ping_butonu = QPushButton("Bağlantıyı Test Et (Ping)")
        self.ping_butonu.setStyleSheet("padding: 8px; font-weight: bold;")
        ana_duzen.addWidget(self.ping_butonu)
        
        # 3. Sonuç Ekranı (Siyah arka plan, yeşil yazı ile terminal görünümü)
        self.sonuc_ekrani = QTextEdit()
        self.sonuc_ekrani.setReadOnly(True)
        self.sonuc_ekrani.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 14px;")
        ana_duzen.addWidget(self.sonuc_ekrani)
        
        ana_duzen.addStretch()

        # Buton Bağlantısı
        self.ping_butonu.clicked.connect(self.ping_at)

    def ping_at(self):
        ip_adresi = self.ip_girisi.text().strip()
        
        if not ip_adresi:
            self.sonuc_ekrani.setText("HATA: Lütfen geçerli bir IP adresi veya web sitesi girin!")
            return
            
        self.sonuc_ekrani.setText(f">>> {ip_adresi} adresine ping gönderiliyor. Lütfen bekleyin...\n")
        # Arayüzün donmaması için kısa bir bekleme süresi verip ping'i arkada çalıştırıyoruz
        self.repaint() 
        
        try:
            # Windows'un kendi ping komutunu 4 paket (-n 4) gönderecek şekilde çalıştırıyoruz
            sonuc = subprocess.run(["ping", "-n", "4", ip_adresi], capture_output=True, text=True, shell=True)
            
            # Gelen sonucu (stdout) yeşil ekrana ekliyoruz
            if sonuc.returncode == 0:
                self.sonuc_ekrani.append(sonuc.stdout)
            else:
                self.sonuc_ekrani.append("--- BAĞLANTI HATASI ---\nHedefe ulaşılamadı veya zaman aşımına uğradı.\n")
                self.sonuc_ekrani.append(sonuc.stdout)
                
        except Exception as e:
            self.sonuc_ekrani.append(f"Sistem Hatası: {str(e)}")