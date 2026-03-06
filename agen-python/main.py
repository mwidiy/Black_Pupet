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
    await asyncio.sleep(1)
    
    # 1. Ngetik
    for char in teks_prompt:
        pyautogui.write(char)
        delay = random.uniform(0.01, 0.05)
        await asyncio.sleep(delay)
        
    print("✅ Selesai mengetik. Jeda baca ulang bentar...")
    await asyncio.sleep(random.uniform(0.5, 1.0))
    
    print("⌨️ Neken tombol Enter! Menunggu ChatGPT berpikir...")
    pyautogui.press('enter')
    
    # === FASE PENCURIAN DATA (SNIPER VISION) === #
    print("⏳ Menunggu AI generate balasan (15 detik)...")
    await asyncio.sleep(15)

    print("🎯 Mengaktifkan SNIPER VISION untuk mengunci tombol Copy terbawah...")
    image_path = "copy_icon.png" 
    
    if not os.path.exists(image_path):
        print(f"❌ ERROR: Gambar '{image_path}' tidak ditemukan di folder ini!")
        return

    # Bersihin clipboard sebelumnya
    pyperclip.copy('')
    
    try:
        # locateAllOnScreen mengembalikan generator iterasi, kita ubah jadi list biar bisa disorting
        print("🌍 Melakukan sweeping seluruh monitor...")
        semua_target = list(pyautogui.locateAllOnScreen(image_path, confidence=0.85))
        
        if len(semua_target) > 0:
            print(f"📡 Radar mendeteksi {len(semua_target)} tombol Copy di layar!")
            
            # Kita urutkan berdasarkan kordinat Y (dari atas ke bawah)
            semua_target_sorted = sorted(semua_target, key=lambda box: box.top)
            target_terbawah = semua_target_sorted[-1]
            
            print(f"🎯 Mengunci target TERBAWAH pada Y: {target_terbawah.top}")
            
            center_x = target_terbawah.left + (target_terbawah.width / 2)
            center_y = target_terbawah.top + (target_terbawah.height / 2)
            
            pyautogui.moveTo(center_x, center_y, duration=0.5)
            await asyncio.sleep(0.2)
            
            pyautogui.click()
            print("🔫 Target Copy Headshot berhasil dieksekusi!")
            
            await asyncio.sleep(1)
            
            raw_text = pyperclip.paste()
            
            if raw_text:
                payload = {
                    "action": "AI_RESPONSE",
                    "taskId": task_id,
                    "text": raw_text
                }
                await websocket.send(json.dumps(payload))
                print(f"📤 Laporan rahasia untuk Task ID {task_id} berhasil dikirim ke Markas!")
            else:
                print("❌ Clipboard kosong... Copy gagal.")
        else:
            print("❌ Gagal menemukan satupun tombol Copy di layar.")
            
    except pyautogui.ImageNotFoundException:
         print("❌ Gambar tidak ditemukan di layar.")
    except Exception as e:
        print(f"❌ Terjadi error saat operasi Sniper: {e}")

if __name__ == "__main__":
    print("=== OS-LEVEL SNIPER VISION PROTOCOL ===")
    print("1. Pastikan file 'copy_icon.png' (ukuran kecil) udah lu sediakan.")
    print("2. Pas jalanin, kursor wajib kedap-kedip di dalam text box ChatGPT.")
    print("3. JANGAN GERAKIN LAYAR/MOUSE saat dia ngeluarin Radar di detik 15!")
    asyncio.run(connect_to_markas())
