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

from dotenv import load_dotenv

async def connect_to_markas():
    load_dotenv()
    # Jika tidak ada TARGET_URL di OS/Docker, gunakan host jaringan Docker (host.docker.internal)
    # atau langsung tembak IP Publik VPS Anda sebagai fallback keras
    TARGET_URL = os.getenv("TARGET_URL", "http://202.155.143.189:3000")
    uri = TARGET_URL.replace("http://", "ws://").replace("https://", "wss://").replace(":3000", ":8080")
    
    while True:
        try:
            print(f"🚀 Agen Python SNIPER VISION mencoba menyusup ke {uri}...")
            async with websockets.connect(uri) as websocket:
                print(f"🎧 Earpiece nyala! Terhubung ke Markas ({uri})")
                
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


async def reset_layar():
    try:
        print("🔥 [PHOENIX PROTOCOL] Menjalankan Auto-Recovery. Refresh Layer (F5)...")
        # Pindahkan mouse ke tengah dulu agar kliknya fokus ke Chrome
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width / 2, screen_height / 2, duration=0.2)
        pyautogui.click() 
        await asyncio.sleep(0.5)
        
        # Tekan F5 untuk me-refresh halaman agar obrolan baru bersih dari pop-up
        pyautogui.press('f5')
        print("⏳ Menunggu 7 detik sampai halaman ChatGPT selesai di-refresh...")
        await asyncio.sleep(7.0)
        print("✅ Recovery Selesai. Siap menerima orderan dari Antrean selanjutnya!")
    except Exception as e:
        print(f"💀 FATAL: Gagal melakukan Phoenix Reset T_T : {e}")

async def eksekusi_prompt_human(websocket, teks_prompt, task_id):
    print(f"🤖 Mulai ngetik prompt untuk Task: {task_id}")
    
    try:
        # === FASE NGETIK PROMPT === #
        print("🔍 [FASE 1] Klik Koordinat Prompt Box (X:1090, Y:650)...")
        # Karena kita selalu refresh F5 di akhir, posisinya selalu bersih di tengah agak bawah.
        pyautogui.click(1090, 650)
        await asyncio.sleep(0.5)

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
        
        # === FASE PENGAMBILAN DATA (DOM DUMP V4) === #
        print("⏳ Menunggu AI generate balasan pertama (15 detik)...")
        await asyncio.sleep(15)

        print("🎯 Mengekstrak teks dari seluruh halaman (Ctrl+A / Ctrl+C)...")
        
        # Pindahkan mouse ke tempat netral dan klik untuk fokus browser
        pyautogui.click(960, 400)
        await asyncio.sleep(0.5)
        
        pyautogui.press('esc') # Hilangkan overlay/fokus dari textbox
        await asyncio.sleep(0.5)

        pyperclip.copy('') # Bersihkan clipboard
        
        pyautogui.hotkey('ctrl', 'a')
        await asyncio.sleep(0.5)
        pyautogui.hotkey('ctrl', 'c')
        await asyncio.sleep(1.0)
        
        # Deselect text
        pyautogui.click(960, 400)
        
        raw_text = pyperclip.paste()
        
        if not raw_text or teks_prompt not in raw_text:
            raise Exception("Clipboard kosong atau Prompt tidak ditemukan di layar! AI mungkin gagal merespon atau nge-lag.")

        # Ekstrak jawaban setelah kemunculan terakhir dari prompt kita
        potongan_akhir = raw_text.split(teks_prompt)[-1].strip()
        
        # Bersihkan footer-footer sampah dari anonymous chat
        for footer in [
            "Get smarter responses", 
            "Log in", 
            "Sign up for free", 
            "Voice", 
            "We use cookies", 
            "Thanks for trying ChatGPT"
        ]:
            if footer in potongan_akhir:
                potongan_akhir = potongan_akhir.split(footer)[0].strip()

        print("✅ Ekstraksi Berhasil! Jawaban AI:")
        print(f"[{potongan_akhir[:50]}...]")
        
        payload = {
            "action": "AI_RESPONSE",
            "taskId": task_id,
            "text": potongan_akhir
        }
        await websocket.send(json.dumps(payload))
        print(f"📤 Laporan rahasia untuk Task ID {task_id} terkirim!")
        
        # PHOENIX RESET: Selalu refresh F5 layar Murni kembali setiap selesai tugas
        # agar UI selalu balik ke State Awal (Prompt box di tengah)
        await reset_layar()

    except Exception as error_msg:
        print(f"❌ AGEN FISIK TERKENDALA: {error_msg}")
        
        # 1. Kirim Laporan Kegagalan ke Node.js agar antrian tidak nyangkut 90 Detik!
        laporan_gagal = {
            "action": "AI_ERROR",
            "taskId": task_id,
            "error": str(error_msg)
        }
        await websocket.send(json.dumps(laporan_gagal))
        print(f"📤 Laporan GAGAL (AI_ERROR) terkirim ke Server.")
        
        # 2. PHOENIX RESET
        await reset_layar()


if __name__ == "__main__":
    print("=== SNIPER VISION V3 (SCROLL ICON & SHIFT+ENTER) ===")
    print("Memastikan ada file: 1. copy_icon.png | 2. kolom_promp.png | 3. scroll_icon.png")
    asyncio.run(connect_to_markas())
