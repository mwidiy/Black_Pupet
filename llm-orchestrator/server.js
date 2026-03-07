const express = require('express');
const { v4: uuidv4 } = require('uuid');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

// === DATABASE KECIL API KEYS ===
const DB_PATH = path.join(__dirname, 'apikeys.json');

function loadApiKeys() {
  try {
    const data = fs.readFileSync(DB_PATH, 'utf-8');
    return JSON.parse(data);
  } catch (e) {
    console.error("Gagal membaca apikeys.json", e);
    return {};
  }
}

function saveApiKeys(db) {
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2), 'utf-8');
}


// === STATE MANAGEMENT ===
let jobQueue = []; // Berisi: { taskId, prompt, res, apiKey }
let isProcessing = false;
let activeJob = null; // Berisi object utuh dari job yang sedang jalan
let processTimeout = null;

const wss = new WebSocket.Server({ port: 8080 });
console.log('📡 Markas Rahasia (WebSocket Server) nyala di ws://localhost:8080');

const HTTP_PORT = 3000;

// === PUSAT KOMANDO HTTP API ===
app.post('/api/chat', (req, res) => {
  // 1. CEK OTORISASI (BEARER TOKEN)
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Unauthorized: Missing or Invalid Token format" });
  }

  const apiKey = authHeader.split(" ")[1];
  const db = loadApiKeys();

  if (!db[apiKey]) {
    return res.status(401).json({ error: "Unauthorized: Invalid API Key" });
  }

  if (db[apiKey].credit <= db[apiKey].usage) {
    return res.status(403).json({ error: "Forbidden: Kuota API Key habis!" });
  }

  let { prompt } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: "Prompt tidak boleh kosong" });
  }

  // INJECTION: Memaksa ChatGPT menjawab dengan sangat singkat agar tidak over-timeout
  const strictConstraint = "\n\n(PENTING: Jawab secara super padat dan langsung ke intinya. Tidak boleh lebih dari 50 kata.)";
  prompt = prompt + strictConstraint;

  const taskId = uuidv4();

  console.log(`\n🛎️ [API] Request masuk dari Key: ${apiKey.substring(0, 8)}***`);
  console.log(`   Task ID : ${taskId}`);
  console.log(`   Prompt  : "${prompt}"`);

  // 1. Masukkan ke Antrean
  jobQueue.push({
    taskId: taskId,
    prompt: prompt,
    apiKey: apiKey, // CATAT KEY MILIK SIAPA
    res: res // Simpan res object HTTP di memori
  });

  console.log(`   Status  : Mengantre. Sisa antrean di belakangnya: ${jobQueue.length - 1}`);

  // 2. Coba jalankan antrean
  processQueue();
});

// === SANG KONDEKTUR (Fungsi Eksekusi Antrean) ===
function processQueue() {
  // ... [Tidak berubah]
  if (isProcessing || jobQueue.length === 0) {
    return;
  }

  isProcessing = true;
  activeJob = jobQueue.shift();

  console.log(`\n🚀 [QUEUE] Memulai Eksekusi Task: ${activeJob.taskId}`);
  console.log(`   Sisa antrean menunggu: ${jobQueue.length}`);

  const perintah = {
    action: "SEND_PROMPT",
    taskId: activeJob.taskId,
    text: activeJob.prompt
  };

  console.log(`   -> Mengirim perintah ke Python via WebSocket...`);

  wss.clients.forEach(function each(client) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(perintah));
    }
  });

  processTimeout = setTimeout(() => {
    console.log(`\n❌ [TIMEOUT] Task ${activeJob.taskId} tidak ada respons dari UI selama 90 detik.`);
    activeJob.res.status(504).json({
      success: false,
      error: "Gateway Timeout: UI Automation tidak membalas."
    });
    resetStateAndProcessNext();
  }, 90000);
}

function resetStateAndProcessNext() {
  if (processTimeout) clearTimeout(processTimeout);
  isProcessing = false;
  activeJob = null;
  processQueue();
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

        if (isProcessing && activeJob) {

          // DEDUCT QUOTA (POTONG KUOTA)
          const db = loadApiKeys();
          if (db[activeJob.apiKey]) {
            db[activeJob.apiKey].usage += 1; // TAMBAH JUMLAH PEMAKAIAN
            saveApiKeys(db); // SIMPAN KE JSON
            console.log(`💰 Kuota Dipotong! Pemakaian Key ${activeJob.apiKey.substring(0, 8)}*** kini jadi ${db[activeJob.apiKey].usage} / ${db[activeJob.apiKey].credit}`);
          }

          console.log(`✅ Menyelesaikan HTTP Response untuk Task: ${activeJob.taskId}`);

          activeJob.res.json({
            success: true,
            taskId: activeJob.taskId,
            data: message.text
          });

          resetStateAndProcessNext();
        } else {
          console.log(`⚠️ Jawaban masuk tapi tidak ada Task yang sedang aktif/menunggu.`);
        }
      } else if (message.action === "AI_ERROR") {
        console.log('\n=============================================');
        console.log(`❌ [WEB SOCKET] PROTOKOL DARURAT: AI_ERROR DITERIMA!`);
        console.log(`   Task ID Laporan : ${message.taskId || "TIDAK MENYERTAKAN ID"}`);
        console.log(`   Detail Error : ${message.error || "Unknown Error"}`);
        console.log('=============================================\n');

        if (isProcessing && activeJob) {
          console.log(`❌ Langsung me-Reject Task: ${activeJob.taskId} tanpa menunggu 90 detik!`);

          activeJob.res.status(500).json({
            success: false,
            taskId: activeJob.taskId,
            error: `Agen Fisik Python Gagal: ${message.error}`
          });

          resetStateAndProcessNext();
        }
      } else {
        console.log('📩 Log Agen: %s', messageRaw);
      }
    } catch (e) {
      console.log('📩 Pesan tak terformat: %s', messageRaw);
    }
  });
});

app.listen(HTTP_PORT, '0.0.0.0', () => {
  console.log(`🌍 API Server REST nyala dan terbuka di port ${HTTP_PORT} (0.0.0.0)`);
});
