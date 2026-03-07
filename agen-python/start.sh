#!/bin/bash
# ======================================================================
# THE CLONE WARS: Skrip Penghidup Layar Hantu (Virtual Framebuffer)
# ======================================================================

echo "👻 Membangkitkan Layar Hantu Xvfb pada Display :99 (Resolusi 1920x1080)..."
# Hidupkan server Display palsu di background
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &

# Simpan PID dari Xvfb agar kita bisa mematikannya nanti jika crash
XVFB_PID=$!

# Beri waktu sedetik agar Xvfb benar-benar siap
sleep 1

# Beritahu semua program (Chrome & Python) untuk me-render antarmukanya ke Layar Hantu ini
export DISPLAY=:99
echo "✅ DISPLAY=:99 sudah di-export! Python PyAutoGUI sekarang punya Mata."

# ======================================================================
# MENYALAKAN BROWSER GOOGLE CHROME (DI BALIK LAYAR HANTU)
# ======================================================================

echo "🌐 Membuka Google Chrome dengan Profil Session yang tersimpan..."
# Kita menggunakan argument spesifik Linux agar Chrome bisa jalan walau di environment Root Docker
# --user-data-dir sangat penting: ini folder tempat Cookies ChatGPT Anda dibaca agar tidak log-out
google-chrome --no-sandbox --disable-dev-shm-usage --disable-gpu --window-size=1920,1080 --window-position=0,0 --user-data-dir="/app/chrome_profile" "https://chatgpt.com/" &

# Beri waktu 5 detik agar Chrome selesai memuat halaman ChatGPT 
echo "⏳ Menunggu Chrome rendering halaman ChatGPT selama 5 detik..."
sleep 5

# ======================================================================
# MEMBANGUNKAN SNIPER PYTHON
# ======================================================================

echo "🔫 Menjalankan Agen Sniper Python (main.py)..."
# Jalankan main.py. Dia akan nyambung ke WebSocket Server Node.js
# Pastikan alamat WS di main.py nanti terhubung ke IP Publik/Vercel Node.js Anda
python3 main.py

# ======================================================================
# CLEANUP (Hanya dieksekusi kalau main.py mati atau error)
# ======================================================================
echo "💀 Skrip Python mati atau dihentikan. Membunuh Layar Hantu Xvfb..."
kill $XVFB_PID
