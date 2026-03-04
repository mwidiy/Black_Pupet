console.log("🕵️‍♂️ Agen Parasit V3 (The Eyes) ngumpet di pojokan!");

const socket = new WebSocket('ws://localhost:8080');

socket.onopen = function (e) {
    console.log("✅ Mata-mata nyala! Terhubung ke Markas.");
};

socket.onclose = function (event) {
    console.log("❌ Koneksi terputus dari Markas.");
};

// Variabel state untuk oberserver
let isGenerating = false;
let lastMessageCount = 0;

// Fungsi untuk mengekstrak teks balasan AI
function extractLatestAIResponse() {
    // Di ChatGPT, balasan AI biasanya ada di dalam div dengan struktur tertentu.
    // Kita cari semua message block (biasanya punya class 'markdown' atau atribut khusus)
    const messageBlocks = document.querySelectorAll('.markdown');

    if (messageBlocks.length > 0) {
        // Ambil elemen terakhir (pesan AI paling baru)
        const latestBlock = messageBlocks[messageBlocks.length - 1];

        // Ekstrak teks utuhnya
        const responseText = latestBlock.innerText || latestBlock.textContent;

        if (responseText && responseText.trim().length > 0) {
            console.log("📤 Mengirim Laporan (Balasan AI) ke Markas...");
            socket.send(JSON.stringify({
                action: "AI_RESPONSE",
                text: responseText
            }));
            return true;
        }
    }
    return false;
}

// 1. Setup MutationObserver untuk memantau perubahan DOM
const observer = new MutationObserver((mutations) => {
    // Cara gampang deteksi apakah AI lagi ngetik atau udah selesai:
    // Cek keberadaan tombol "Stop generating"
    // Di versi ChatGPT sekarang, biasanya tag <button> dengan aria-label="Stop generating"
    // Atau tombol icon kotak (stop).
    const stopButton = document.querySelector('button[aria-label="Stop generating"]') ||
        document.querySelector('button[data-testid="stop-button"]');

    // Selain itu kita juga bisa mantau jumlah balasan
    const currentMessageBlocks = document.querySelectorAll('.markdown');

    // Jika ada tombol stop -> artinya lagi nge-generate (ngetik)
    if (stopButton) {
        if (!isGenerating) {
            console.log("👀 AI lagi ngetik jawaban...");
            isGenerating = True;
        }
    }
    // Jika awalnya lagi ngetik, terus sekarang tombol stop ILANG -> artinya selesai
    else if (isGenerating && !stopButton) {
        // Kasih jeda dikit biar rendering DOM sempet finish
        setTimeout(() => {
            console.log("✅ AI Selesai ngetik! Nyuri data balasan...");
            extractLatestAIResponse();
            isGenerating = false;
            lastMessageCount = currentMessageBlocks.length;
        }, 500);
    }
});

// 2. Mulai mangintai body dokumen atau container chat utama
const config = { childList: true, subtree: true, attributes: false };
observer.observe(document.body, config);

console.log("🎯 Radar DOM MutationObserver telah diaktifkan.");
