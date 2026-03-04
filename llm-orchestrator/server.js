const WebSocket = require('ws');

// Buka port 8080 untuk jalur WebSocket
const wss = new WebSocket.Server({ port: 8080 });

console.log('📡 Markas Rahasia (WebSocket Server) nyala di ws://localhost:8080');

wss.on('connection', function connection(ws) {
  console.log('✅ Agen berhasil terhubung ke Markas!');

  // Kalau ada pesan masuk dari Agen (misal: jawaban dari web AI)
  ws.on('message', function incoming(messageRaw) {
    try {
      const message = JSON.parse(messageRaw);

      if (message.action === "AI_RESPONSE") {
        console.log('\n=============================================');
        console.log('📩 LAPORAN FINAL MASUK DARI AGEN MATA-MATA:');
        console.log('=============================================');
        console.log(message.text);
        console.log('=============================================\n');
      } else {
        console.log('📩 Laporan masuk dari Agen: %s', messageRaw);
      }
    } catch (e) {
      console.log('📩 Laporan mentah: %s', messageRaw);
    }
  });

  // Simulasi: 5 detik setelah Agen (Python) nyambung, Markas ngasih perintah (Prompt)
  // Catatan: Ini akan nembak ke SEMUA klien yang connect (Chrome & Python)
  // Python bakal nge-eksekusi fisiknya, Chrome bakal ngabaikan (karena V3 udah ga dengerin SEND_PROMPT)
  setTimeout(() => {
    const perintah = {
      action: "SEND_PROMPT",
      text: "Jelaskan konsep adaptasi manusia dalam 3 kalimat."
    };
    console.log('📤 Markas men-dispatch perintah eksekusi OS-Level...');
    ws.send(JSON.stringify(perintah));
  }, 5000);
});
