import asyncio
import websockets
import json
import pyautogui
import pyperclip
import time
import random
import os

# Konfigurasi PyAutoGUI
pyautogui.PAUSE = 0.05

async def connect_to_markas():
    uri = "ws://localhost:8080"
    
    while True:
        try:
            print("🚀 Agen Python SNIPER VISION mencoba menyusup...")
            async with websockets.connect(uri) as websocket:
                print("🎧 Earpiece nyala! Terhubung ke Markas (ws://localhost:8080)")
                
                while True:
                    pesan_raw = await websocket.recv()
                    pesan = json.loads(pesan_raw)
                    print(f"📥 Menerima perintah: {pesan}")
                    
                    if pesan.get("action") == "SEND_PROMPT":
                        task_id = pesan.get("taskId", "NO_ID")
                        await eksekusi_prompt_human(websocket, pesan.get("text", ""), task_id)
                        
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Koneksi terputus dari Markas. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except ConnectionRefusedError:
            print("🔌 Markas (Server Node.js) belum nyala. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Error: {e}")
            await asyncio.sleep(5)


async def eksekusi_prompt_human(websocket, teks_prompt, task_id):
    print(f"🤖 Mulai ngetik prompt untuk Task: {task_id}")
    
    # === FASE AUTO-LOCATE KOLOM PROMPT === #
    print("🔍 [FASE 1] Mencari posisi Kolom Prompt di layar...")
    prompt_img = "kolom_promp.png"
    if not os.path.exists(prompt_img):
        print(f"❌ ERROR: Gambar '{prompt_img}' tidak ditemukan! Eksekusi batal.")
        return

    try:
        # Cari kotak input di layar
        batas_waktu_cari = 5 # detik
        start_time = time.time()
        lokasi_ditemukan = None

        while time.time() - start_time < batas_waktu_cari:
            try:
                # confidence 0.8 butuh opencv-python yang sudah kita install
                lokasi_ditemukan = pyautogui.locateOnScreen(prompt_img, confidence=0.8)
                if lokasi_ditemukan:
                    break
            except pyautogui.ImageNotFoundException:
                pass
            await asyncio.sleep(0.5)

        if lokasi_ditemukan:
            # Pindah dan Klik ke tengah box input
            cx = lokasi_ditemukan.left + (lokasi_ditemukan.width / 2)
            cy = lokasi_ditemukan.top + (lokasi_ditemukan.height / 2)
            print(f"🎯 Kolom Prompt ditemukan di Koordinat (X:{int(cx)}, Y:{int(cy)}). Mengunci target...")
            
            pyautogui.moveTo(cx, cy, duration=0.5)
            await asyncio.sleep(0.2)
            pyautogui.click()
            await asyncio.sleep(0.5)
        else:
            print(f"❌ Gagal menemukan '{prompt_img}' di layar. Pastikan browser ChatGPT terbuka jelas!")
            return

    except Exception as e:
        print(f"❌ Terjadi error saat mencari Kolom Prompt: {e}")
        return

    # === FASE NGETIK === #
    print("✍️ Mulai Mengetik...")
    for char in teks_prompt:
        if char == '\n':
            pyautogui.keyDown('shift')
            pyautogui.press('enter')
            pyautogui.keyUp('shift')
        else:
            pyautogui.write(char)
        delay = random.uniform(0.01, 0.05)
        await asyncio.sleep(delay)
        
    print("✅ Selesai mengetik. Jeda baca ulang bentar...")
    await asyncio.sleep(random.uniform(0.5, 1.0))
    
    print("⌨️ Neken tombol Enter! Menunggu ChatGPT berpikir...")
    pyautogui.press('enter')
    
    # === FASE PENGAMBILAN DATA (SNIPER VISION V3) === #
    print("⏳ Menunggu AI generate balasan pertama (15 detik)...")
    await asyncio.sleep(15)

    # Cek Ikon Scroll Down Terlebih Dahulu
    print("⏬ [FASE 1.5] Mengecek apakah ada tombol Scroll Down...")
    scroll_icon_path = "scroll_icon.png"
    if os.path.exists(scroll_icon_path):
        try:
            scroll_target = pyautogui.locateOnScreen(scroll_icon_path, confidence=0.85)
            if scroll_target:
                print("⏬ Tombol Scroll Down ditemukan! Mengklik agar mentok ke jawaban terbaru...")
                cx = scroll_target.left + (scroll_target.width / 2)
                cy = scroll_target.top + (scroll_target.height / 2)
                pyautogui.moveTo(cx, cy, duration=0.3)
                pyautogui.click()
                await asyncio.sleep(1.5) # Kasih waktu web ChatGPT buat loncat ke bawah
        except pyautogui.ImageNotFoundException:
            print("⏬ Tidak ada tombol Scroll Down (Jawaban mungkin pendek/sudah mentok bawah). Lanjut...")
    else:
        print("⚠️ Warning: Gambar 'scroll_icon.png' tidak ada di folder agen. Melompati step ini.")

    print("🎯 [FASE 2] Mencari tombol Copy...")
    image_path = "copy_icon.png" 
    
    if not os.path.exists(image_path):
        print(f"❌ ERROR: Gambar '{image_path}' tidak ada!")
        return

    pyperclip.copy('') # Bersihkan clipboard
    
    try:
        semua_target = []
        try:
            semua_target = list(pyautogui.locateAllOnScreen(image_path, confidence=0.85))
        except pyautogui.ImageNotFoundException:
            semua_target = []

        if len(semua_target) > 0:
            print(f"📡 Radar menangkap {len(semua_target)} Ikon Copy!")
            semua_target_sorted = sorted(semua_target, key=lambda box: box.top)
            target_terbawah = semua_target_sorted[-1]
            
            print(f"🎯 Mengunci target tombol Paling Bawah...")
            
            center_x = target_terbawah.left + (target_terbawah.width / 2)
            center_y = target_terbawah.top + (target_terbawah.height / 2)
            
            pyautogui.moveTo(center_x, center_y, duration=0.5)
            await asyncio.sleep(0.2)
            
            pyautogui.click()
            print("🔫 Target Copy Headshot berhasil dieksekusi!")
            
            await asyncio.sleep(1) # Tunggu clipboard ngisi
            
            raw_text = pyperclip.paste()
            
            if raw_text:
                payload = {
                    "action": "AI_RESPONSE",
                    "taskId": task_id,
                    "text": raw_text
                }
                await websocket.send(json.dumps(payload))
                print(f"📤 Laporan rahasia untuk Task ID {task_id} terkirim!")
            else:
                print("❌ Clipboard kosong. Gagal Copy.")
        else:
            print("❌ GAGAL TOTAL. Tidak menemukan satupun blok Copy di layar.")
            
    except Exception as e:
        print(f"❌ Terjadi error saat operasi Auto-Scroll Sniper: {e}")


if __name__ == "__main__":
    print("=== SNIPER VISION V3 (SCROLL ICON & SHIFT+ENTER) ===")
    print("Memastikan ada file: 1. copy_icon.png | 2. kolom_promp.png | 3. scroll_icon.png")
    asyncio.run(connect_to_markas())
