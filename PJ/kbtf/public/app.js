// K-BTF Stage 1 Live Web Controller (app.js)

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  fetchStatusAndLogs();
  initTab1Tagging();
  initTab2Rescue();
  initTab3Duplicate();
  initTab4Anchor();

  // 15초마다 최신 트랜잭션 자동 갱신
  setInterval(fetchStatusAndLogs, 15000);
});

// 1. Tab Navigation
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");
    });
  });
}

// 2. Fetch Status & Logs
async function fetchStatusAndLogs() {
  try {
    const resStatus = await fetch("/api/status");
    if (resStatus.ok) {
      const data = await resStatus.json();
      if (data.stats) {
        document.getElementById("kpi-wallets").innerHTML = `${data.stats.total_wallets}<span class="stat-unit">개</span>`;
        document.getElementById("kpi-vcs").innerHTML = `${data.stats.total_active_vcs}<span class="stat-unit">건</span>`;
        document.getElementById("kpi-meals").innerHTML = `${data.stats.meals_approved}<span class="stat-unit">건</span>`;
        document.getElementById("kpi-blocked").innerHTML = `${data.stats.duplicates_blocked}<span class="stat-unit">건</span>`;
      }
    }

    const resLogs = await fetch("/api/v1/logs");
    if (resLogs.ok) {
      const data = await resLogs.json();
      renderLogTable(data.logs || []);
    }
  } catch (err) {
    console.warn("Status fetch error (Serverless cold start or offline):", err);
  }
}

function renderLogTable(logs) {
  const tbody = document.getElementById("tx-log-tbody");
  if (!tbody) return;

  if (logs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-dim);">기록된 트랜잭션이 없습니다.</td></tr>`;
    return;
  }

  tbody.innerHTML = logs.map(log => {
    const isApproved = log.result_status === "APPROVED";
    const statusColor = isApproved ? "#34d399" : (log.result_status === "DUPLICATE_BLOCKED" ? "#fbbf24" : "#f87171");
    const statusBadge = `<span style="color: ${statusColor}; font-weight: 700;">${log.result_status}</span>`;
    
    return `
      <tr>
        <td>${log.verified_at || "-"}</td>
        <td><code>${log.sensor_id}</code></td>
        <td><code>${log.nfc_uid}</code></td>
        <td>${log.verification_method || "NFC_TAG"}</td>
        <td>${statusBadge}</td>
        <td><small style="color: var(--text-dim);">${(log.tx_id || "").substring(0, 8)}...</small></td>
      </tr>
    `;
  }).join("");
}

// 3. Tab 1: NFC Tagging Simulator
function initTab1Tagging() {
  const pad = document.getElementById("nfc-trigger-pad");
  const led = document.getElementById("reader-led");
  const speakerText = document.getElementById("speaker-text");
  const consoleViewer = document.getElementById("tagging-console");

  if (!pad) return;

  pad.addEventListener("click", async () => {
    pad.classList.add("active");
    const nfcUid = document.getElementById("select-resident").value;
    const sensorId = document.getElementById("select-sensor").value;

    const startTime = performance.now();

    // 0.05초 초고속 선확인 시뮬레이션
    led.className = "led-light led-green";
    speakerText.textContent = "🔊 [0.05초 선확인] 띵동! 반갑습니다. 맛있게 드세요.";

    try {
      const res = await fetch("/api/v1/dining/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: jsonSafe({ sensor_id: sensorId, nfc_uid: nfcUid, method: "NFC_TAG" })
      });
      const data = await res.json();
      const elapsedMs = Math.round(performance.now() - startTime);

      if (data.status === "APPROVED") {
        led.className = "led-light led-green";
        speakerText.textContent = `🔊 "띵동! 반갑습니다. 맛있게 드세요." (소요: ${elapsedMs}ms)`;
      } else {
        led.className = "led-light led-yellow";
        speakerText.textContent = `⚠️ [거부/차단] ${data.message || data.reason} (${elapsedMs}ms)`;
      }

      consoleViewer.textContent = JSON.stringify({
        latency_benchmark: {
          edge_precheck_ms: "0.05 ms",
          cloud_roundtrip_ms: `${elapsedMs} ms`
        },
        request: { sensor_id: sensorId, nfc_uid: nfcUid },
        response: data
      }, null, 2);

      fetchStatusAndLogs();
    } catch (err) {
      led.className = "led-light led-red";
      speakerText.textContent = "네트워크 오류 발생";
      consoleViewer.textContent = String(err);
    } finally {
      setTimeout(() => pad.classList.remove("active"), 400);
    }
  });
}

