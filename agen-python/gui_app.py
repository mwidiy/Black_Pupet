import tkinter as tk
from tkinter import scrolledtext
import threading
import requests
import os
from dotenv import load_dotenv

# Load configurasi dari .env
load_dotenv()

# Setup URL target dan token dari env
TARGET_URL = os.getenv("TARGET_URL", "http://localhost:3000")
API_KEY = os.getenv("API_KEY", "KUNCI_PREMIUM_999")

API_URL = f"{TARGET_URL}/api/chat"

def main():
    # Setup Window Utama
    root = tk.Tk()
    root.title("Sniper OS-Level - Panel Kontrol")
    root.geometry("600x550")
    root.configure(bg="#2d2d2d")
    root.resizable(False, False)

    # Label Judul
    title_label = tk.Label(root, text="Agen Mata-Mata ChatGPT", font=("Helvetica", 16, "bold"), bg="#2d2d2d", fg="#4CAF50")
    title_label.pack(pady=15)

    # Frame Input Prompt
    input_frame = tk.Frame(root, bg="#2d2d2d")
    input_frame.pack(fill=tk.X, padx=20, pady=5)

    prompt_label = tk.Label(input_frame, text="Tuliskan Prompt (Pertanyaan) di bawah ini:", font=("Helvetica", 10), bg="#2d2d2d", fg="#ffffff")
    prompt_label.pack(anchor=tk.W)

    prompt_entry = tk.Text(input_frame, height=5, font=("Helvetica", 10), bg="#1e1e1e", fg="#ffffff", insertbackground="white")
    prompt_entry.pack(fill=tk.X, pady=5)

    # Frame Tombol & Status
    action_frame = tk.Frame(root, bg="#2d2d2d")
    action_frame.pack(fill=tk.X, padx=20, pady=10)

    # Label Status
    status_label = tk.Label(action_frame, text="Status: Standby. Menunggu perintah...", font=("Helvetica", 10, "italic"), bg="#2d2d2d", fg="#aaaaaa")
    status_label.pack(side=tk.LEFT)

    # Tombol Eksekusi
    def send_prompt():
        teks_prompt = prompt_entry.get("1.0", tk.END).strip()
        if not teks_prompt:
            status_label.config(text="Status: ❌ Error. Prompt tidak boleh kosong!", fg="#ff5555")
            return

        # MINIMIZE WINDOW (SEMBUNYIKAN GUI DARI LAYAR AI)
        root.iconify()

        # Disable tombol dan ubah status agar user tau lagi mikir
        btn_send.config(state=tk.DISABLED, text="⏳ SEDANG MEMPROSES...", bg="#555555")
        status_label.config(text="Status: 🚀 Mengirim ke Server Node...", fg="#ffaa00")
        answer_box.delete("1.0", tk.END)
        answer_box.insert(tk.END, "Menunggu agen fisik mengetik dan mencuri data...\n(JANGAN SENTUH MOUSE DULU!)")

        # Jalankan HTTP Request di Thread berbeda agar GUI tidak Not-Responding
        threading.Thread(target=process_api_call, args=(teks_prompt,), daemon=True).start()

    def process_api_call(prompt_text):
        try:
            payload = {"prompt": prompt_text}
            
            # INJECTION: Menambahkan Token Rahasia Klien sebagai Autentikasi API
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Timeout dinaikin jadi 100 detik karena proses fisik UI lumayan lama (15s nunggu AI mikir)
            response = requests.post(API_URL, json=payload, headers=headers, timeout=100)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    jawaban = data.get("data", "")
                    
                    # Update GUI dari dalam Thread harus hati-hati, amannya pakai root.after
                    root.after(0, update_success_ui, jawaban)
                else:
                    root.after(0, update_error_ui, f"Server menolak: {data}")
            else:
                root.after(0, update_error_ui, f"Error HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            root.after(0, update_error_ui, "❌ TIMEOUT! Agen gagal nyolong data dalam 100 detik.")
        except requests.exceptions.ConnectionError:
            root.after(0, update_error_ui, "❌ NODE SERVER MATI! Jalankan 'node server.js' dulu.")
        except Exception as e:
            root.after(0, update_error_ui, f"❌ Terjadi kesalahan misterius: {e}")

    def update_success_ui(jawaban):
        # MUNCULKAN KEMBALI WINDOW YANG TERSEMBUNYI
        root.deiconify()
        root.lift()
        root.attributes('-topmost',True)
        root.after_idle(root.attributes,'-topmost',False)

        status_label.config(text="Status: ✅ Misi Selesai! Balasan diterima.", fg="#4CAF50")
        answer_box.delete("1.0", tk.END)
        answer_box.insert(tk.END, jawaban)
        btn_send.config(state=tk.NORMAL, text="🚀 ENVOY / KIRIM PROMPT", bg="#4CAF50")

    def update_error_ui(pesan_error):
        # MUNCULKAN JUGA KALAU ERROR
        root.deiconify()
        root.lift()

        status_label.config(text="Status: ❌ Misi Gagal.", fg="#ff5555")
        answer_box.delete("1.0", tk.END)
        answer_box.insert(tk.END, pesan_error)
        btn_send.config(state=tk.NORMAL, text="💥 COBA LAGI TIGER", bg="#ff5555")


    btn_send = tk.Button(action_frame, text="🚀 ENVOY / KIRIM PROMPT", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049", cursor="hand2", command=send_prompt)
    btn_send.pack(side=tk.RIGHT, padx=5)


    # Frame Output (Kotak Jawaban)
    output_frame = tk.Frame(root, bg="#2d2d2d")
    output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    answer_label = tk.Label(output_frame, text="Balasan Rahasia dari AI:", font=("Helvetica", 10), bg="#2d2d2d", fg="#ffffff")
    answer_label.pack(anchor=tk.W)

    answer_box = scrolledtext.ScrolledText(output_frame, font=("Helvetica", 10), bg="#1e1e1e", fg="#00ff00", insertbackground="white")
    answer_box.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Pesan intro ringan
    answer_box.insert(tk.END, "Halo Komandan. Masukkan prompt di atas untuk memulai operasi 'Sniper OS-Level'...")

    # Jalankan Loop GUI Utama
    root.mainloop()

if __name__ == "__main__":
    main()
