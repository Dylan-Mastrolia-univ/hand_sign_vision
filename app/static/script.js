const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const btnStart = document.getElementById("btnStart");
const btnStop = document.getElementById("btnStop");
const intervalInput = document.getElementById("interval");
const intervalValue = document.getElementById("intervalValue");
const elTop1 = document.getElementById("top1");
const elTopk = document.getElementById("topk");
const elStatus = document.getElementById("status");
const videoOverlay = document.getElementById("videoOverlay");

let stream = null;
let timer = null;

intervalInput.addEventListener("input", () => {
  intervalValue.textContent = `${intervalInput.value} ms`;
});

function updateStatus(message, type = "ready") {
  const icons = {
    ready: "⚪",
    active: "🟢",
    processing: "🔵",
    error: "🔴"
  };

  elStatus.className = `status-text status-${type}`;
  elStatus.innerHTML = `
    <span class="status-icon">${icons[type] || icons.ready}</span>
    <span>${message}</span>
  `;
}

async function startCamera() {
  if (stream) return;

  try {
    updateStatus("Accès à la caméra...", "processing");
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false
    });

    video.srcObject = stream;
    btnStart.disabled = true;
    btnStop.disabled = false;
    videoOverlay.classList.add("hidden");

    updateStatus("Caméra active - Analyse en cours", "active");
    startLoop();
  } catch (e) {
    updateStatus("Erreur : Accès caméra refusé", "error");
    console.error(e);
  }
}

function stopCamera() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }

  if (stream) {
    stream.getTracks().forEach(t => t.stop());
    stream = null;
  }

  btnStart.disabled = false;
  btnStop.disabled = true;
  videoOverlay.classList.remove("hidden");

  elTop1.textContent = "En attente...";
  elTopk.innerHTML = "";
  updateStatus("Arrêté - Prêt à redémarrer", "ready");
}

function startLoop() {
  const send = async () => {
    if (!stream) return;

    const w = 224, h = 224;
    canvas.width = w;
    canvas.height = h;

    const vw = video.videoWidth || 640;
    const vh = video.videoHeight || 480;

    const size = Math.min(vw, vh);
    const sx = (vw - size) / 2;
    const sy = (vh - size) / 2;
    ctx.drawImage(video, sx, sy, size, size, 0, 0, w, h);

    const dataURL = canvas.toDataURL("image/jpeg", 0.8);

    try {
      const t0 = performance.now();
      updateStatus("Analyse en cours...", "processing");

      const resp = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataURL })
      });

      if (!resp.ok) throw new Error("Erreur serveur");

      const json = await resp.json();
      const t1 = performance.now();
      const latency = (t1 - t0).toFixed(0);

      // Update top-1 result
      elTop1.innerHTML = `
        <strong>${json.top1.class}</strong>
        <div style="font-size: 0.9rem; color: var(--text-dim); margin-top: 4px;">
          Confiance: ${(json.top1.score * 100).toFixed(1)}%
        </div>
      `;
      elTopk.innerHTML = json.topk.map((x, i) => `
        <div class="topk-item">
          <span class="topk-item-name">${i + 1}. ${x.class}</span>
          <span class="topk-item-score">${(x.score * 100).toFixed(1)}%</span>
          <div class="topk-item-bar">
            <div class="topk-item-bar-fill" style="width: ${x.score * 100}%"></div>
          </div>
        </div>
      `).join("");

      updateStatus(`✓ Analyse réussie (${latency} ms)`, "active");
    } catch (e) {
      console.error(e);
      updateStatus("Erreur lors de l'analyse", "error");
    }
  };

  const ms = Math.max(100, parseInt(intervalInput.value || "300", 10));
  if (timer) clearInterval(timer);
  timer = setInterval(send, ms);
}

btnStart.addEventListener("click", startCamera);
btnStop.addEventListener("click", stopCamera);

intervalInput.addEventListener("change", () => {
  if (timer) {
    startLoop();
  }
});

document.addEventListener("keydown", (e) => {
  if (e.code === "Space") {
    e.preventDefault();
    if (!stream) {
      startCamera();
    } else {
      stopCamera();
    }
  }
});

updateStatus("Prêt à démarrer", "ready");

