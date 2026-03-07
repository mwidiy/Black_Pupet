# Menggunakan base image Python yang ringan
# Menggunakan base image Ubuntu 22.04 lengkap
FROM ubuntu:22.04

# Hindari interaksi saat apt-get install
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3 dan PIP terlebih dahulu
RUN apt-get update && apt-get install -y python3 python3-pip python-is-python3


# Mencegah Python membuat file .pyc dan memastikannya jalan secara unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Menetapkan zona waktu agar log bot sinkron dengan kita
ENV TZ="Asia/Jakarta"

# Bypass Strict X11 Authentication untuk PyAutoGUI
ENV XAUTHORITY=/tmp/.Xauthority

# Update OS Linux dan install dependencies krusial untuk Xvfb, Chrome, OpenCV, dan PyAutoGUI
RUN apt-get update && apt-get install -y \
    xvfb \
    x11-utils \
    gnupg \
    wget \
    curl \
    unzip \
    xxd \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    scrot \
    gnome-screenshot \
    python3-tk \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome Stable secara spesifik untuk Linux
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Buat folder kerja di dalam Linux Container
WORKDIR /app

# Salin file requirements.txt dan install paket Python kita (websockets, pyautogui, opencv, dll)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua isi folder agen-python (termasuk .png dan main.py) ke dalam container
COPY . .

# Buat folder sementara untuk menyimpan riwayat login ChatGPT (Session Profil Chrome)
# Nanti kita akan me-mount folder Windows kita ke mari, agar Linux tidak meminta "Login Manual"
VOLUME ["/app/chrome_profile"]

# Beri hak akses eksekusi pada script pembangkit Layar Hantu
RUN chmod +x /app/start.sh

# Jalankan skrip pamungkas
CMD ["/app/start.sh"]
