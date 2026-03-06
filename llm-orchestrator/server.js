const express = require('express');
const { v4: uuidv4 } = require('uuid');
const WebSocket = require('ws');

const app = express();
app.use(express.json());

// === STATE MANAGEMENT ===
let jobQueue = []; // Berisi: { taskId, prompt, res }
let isProcessing = false;
let activeJob = null; // Berisi object utuh dari job yang sedang jalan { taskId, prompt, res }
let processTimeout = null;

const wss = new WebSocket.Server({ port: 8080 });
console.log('📡 Markas Rahasia (WebSocket Server) nyala di ws://localhost:8080');

const HTTP_PORT = 3000;

// === PUSAT KOMANDO HTTP API ===
app.post('/api/chat', (req, res) => {
  const { prompt } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: "Prompt tidak boleh kosong" });
  }

  const taskId = uuidv4();

  console.log(`\n🛎️ [API] Request masuk.`);
  console.log(`   Task ID : ${taskId}`);
  console.log(`   Prompt  : "${prompt}"`);

  // 1. Masukkan ke Antrean
  jobQueue.push({
    taskId: taskId,
    prompt: prompt,
    res: res // Simpan res object HTTP di memori
  });

  console.log(`   Status  : Mengantre. Sisa antrean di belakangnya: ${jobQueue.length - 1}`);

  // 2. Coba jalankan antrean
  processQueue();
});

// === SANG KONDEKTUR (Fungsi Eksekusi Antrean) ===
function processQueue() {
  // Jika masih ada yang diproses, atau antrean kosong, abaikan
  if (isProcessing || jobQueue.length === 0) {
    return;
  }

  // Ambil job pertama dari antrean
  isProcessing = true;
  activeJob = jobQueue.shift();

  console.log(`\n🚀 [QUEUE] Memulai Eksekusi Task: ${activeJob.taskId}`);
  console.log(`   Sisa antrean menunggu: ${jobQueue.length}`);

  const perintah = {
    action: "SEND_PROMPT",
    taskId: activeJob.taskId, // Sisipkan taskId agar Extension tahu
    text: activeJob.prompt
  };

  console.log(`   -> Mengirim perintah ke Python via WebSocket...`);

  // Broadcast perintah
  wss.clients.forEach(function each(client) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(perintah));
    }
  });

  // Pasang Timeout 90 detik
  processTimeout = setTimeout(() => {
    console.log(`\n❌ [TIMEOUT] Task ${activeJob.taskId} tidak ada respons dari UI selama 90 detik.`);

    // Balas HTTP Client dengan Error
    activeJob.res.status(504).json({
      success: false,
      error: "Gateway Timeout: UI Automation tidak membalas."
    });

    // Lanjut job selanjutnya
    resetStateAndProcessNext();
  }, 90000);
}

function resetStateAndProcessNext() {
  if (processTimeout) clearTimeout(processTimeout);
  isProcessing = false;
  activeJob = null;
  processQueue(); // Panggil paksa job selanjutnya jika ada
}

// === PUSAT KOMUNIKASI WEBSOCKET ===
wss.on('connection', function connection(ws) {
  console.log('✅ Klien (Python/Chrome Ext) berhasil terhubung ke Markas!');

  ws.on('message', function incoming(messageRaw) {
    try {
      const message = JSON.parse(messageRaw);

      if (message.action === "AI_RESPONSE") {
        console.log('\n=============================================');
        console.log(`📩 [WEB SOCKET] LAPORAN JAWABAN MASUK`);
        console.log(`   Task ID Laporan : ${message.taskId || "TIDAK MENYERTAKAN ID"}`);
        console.log('=============================================');
        console.log(message.text);
        console.log('=============================================\n');

        // Jika sedang ada job yang diproses
        if (isProcessing && activeJob) {
          // Idealnya kita mencocokkan message.taskId dengan activeJob.taskId
          // Namun karena belum tentu Extension Anda sudah mengirim taskId,
          // Kita asumsikan jawaban yang datang PERTAMA adalah milik activeJob.

          console.log(`✅ Menyelesaikan HTTP Response untuk Task: ${activeJob.taskId}`);

          // Balas HTTP peminta awal
          activeJob.res.json({
            success: true,
            taskId: activeJob.taskId,
            data: message.text
          });

          // Bersihkan state & Lanjut antrean berikutnya
          resetStateAndProcessNext();
        } else {
          console.log(`⚠️ Jawaban masuk tapi tidak ada Task yang sedang aktif/menunggu.`);
        }
      } else {
        console.log('📩 Log Agen: %s', messageRaw);
      }
    } catch (e) {
      console.log('📩 Pesan tak terformat: %s', messageRaw);
    }
  });
});

app.listen(HTTP_PORT, () => {
  console.log(`🌍 API Server REST nyala di http://localhost:${HTTP_PORT}`);
});