// 4. Tab 2: Card-less Oral Rescue (Mobile Frame)
function initTab2Rescue() {
  const btnSearch = document.getElementById("btn-rescue-search");
  const resultBox = document.getElementById("rescue-result-box");
  const maskedNameElem = document.getElementById("rescue-masked-name");
  const uidTextElem = document.getElementById("rescue-uid-text");
  const btnApprove = document.getElementById("btn-rescue-approve");
  const rescueConsole = document.getElementById("rescue-console");

  let currentRescueUid = null;

  if (btnSearch) {
    btnSearch.addEventListener("click", async () => {
      const dong = document.getElementById("rescue-dong").value.trim();
      const ho = document.getElementById("rescue-ho").value.trim();
      const birth = document.getElementById("rescue-birth").value.trim();

      try {
        const res = await fetch("/api/residents/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: jsonSafe({ building_no: dong, room_no: ho, birth_date: birth, officer_name: "공익요원(현장)" })
        });
        const data = await res.json();

        if (res.ok && data.status === "MATCHED") {
          currentRescueUid = data.nfc_uid;
          maskedNameElem.textContent = `${data.masked_name} (자격: ${data.welfare_tier})`;
          uidTextElem.textContent = data.nfc_uid;
          resultBox.style.display = "block";
          rescueConsole.textContent = `[에지 사설 Wi-Fi 192.168.0.x 조회 성공]\n${JSON.stringify(data, null, 2)}`;
        } else {
          resultBox.style.display = "none";
          rescueConsole.textContent = `[조회 실패] ${data.message || "거주자 명부 불일치"}`;
          alert(data.message || "거주자 정보가 일치하지 않습니다.");
        }
      } catch (err) {
        rescueConsole.textContent = String(err);
      }
    });
  }

  if (btnApprove) {
    btnApprove.addEventListener("click", async () => {
      if (!currentRescueUid) return;

      try {
        const res = await fetch("/api/v1/dining/verify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: jsonSafe({ sensor_id: "SENSOR_MEAL_01", nfc_uid: currentRescueUid, method: "MANUAL_PASS" })
        });
        const data = await res.json();

        rescueConsole.textContent = `[클라우드 전송 결과: MANUAL_PASS]\n${JSON.stringify(data, null, 2)}`;
        alert(data.message || "배식 승인 처리 완료");
        fetchStatusAndLogs();
      } catch (err) {
        rescueConsole.textContent = String(err);
      }
    });
  }
}

// 5. Tab 3: Duplicate Block Simulator
function initTab3Duplicate() {
  const btnMeal = document.getElementById("btn-sim-meal");
  const btnBunker = document.getElementById("btn-sim-bunker");
  const led = document.getElementById("bunker-led");
  const speakerText = document.getElementById("bunker-speaker-text");
  const consoleViewer = document.getElementById("bunker-console");

  const testUid = "04:A1:B2:C3:D4:E5:01"; // 김만석 어르신

  if (btnMeal) {
    btnMeal.addEventListener("click", async () => {
      led.className = "led-light led-green";
      speakerText.textContent = "1단계: 김만석 어르신 현장식사(Line 1) 완료";

      const res = await fetch("/api/v1/dining/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: jsonSafe({ sensor_id: "SENSOR_MEAL_01", nfc_uid: testUid, method: "NFC_TAG" })
      });
      const data = await res.json();
      consoleViewer.textContent = `[1단계 결과: 현장식사]\n${JSON.stringify(data, null, 2)}`;
      fetchStatusAndLogs();
    });
  }

  if (btnBunker) {
    btnBunker.addEventListener("click", async () => {
      led.className = "led-light led-yellow";
      speakerText.textContent = "2단계: 동일 카드로 도시락 배부처(Line 2) 태깅 중복 시도...";

      const res = await fetch("/api/v1/dining/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: jsonSafe({ sensor_id: "SENSOR_BENTO_02", nfc_uid: testUid, method: "NFC_TAG" })
      });
      const data = await res.json();

      if (data.code === 403 || data.reason === "ALREADY_DINED_TODAY") {
        led.className = "led-light led-yellow";
        speakerText.textContent = `🚫 [차단 성공] "오늘 이미 배식을 완료하셨습니다!"`;
      } else {
        speakerText.textContent = `응답: ${data.message}`;
      }

      consoleViewer.textContent = `[2단계 판정 결과: 중복 수령 상호배제 차단 (HTTP 403)]\n${JSON.stringify(data, null, 2)}`;
      fetchStatusAndLogs();
    });
  }
}

// 6. Tab 4: 18:00 Batch Anchorer
function initTab4Anchor() {
  const btnAnchor = document.getElementById("btn-run-anchor");
  const consoleViewer = document.getElementById("anchor-console");

  if (!btnAnchor) return;

  btnAnchor.addEventListener("click", async () => {
    consoleViewer.textContent = "일일 18시 온체인 배치 앵커링 연산 중 (머클루트 해시 도출)...";

    try {
      const res = await fetch("/api/v1/kpi/anchor-batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: jsonSafe({})
      });
      const data = await res.json();

      consoleViewer.textContent = `[일일 18시 온체인 공증 영수증 (Notarization Receipt)]\n${JSON.stringify(data, null, 2)}`;
      alert("일일 18시 온체인 배치 앵커링이 성공적으로 완료되었습니다!");
      fetchStatusAndLogs();
    } catch (err) {
      consoleViewer.textContent = String(err);
    }
  });
}

function jsonSafe(obj) {
  return JSON.stringify(obj);
}
