/* ==========================================================================
   우리단지 ON (Our Village ON) - Core Logic & K-BTF Simulation Engine
   ========================================================================== */

// --- Global State ---
const State = {
  currentUser: 'user1', // 'user1' (Kim Young-soo), 'user2' (Park Jung-ja), 'admin'
  fontSize: 'normal',   // 'normal', 'large', 'xlarge'
  highContrast: false,
  ttsEnabled: true,
  credits: 35.5, // 햇살머니 (SM) & 시간크레딧 (TC)
  vitalScore: 'safe',   // 'safe', 'warning', 'danger'
  lastVitalTime: '오늘 11:42 (경로식당 태깅)',
  mealReceived: true,
  dailyMealCount: 142,
  pwaDeferredPrompt: null,
  activeTab: 'tab-resident-id',
  trackMode: 'smartphone', // 'smartphone', 'physical-nfc'
  
  // Top 3 User Selected Core Features (Default: DID, Anabada, Advisor)
  top3Features: ['did', 'anabada', 'advisor'],

  // Anabada Market State
  activeMarketFilter: 'all',
  selectedMarketItemId: null,
  marketItems: [
    {
      id: 'mkt-01',
      type: 'used',
      title: '쿠쿠 6인용 전기압력밥솥 (IH 작동 양호)',
      price: 12.0,
      icon: '🍲',
      seller: '102동 해피할머니',
      desc: '내솥 코팅 상태 양호하며 밥맛 좋습니다. 102동 1층 로비에서 직접 전달해 드립니다.',
      date: '10분 전'
    },
    {
      id: 'mkt-02',
      type: 'used',
      title: '겨울 롱패딩 100호 (오리털 드라이 완료)',
      price: 8.5,
      icon: '🧥',
      seller: '104동 산남장인',
      desc: '세탁소 드라이클리닝 완료하여 바로 입으실 수 있습니다. 깨끗합니다.',
      date: '30분 전'
    },
    {
      id: 'mkt-03',
      type: 'free',
      title: '공기정화 산세베리아 화분 (분갈이 완료)',
      price: 0,
      icon: '🪴',
      seller: '101동 꽃바람',
      desc: '화분 정리차 이웃 어르신께 무료 나눔합니다. 따뜻하게 키워주세요!',
      date: '1시간 전'
    },
    {
      id: 'mkt-04',
      type: 'free',
      title: '스테인리스 냄비 2종 세트 (미사용)',
      price: 0,
      icon: '🥘',
      seller: '103동 나눔이',
      desc: '선물로 받은 미사용 새 제품입니다. 필요하신 세대 가져가세요.',
      date: '2시간 전'
    },
    {
      id: 'mkt-05',
      type: 'group',
      title: '2026 햅쌀 10kg 산지직송 (5세대 모집)',
      price: 15.0,
      icon: '🌾',
      seller: '단지 상생 번영회',
      desc: '생산지 직거래 공동구매로 배송비 무료 및 최저가 혜택! (현재 3/5세대 참여)',
      participants: 3,
      maxParticipants: 5,
      date: '진행 중'
    },
    {
      id: 'mkt-06',
      type: 'group',
      title: '친환경 3겹 롤화장지 30롤 (4세대 모집)',
      price: 6.0,
      icon: '🧻',
      seller: '단지 복지나눔회',
      desc: '도매가 일괄구매로 세대당 6.0 햇살머니에 나눕니다. (현재 2/4세대 참여)',
      participants: 2,
      maxParticipants: 4,
      date: '진행 중'
    }
  ],

  // Senior Career Advisor State
  activeAdvisorDomain: 'all',
  advisorKeyword: '',
  selectedAdvisorUuid: null,
  advisors: [
    {
      uuid: 'uuid:adv-2026-f8a1',
      name: '김*진',
      nickname: '새벽공기',
      domain: 'it',
      domainLabel: '💻 IT · SW 아키텍처',
      years: 32,
      rate: 3.0,
      avatar: '💻',
      keywords: ['클라우드', '임베디드', '백엔드', '스타트업자문', '시스템설계'],
      project: {
        name: '스마트 제조공장 IoT 통합 제어 플랫폼 아키텍처 총괄',
        role: '수석 소프트웨어 아키텍트 (PM)',
        desc: '실시간 센서 데이터 파이프라인 및 고가용성 마이크로서비스 설계 노하우 전수'
      }
    },
    {
      uuid: 'uuid:adv-2026-b924',
      name: '박*수',
      nickname: '기술장인70',
      domain: 'manufacturing',
      domainLabel: '🏭 제조 · 사출 · 품질',
      years: 35,
      rate: 2.5,
      avatar: '⚙️',
      keywords: ['금형사출', '품질인증', '공정개선', '원가절감', 'ISO9001'],
      project: {
        name: '친환경 전기차 배터리팩 경량화 프레임 사출 공정 최적화',
        role: '품질총괄 상무이사',
        desc: '금형 불량률 95% 감소 공정 혁신 및 해외 완성차 품질 승인 획득 자문'
      }
    },
    {
      uuid: 'uuid:adv-2026-c311',
      name: '이*원',
      nickname: '금융멘토',
      domain: 'finance',
      domainLabel: '💼 금융 · 여신 · 투자심사',
      years: 28,
      rate: 3.5,
      avatar: '📈',
      keywords: ['기업대출', '재무제표분석', '스타트업투자', '자금조달', '정책자금'],
      project: {
        name: '중소 벤처기업 정책자금 융자 및 기술평가 심사 500건+',
        role: '시중은행 기업금융 심사부장',
        desc: '초기 스타트업 재무제표 건전화, 신용보증기금 자금 매칭 컨설팅'
      }
    }
  ],

  // High risk households for Admin Dashboard
  riskUnits: [
    { id: 'u104-302', name: '박정자 어르신', address: '104동 302호', days: 3, age: 79, phone: '010-3341-XXXX', status: 'critical', handOver: false },
    { id: 'u102-504', name: '이순남 어르신', address: '102동 504호', days: 3, age: 84, phone: '010-8821-XXXX', status: 'critical', handOver: false },
    { id: 'u105-1102', name: '최기철 어르신', address: '105동 1102호', days: 2, age: 76, phone: '010-5512-XXXX', status: 'warning', handOver: false }
  ],

  // Transaction Ledger
  transactions: [
    { id: 'tx-01', title: '단지 내 화단 정원 가꾸기', type: 'earn', amount: 1.5, date: '2026.08.15 14:00', hash: '0x8f2a...1b9c' },
    { id: 'tx-02', title: '단지 코인빨래방 (대형세탁 1회)', type: 'spend', amount: 2.0, date: '2026.08.14 10:30', hash: '0x3c7e...9a41' },
    { id: 'tx-03', title: '독거 이웃 말벗 나눔 활동', type: 'earn', amount: 1.0, date: '2026.08.13 16:00', hash: '0x1d4a...55e2' }
  ],

  // Anchoring records
  anchoringRecords: [
    { batchDate: '2026-08-15', count: 1288, merkleRoot: '0x7f4e91ac28bc9a1038e811904bf2389d', status: 'Anchored 🟢' },
    { batchDate: '2026-08-14', count: 1294, merkleRoot: '0x1a89bf44dc8109ef8821034bcfa89211', status: 'Anchored 🟢' }
  ]
};

// --- Web Audio Synthesis (Chimes & Sirens) ---
let audioCtx = null;
function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

function playBeepSuccess() {
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, now); // A5
    osc.frequency.exponentialRampToValueAtTime(1760, now + 0.15); // A6
    
    gain.gain.setValueAtTime(0.3, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    osc.start(now);
    osc.stop(now + 0.2);
    
    if (navigator.vibrate) navigator.vibrate([100, 50, 100]);
  } catch (e) {
    console.warn('Audio not allowed or supported:', e);
  }
}

function playCoinChime() {
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;
    [523.25, 659.25, 783.99, 1046.5].forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.2, now + i * 0.08);
      gain.gain.exponentialRampToValueAtTime(0.01, now + i * 0.08 + 0.25);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + i * 0.08);
      osc.stop(now + i * 0.08 + 0.25);
    });
  } catch (e) {
    console.warn('Audio error:', e);
  }
}

let sirenInterval = null;
function startSirenSound() {
  try {
    const ctx = getAudioContext();
    let toggle = false;
    sirenInterval = setInterval(() => {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.value = toggle ? 950 : 650;
      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.28);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.3);
      toggle = !toggle;
    }, 300);
  } catch (e) {}
}

function stopSirenSound() {
  if (sirenInterval) {
    clearInterval(sirenInterval);
    sirenInterval = null;
  }
}

// --- Text To Speech (TTS) ---
function speakText(text) {
  if (!State.ttsEnabled || !('speechSynthesis' in window)) return;
  try {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ko-KR';
    utterance.rate = 0.95; // Slightly slower for seniors
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  } catch (e) {
    console.warn('TTS error:', e);
  }
}

// --- Toast Notification ---
function showToast(message, icon = '✅') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s';
    setTimeout(() => toast.remove(), 300);
  }, 2800);
}

// --- Tab Switching ---
function switchTab(tabId) {
  State.activeTab = tabId;
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  
  const targetPane = document.getElementById(tabId);
  if (targetPane) targetPane.classList.add('active');
  
  const targetNav = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
  if (targetNav) targetNav.classList.add('active');
  
  // Expand container if on admin tab
  const appContainer = document.getElementById('app-container');
  const bottomNav = document.getElementById('bottom-nav');
  if (tabId === 'tab-admin') {
    appContainer.classList.add('admin-expanded');
    bottomNav.classList.add('admin-expanded');
  } else {
    appContainer.classList.remove('admin-expanded');
    bottomNav.classList.remove('admin-expanded');
  }

  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// --- Barcode & QR Code Rendering ---
function renderMockQRCode(canvasId, text) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const size = canvas.width;
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, size, size);
  
  // Draw simulated QR matrix with high contrast
  ctx.fillStyle = '#0f172a';
  const grid = 17;
  const cellSize = size / grid;
  
  // Seed random from text
  let seed = 0;
  for (let i = 0; i < text.length; i++) seed += text.charCodeAt(i);
  
  for (let r = 0; r < grid; r++) {
    for (let c = 0; c < grid; c++) {
      // Corner alignment boxes
      const isCorner1 = r < 5 && c < 5;
      const isCorner2 = r < 5 && c >= grid - 5;
      const isCorner3 = r >= grid - 5 && c < 5;
      if (isCorner1 || isCorner2 || isCorner3) {
        if ((r === 0 || r === 4 || c === 0 || c === 4) && isCorner1) ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
        else if ((r >= 1 && r <= 3 && c >= 1 && c <= 3) && isCorner1) ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
        else if ((r === 0 || r === 4 || c === grid - 5 || c === grid - 1) && isCorner2) ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
        else if ((r >= 1 && r <= 3 && c >= grid - 4 && c <= grid - 2) && isCorner2) ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
        else if ((r === grid - 5 || r === grid - 1 || c === 0 || c === 4) && isCorner3) ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
        else if ((r >= grid - 4 && r <= grid - 2 && c >= 1 && c <= 3) && isCorner3) ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
      } else {
        const rand = Math.sin(seed * (r * grid + c)) * 10000;
        if ((rand - Math.floor(rand)) > 0.45) {
          ctx.fillRect(c * cellSize, r * cellSize, cellSize, cellSize);
        }
      }
    }
  }
}

// --- 1-Second NFC Simulation ---
function simulate1SecNFCTag() {
  const btn = document.getElementById('btn-nfc-tag');
  btn.classList.add('btn-nfc-active');
  btn.innerHTML = '<span>⚡</span> 1초 접촉 인식 중...';
  
  setTimeout(() => {
    playBeepSuccess();
    btn.classList.remove('btn-nfc-active');
    btn.innerHTML = '<span>📲</span> 1초 NFC 태깅하기';
    
    // Update state
    State.vitalScore = 'safe';
    const nowStr = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
    State.lastVitalTime = `오늘 ${nowStr} (스마트폰 NFC 접촉 인증)`;
    State.mealReceived = true;
    State.dailyMealCount += 1;
    
    updateUI();
    showToast('K-BTF DID 1초 인증 성공! 오늘 생존신호가 등록되었습니다.', '🎉');
    speakText('인증이 완료되었습니다. 김영수 어르신, 좋은 하루 보내세요!');
  }, 1000);
}

// --- Cafeteria Kiosk Check-In Simulation ---
function checkInCafeteriaMeal() {
  playBeepSuccess();
  State.mealReceived = true;
  State.dailyMealCount += 1;
  const nowStr = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  State.lastVitalTime = `오늘 ${nowStr} (경로식당 무료급식 1초 태깅)`;
  updateUI();
  
  showToast('경로식당 1초 급식 체크인 완료! (식수 누적: ' + State.dailyMealCount + '명)', '🍚');
  speakText('김영수 어르신, 경로식당 무료 급식 확인 완료되었습니다. 맛있게 드세요!');
}

// --- Volunteer Lunchbox Delivery Check ---
function checkInLunchboxDelivery(unitName) {
  playBeepSuccess();
  showToast(`${unitName} 도시락 배달 및 안부 확인이 완료되었습니다.`, '🍱');
  speakText(`${unitName} 배달 완료 등록되었습니다.`);
}

// --- Time Credit Actions ---
function applyJob(title, reward) {
  playCoinChime();
  State.credits += reward;
  const nowStr = new Date().toLocaleDateString('ko-KR') + ' ' + new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  const txHash = '0x' + Array.from({length: 8}, () => Math.floor(Math.random()*16).toString(16)).join('') + '...';
  
  State.transactions.unshift({
    id: 'tx-' + Date.now(),
    title: title,
    type: 'earn',
    amount: reward,
    date: nowStr,
    hash: txHash
  });
  
  updateUI();
  showToast(`[${title}] 참여 완료! +${reward} TC가 지갑으로 적립되었습니다.`, '💰');
  speakText(`축하합니다! ${reward} 시간크레딧이 적립되었습니다.`);
}

function payWithTimeCredit(storeName, cost) {
  if (State.credits < cost) {
    alert('시간크레딧 잔액이 부족합니다!');
    return;
  }
  playCoinChime();
  State.credits -= cost;
  const nowStr = new Date().toLocaleDateString('ko-KR') + ' ' + new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  const txHash = '0x' + Array.from({length: 8}, () => Math.floor(Math.random()*16).toString(16)).join('') + '...';
  
  State.transactions.unshift({
    id: 'tx-' + Date.now(),
    title: storeName,
    type: 'spend',
    amount: cost,
    date: nowStr,
    hash: txHash
  });
  
  updateUI();
  closeModal('modal-payment');
  showToast(`[${storeName}] ${cost} TC 결제 완료! (Tx: ${txHash})`, '🧾');
  speakText(`${storeName} ${cost} 시간크레딧 결제가 안전하게 처리되었습니다.`);
}

// --- SOS Emergency System ---
let sosTimer = null;
let sosSeconds = 30;

function triggerSOSModal() {
  sosSeconds = 30;
  const modal = document.getElementById('modal-sos');
  modal.classList.add('active');
  document.getElementById('sos-countdown-num').innerText = sosSeconds;
  
  startSirenSound();
  speakText('어르신, 괜찮으신가요? 30초 후 관리사무소와 119로 자동 긴급 출동 요청이 발송됩니다.');
  
  sosTimer = setInterval(() => {
    sosSeconds -= 1;
    document.getElementById('sos-countdown-num').innerText = sosSeconds;
    if (sosSeconds <= 0) {
      clearInterval(sosTimer);
      confirmSOSDispatch();
    }
  }, 1000);
}

function cancelSOS() {
  if (sosTimer) clearInterval(sosTimer);
  stopSirenSound();
  closeModal('modal-sos');
  showToast('긴급 SOS 경보가 취소되었습니다. (안심 상태 유지)', '🛡️');
  speakText('긴급 경보가 취소되었습니다. 안심하세요.');
}

function confirmSOSDispatch() {
  if (sosTimer) clearInterval(sosTimer);
  stopSirenSound();
  closeModal('modal-sos');
  
  showToast('🚨 119 상황실 및 산남관리소로 긴급 구조 출동 요청이 전송되었습니다!', '🚨');
  speakText('119 구조대와 관리사무소에 비상 상황이 전송되었습니다. 곧 도움의 손길이 도착합니다.');
  
  // Add to Admin alert log
  State.riskUnits.unshift({
    id: 'sos-' + Date.now(),
    name: '김영수 어르신 (긴급 SOS)',
    address: '104동 702호',
    days: 0,
    age: 78,
    phone: '010-7712-XXXX',
    status: 'sos',
    handOver: false
  });
  updateUI();
}

// --- Admin Hand-Over & Daily Anchoring ---
function signHandOver(unitId) {
  playBeepSuccess();
  const unit = State.riskUnits.find(u => u.id === unitId);
  if (unit) {
    unit.handOver = true;
    updateUI();
    showToast(`[${unit.name} - ${unit.address}] K-BTF DID 조기 이관 상호 전자서명 완료!`, '✍️');
    speakText(`${unit.name} 세대 조기 이관 전자 서명이 완료되었습니다.`);
  }
}

function triggerDailyBatchAnchoring() {
  playBeepSuccess();
  const todayStr = new Date().toISOString().split('T')[0];
  const newMerkle = '0x' + Array.from({length: 32}, () => Math.floor(Math.random()*16).toString(16)).join('');
  
  State.anchoringRecords.unshift({
    batchDate: todayStr,
    count: 1339,
    merkleRoot: newMerkle,
    status: 'Anchored 🟢 (K-BTF 공증)'
  });
  
  updateUI();
  showToast('오늘자 1,339건 전체 생존신호 K-BTF 블록체인 일일 앵커링 공증 성공!', '⛓️');
  speakText('K-BTF 블록체인 일일 배치 앵커링이 정상 완료되었습니다.');
}

// --- Edeum-Chat AI Chatbot ---
const ChatBot = {
  responses: {
    menu: '🍚 **오늘 경로식당 점심 메뉴**는 영양 소고기 미역국, 잡곡밥, 삼치구이, 계란찜, 깍두기입니다! 배식 시간은 11시 30분부터 13시까지입니다.',
    credit: `💰 현재 어르신의 **보유 햇살머니 잔액은 ${State.credits} SM (시간크레딧 ${State.credits} TC)**입니다. 아나바다 장터 물품 구매나 코인빨래방, 시니어 자문 등에 안심하고 사용하실 수 있습니다! (현금 환전 불가 / 비소득성 상생화폐)`,
    market: '🛍️ **아나바다 상생 장터**에서는 입주민 간 중고거래, 무료 나눔, 공동구매가 모두 햇살머니로 진행됩니다. 상단 [아나바다] 탭에서 필요한 물품을 찾아보세요!',
    advisor: '🧑‍💼 **시니어 커리어 어드바이저**는 30년 현장 경험(IT, 제조, 금융 등)을 스타트업 및 청년 기업에 전수하고 햇살머니로 보상받는 플랫폼입니다. AI 스마트 계약과 AI 분쟁조정이 안전하게 보호합니다.',
    volunteer: '🤝 **추천 짬바이트 활동**: [화단 정원 가꾸기: 1.5 SM], [이웃 말벗 동행: 1.0 SM]가 있습니다. 참여하시려면 [햇살머니] 탭에서 신청 버튼을 눌러주세요!',
    health: '🏥 **산남종합사회복지관 건강증진실**에서 매주 화/목 혈압 및 혈당 무료 체크를 해드리고 있습니다. 필요하시면 동행 봉사자 매칭도 도와드립니다.',
    laundry: '🧺 **단지 내 코인빨래방**은 103동 지하 1층에 있으며, 2 SM 바코드를 기기에 스캔하시면 대형 세탁기를 무료로 돌리실 수 있습니다.'
  },

  send(userText) {
    if (!userText.trim()) return;
    const msgBox = document.getElementById('chat-messages');
    
    // Append user message
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble user';
    userBubble.innerText = userText;
    msgBox.appendChild(userBubble);
    
    document.getElementById('chat-input-text').value = '';
    msgBox.scrollTop = msgBox.scrollHeight;
    
    // Simulate AI thinking and reply
    setTimeout(() => {
      let botReply = '어르신, 문의주신 내용 잘 확인했습니다. 무엇이든 더 궁금하신 점이 있으시면 편하게 말씀해 주세요!';
      const t = userText.toLowerCase();
      if (t.includes('식단') || t.includes('메뉴') || t.includes('점심') || t.includes('밥')) botReply = ChatBot.responses.menu;
      else if (t.includes('장터') || t.includes('아나바다') || t.includes('중고') || t.includes('나눔') || t.includes('공구')) botReply = ChatBot.responses.market;
      else if (t.includes('어드바이저') || t.includes('시니어') || t.includes('자문') || t.includes('경력') || t.includes('멘토')) botReply = ChatBot.responses.advisor;
      else if (t.includes('햇살머니') || t.includes('크레딧') || t.includes('잔액') || t.includes('얼마') || t.includes('돈')) botReply = `💰 현재 어르신의 **보유 햇살머니 잔액은 ${State.credits.toFixed(1)} SM**입니다. 아나바다 장터나 코인빨래방에서 바로 사용하실 수 있습니다! (현금 환전 불가)`;
      else if (t.includes('봉사') || t.includes('일자리') || t.includes('짬바이트') || t.includes('신청')) botReply = ChatBot.responses.volunteer;
      else if (t.includes('아파') || t.includes('병원') || t.includes('건강') || t.includes('의사')) botReply = ChatBot.responses.health;
      else if (t.includes('빨래') || t.includes('세탁') || t.includes('이불')) botReply = ChatBot.responses.laundry;
      
      const botBubble = document.createElement('div');
      botBubble.className = 'chat-bubble bot';
      botBubble.innerHTML = botReply.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      msgBox.appendChild(botBubble);
      msgBox.scrollTop = msgBox.scrollHeight;
      
      // Auto speak first sentence
      const plainText = botReply.replace(/\*\*/g, '').replace(/[🍚💰🤝🏥🧺🛍️🧑‍💼]/g, '');
      speakText(plainText);
    }, 600);
  }
};

// ==========================================================================
// Top 3 Customizable Feature Core Functions
// ==========================================================================
const FeatureRegistry = {
  did: {
    key: 'did',
    title: '모바일 주민증',
    desc: '1초 QR / NFC 태깅 및 복지시설 인증',
    icon: '🪪',
    action: () => {
      switchTab('tab-resident-id');
      document.getElementById('track-smartphone-card')?.scrollIntoView({ behavior: 'smooth' });
    }
  },
  anabada: {
    key: 'anabada',
    title: '아나바다 장터',
    desc: '햇살머니 전용 중고거래·나눔·공동구매',
    icon: '🛍️',
    action: () => switchTab('tab-anabada')
  },
  advisor: {
    key: 'advisor',
    title: '시니어 어드바이저',
    desc: '30년 현장 경력 자문 & 햇살머니 보상',
    icon: '🧑‍💼',
    action: () => switchTab('tab-advisor')
  },
  meal: {
    key: 'meal',
    title: '경로식당 체크인',
    desc: '1초 급식 체크 및 안심 생존신호 등록',
    icon: '🍚',
    action: () => switchTab('tab-meal-vital')
  },
  credit: {
    key: 'credit',
    title: '햇살머니 지갑',
    desc: '노동화폐 잔액 확인 & 짬바이트 활동',
    icon: '💰',
    action: () => switchTab('tab-credit')
  },
  sos: {
    key: 'sos',
    title: '긴급 SOS 비상벨',
    desc: '30초 카운트다운 후 119·관리소 자동 연결',
    icon: '🚨',
    action: () => triggerSOSModal()
  },
  chat: {
    key: 'chat',
    title: '이듬챗 AI 말벗',
    desc: '24시간 복지 안내 및 어르신 말벗 대화',
    icon: '🤖',
    action: () => switchTab('tab-chat')
  }
};

function renderTop3Grid() {
  const container = document.getElementById('top3-grid-container');
  if (!container) return;

  const [top1Key, top2Key, top3Key] = State.top3Features;
  const f1 = FeatureRegistry[top1Key] || FeatureRegistry.did;
  const f2 = FeatureRegistry[top2Key] || FeatureRegistry.anabada;
  const f3 = FeatureRegistry[top3Key] || FeatureRegistry.advisor;

  container.innerHTML = `
    <!-- Top 1: Left 50% Full Height -->
    <div class="top3-card top1" onclick="executeFeatureAction('${f1.key}')">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <span class="top3-rank-badge">🥇 TOP 1</span>
        <span style="font-size: 0.72em; opacity: 0.85;">자주 사용</span>
      </div>
      <div class="top3-icon">${f1.icon}</div>
      <div>
        <div class="top3-label">${f1.title}</div>
        <div class="top3-desc">${f1.desc}</div>
      </div>
    </div>

    <!-- Top 2: Right 50% Top -->
    <div class="top3-card top2" onclick="executeFeatureAction('${f2.key}')">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <span class="top3-rank-badge">🥈 TOP 2</span>
        <span class="top3-icon" style="font-size: 20px;">${f2.icon}</span>
      </div>
      <div>
        <div class="top3-label">${f2.title}</div>
        <div class="top3-desc">${f2.desc}</div>
      </div>
    </div>

    <!-- Top 3: Right 50% Bottom -->
    <div class="top3-card top3" onclick="executeFeatureAction('${f3.key}')">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <span class="top3-rank-badge">🥉 TOP 3</span>
        <span class="top3-icon" style="font-size: 20px;">${f3.icon}</span>
      </div>
      <div>
        <div class="top3-label">${f3.title}</div>
        <div class="top3-desc">${f3.desc}</div>
      </div>
    </div>
  `;
}

function executeFeatureAction(key) {
  if (FeatureRegistry[key] && typeof FeatureRegistry[key].action === 'function') {
    FeatureRegistry[key].action();
  }
}

function saveTop3Settings() {
  const s1 = document.getElementById('top3-select-1').value;
  const s2 = document.getElementById('top3-select-2').value;
  const s3 = document.getElementById('top3-select-3').value;

  if (s1 === s2 || s1 === s3 || s2 === s3) {
    alert('Top 1, Top 2, Top 3 기능은 서로 중복되지 않게 선택해 주세요.');
    return;
  }

  State.top3Features = [s1, s2, s3];
  renderTop3Grid();
  closeModal('modal-top3-customize');
  playBeepSuccess();
  showToast('자주 쓰는 Top 3 메뉴 설정이 성공적으로 저장되었습니다!', '⭐');
  speakText('Top 3 기능 배치가 변경되었습니다.');
}

// ==========================================================================
// Anabada Market Functions (햇살머니 전용)
// ==========================================================================
function filterMarket(type) {
  State.activeMarketFilter = type;
  document.querySelectorAll('.market-filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-market-filter') === type);
  });
  renderMarketItems();
}

function renderMarketItems() {
  const listEl = document.getElementById('market-items-list');
  if (!listEl) return;

  let items = State.marketItems;
  if (State.activeMarketFilter !== 'all') {
    items = items.filter(it => it.type === State.activeMarketFilter);
  }

  if (items.length === 0) {
    listEl.innerHTML = `
      <div style="text-align: center; padding: 30px 10px; color: var(--text-muted);">
        <div style="font-size: 32px; margin-bottom: 8px;">📭</div>
        등록된 물품이 없습니다.
      </div>
    `;
    return;
  }

  listEl.innerHTML = items.map(item => {
    const isUsed = item.type === 'used';
    const isFree = item.type === 'free';
    const isGroup = item.type === 'group';

    const typeTag = isUsed 
      ? '<span class="market-type-tag market-type-used">중고거래</span>'
      : isFree 
        ? '<span class="market-type-tag market-type-free">무료나눔</span>'
        : '<span class="market-type-tag market-type-group">공동구매</span>';

    const priceText = isFree 
      ? '<span class="market-price-free">무료 나눔 (0 SM)</span>'
      : `<span class="market-price">${item.price.toFixed(1)} <span style="font-size:0.75em;">SM</span></span>`;

    const groupProgress = isGroup 
      ? `<div style="font-size:0.78em; color:#b45309; margin-top:3px; font-weight:700;">모집 현황: ${item.participants}/${item.maxParticipants}세대 완료</div>`
      : '';

    return `
      <div class="market-item-card" onclick="openMarketItemDetail('${item.id}')" style="cursor: pointer;">
        <div class="market-item-thumb">${item.icon}</div>
        <div class="market-item-body">
          <div>
            <div class="market-item-title-row">
              <div class="market-item-title">${item.title}</div>
              ${typeTag}
            </div>
            <div class="market-item-meta">${item.seller} · ${item.date}</div>
            ${groupProgress}
          </div>
          <div class="market-item-bottom">
            ${priceText}
            <button class="btn-action-sm" style="background: ${isFree ? 'var(--success)' : '#d97706'}; font-size: 0.78em; padding: 4px 10px;">
              ${isFree ? '나눔받기' : isGroup ? '공구참여' : '상세보기'}
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function toggleMarketPriceInput(type) {
  const priceGroup = document.getElementById('reg-market-price-group');
  if (priceGroup) {
    if (type === 'free') {
      priceGroup.style.display = 'none';
      document.getElementById('reg-market-price').value = '0';
    } else {
      priceGroup.style.display = 'block';
      if (document.getElementById('reg-market-price').value === '0') {
        document.getElementById('reg-market-price').value = '5.0';
      }
    }
  }
}

function submitMarketItem() {
  const type = document.getElementById('reg-market-type').value;
  const title = document.getElementById('reg-market-title').value.trim();
  const price = parseFloat(document.getElementById('reg-market-price').value) || 0;
  const icon = document.getElementById('reg-market-icon').value;
  const desc = document.getElementById('reg-market-desc').value.trim();

  if (!title) {
    alert('물품명을 입력해 주세요.');
    return;
  }

  const newItem = {
    id: 'mkt-' + Date.now(),
    type: type,
    title: title,
    price: type === 'free' ? 0 : price,
    icon: icon,
    seller: '104동 702호 (김영수)',
    desc: desc || '직접 만나서 전달해 드립니다.',
    date: '방금 전'
  };

  if (type === 'group') {
    newItem.participants = 1;
    newItem.maxParticipants = 5;
  }

  State.marketItems.unshift(newItem);
  renderMarketItems();
  closeModal('modal-market-register');
  playCoinChime();
  showToast(`[${title}] 아나바다 장터에 등록되었습니다!`, '🛍️');
  speakText(`${title} 물품 등록이 완료되었습니다.`);

  // Reset form
  document.getElementById('reg-market-title').value = '';
  document.getElementById('reg-market-desc').value = '';
}

function openMarketItemDetail(itemId) {
  const item = State.marketItems.find(it => it.id === itemId);
  if (!item) return;

  State.selectedMarketItemId = itemId;
  document.getElementById('md-icon').innerText = item.icon;
  document.getElementById('md-title').innerText = item.title;
  document.getElementById('md-seller').innerText = `판매/나눔자: ${item.seller}`;
  document.getElementById('md-desc').innerText = item.desc;

  const priceWrap = document.getElementById('md-price-wrap');
  const actionBtn = document.getElementById('btn-md-action');

  if (item.type === 'free') {
    priceWrap.innerHTML = '<span style="color: var(--success);">0 SM (무료 나눔)</span>';
    actionBtn.innerText = '🎁 무료 나눔 신청하기';
    actionBtn.style.background = 'var(--success)';
  } else if (item.type === 'group') {
    priceWrap.innerHTML = `<span>${item.price.toFixed(1)}</span> <span style="font-size:0.7em;">햇살머니 (공동구매가)</span>`;
    actionBtn.innerText = `🛒 공동구매 참여하기 (${item.price.toFixed(1)} SM)`;
    actionBtn.style.background = '#d97706';
  } else {
    priceWrap.innerHTML = `<span>${item.price.toFixed(1)}</span> <span style="font-size:0.7em;">햇살머니 (SM)</span>`;
    actionBtn.innerText = `🛒 ${item.price.toFixed(1)} SM 거래하기`;
    actionBtn.style.background = '#d97706';
  }

  openModal('modal-market-detail');
}

function executeMarketAction() {
  const item = State.marketItems.find(it => it.id === State.selectedMarketItemId);
  if (!item) return;

  if (item.price > 0 && State.credits < item.price) {
    alert(`햇살머니 잔액이 부족합니다! (현재 잔액: ${State.credits.toFixed(1)} SM / 필요: ${item.price.toFixed(1)} SM)`);
    return;
  }

  if (item.price > 0) {
    State.credits -= item.price;
  }

  if (item.type === 'group') {
    item.participants = Math.min(item.maxParticipants, item.participants + 1);
  }

  const nowStr = new Date().toLocaleDateString('ko-KR') + ' ' + new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  const txHash = '0x' + Array.from({length: 8}, () => Math.floor(Math.random()*16).toString(16)).join('') + '...';

  State.transactions.unshift({
    id: 'tx-' + Date.now(),
    title: `[아나바다] ${item.title}`,
    type: item.price > 0 ? 'spend' : 'earn',
    amount: item.price,
    date: nowStr,
    hash: txHash
  });

  updateUI();
  renderMarketItems();
  closeModal('modal-market-detail');
  playCoinChime();

  const msg = item.type === 'free' 
    ? `[${item.title}] 무료 나눔 신청이 완료되었습니다. 이웃에게 안심 메시지가 전달됩니다.`
    : `[${item.title}] ${item.price.toFixed(1)} 햇살머니 결제 및 거래 예약 완료! (Tx: ${txHash})`;

  showToast(msg, '🎉');
  speakText(item.type === 'free' ? '무료 나눔 신청이 접수되었습니다.' : '햇살머니 거래가 체결되었습니다.');
}

function chatWithSeller() {
  closeModal('modal-market-detail');
  switchTab('tab-chat');
  ChatBot.send('아나바다 장터 물품 문의 및 전달 일정을 조율하고 싶습니다.');
}

// ==========================================================================
// Senior Career Advisor Functions (Obsidian 설계 완벽 구현)
// ==========================================================================
function filterAdvisorDomain(domain) {
  State.activeAdvisorDomain = domain;
  document.querySelectorAll('.domain-pill-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-domain') === domain);
  });
  renderAdvisorCards();
}

function filterAdvisorKeyword(keyword) {
  State.advisorKeyword = keyword.trim().toLowerCase();
  renderAdvisorCards();
}

function applyAdvisorSearch() {
  const kw = document.getElementById('advisor-search-input').value;
  filterAdvisorKeyword(kw);
}

function renderAdvisorCards() {
  const listEl = document.getElementById('advisor-cards-list');
  if (!listEl) return;

  let filtered = State.advisors;

  if (State.activeAdvisorDomain !== 'all') {
    filtered = filtered.filter(adv => adv.domain === State.activeAdvisorDomain);
  }

  if (State.advisorKeyword) {
    filtered = filtered.filter(adv => {
      const matchKw = adv.keywords.some(k => k.toLowerCase().includes(State.advisorKeyword));
      const matchDomain = adv.domainLabel.toLowerCase().includes(State.advisorKeyword);
      const matchProj = adv.project.name.toLowerCase().includes(State.advisorKeyword);
      const matchNick = adv.nickname.toLowerCase().includes(State.advisorKeyword);
      return matchKw || matchDomain || matchProj || matchNick;
    });
  }

  if (filtered.length === 0) {
    listEl.innerHTML = `
      <div style="text-align: center; padding: 30px 10px; color: var(--text-muted);">
        <div style="font-size: 32px; margin-bottom: 8px;">🔍</div>
        조건에 맞는 시니어 어드바이저를 찾을 수 없습니다.
      </div>
    `;
    return;
  }

  listEl.innerHTML = filtered.map(adv => `
    <div class="advisor-card-item">
      <div class="advisor-profile-row">
        <div class="advisor-avatar-box">
          <div class="advisor-avatar-circle">${adv.avatar}</div>
          <div>
            <div style="font-weight: 800; font-size: 1.1em; color: var(--text-main); display: flex; align-items: center; gap: 6px;">
              <span>${adv.nickname}</span>
              <span style="font-size: 0.72em; background: #f3e8ff; color: #7c3aed; padding: 2px 7px; border-radius: 10px; font-weight: 800;">
                경력 ${adv.years}년
              </span>
            </div>
            <div style="font-size: 0.82em; color: var(--text-muted); margin-top: 2px;">
              ${adv.domainLabel} · <span style="font-family: monospace; font-size: 0.9em;">${adv.uuid}</span>
            </div>
          </div>
        </div>
        <span class="kbtf-tag" style="background: #e0e7ff; color: #3730a3;">공증 완료</span>
      </div>

      <!-- Keyword Tags (Max 5) -->
      <div class="advisor-tags-row">
        ${adv.keywords.map(kw => `<span class="adv-keyword-tag">#${kw}</span>`).join('')}
      </div>

      <!-- Key Project Preview -->
      <div class="adv-project-box">
        <div style="font-weight: 800; margin-bottom: 2px;">🏆 대표 프로젝트: ${adv.project.name}</div>
        <div style="font-size: 0.8em; opacity: 0.9;"><strong>역할:</strong> ${adv.project.role}</div>
        <div style="font-size: 0.8em; opacity: 0.85; margin-top: 2px;">${adv.project.desc}</div>
      </div>

      <!-- Rate & Action -->
      <div class="adv-rate-row">
        <div>
          <span style="font-size: 0.8em; color: var(--text-muted);">자문료:</span>
          <strong style="font-size: 1.15em; color: #7c3aed;">${adv.rate.toFixed(1)} SM</strong>
          <span style="font-size: 0.75em; color: var(--text-muted);">/시간</span>
        </div>
        <button class="btn-action-sm" style="background: #7c3aed;" onclick="openAdvisorContractModal('${adv.uuid}')">
          📜 표준 스마트 계약 & 자문 요청
        </button>
      </div>
    </div>
  `).join('');
}

function openAdvisorContractModal(advUuid) {
  const adv = State.advisors.find(a => a.uuid === advUuid);
  if (!adv) return;

  State.selectedAdvisorUuid = advUuid;
  document.getElementById('contract-adv-name').innerText = adv.nickname;
  document.getElementById('contract-adv-domain').innerText = adv.domainLabel;
  document.getElementById('contract-adv-uuid').innerText = `식별자: ${adv.uuid}`;
  document.getElementById('contract-rate').value = adv.rate.toFixed(1);

  calcContractTotal();
  openModal('modal-advisor-contract');
}

function calcContractTotal() {
  const hours = parseFloat(document.getElementById('contract-hours').value) || 0;
  const rate = parseFloat(document.getElementById('contract-rate').value) || 0;
  const total = hours * rate;
  document.getElementById('contract-total-sm').innerText = total.toFixed(1);
}

function signAdvisorContract() {
  const adv = State.advisors.find(a => a.uuid === State.selectedAdvisorUuid);
  if (!adv) return;

  const hours = parseFloat(document.getElementById('contract-hours').value) || 0;
  const total = hours * adv.rate;

  if (State.credits < total) {
    alert(`햇살머니 잔액이 부족합니다! (현재 잔액: ${State.credits.toFixed(1)} SM / 필요 에스크로: ${total.toFixed(1)} SM)`);
    return;
  }

  State.credits -= total;
  const nowStr = new Date().toLocaleDateString('ko-KR') + ' ' + new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  const contractHash = '0x' + Array.from({length: 12}, () => Math.floor(Math.random()*16).toString(16)).join('');

  State.transactions.unshift({
    id: 'tx-adv-' + Date.now(),
    title: `[자문계약 에스크로] ${adv.nickname} (${hours}시간)`,
    type: 'spend',
    amount: total,
    date: nowStr,
    hash: contractHash.slice(0, 10) + '...'
  });

  updateUI();
  closeModal('modal-advisor-contract');
  playBeepSuccess();

  showToast(`[${adv.nickname} 어드바이저] 표준 스마트 계약 체결 완료! (에스크로: ${total.toFixed(1)} SM, Tx: ${contractHash.slice(0, 8)}...)`, '📜');
  speakText(`${adv.nickname} 어드바이저와 자문 스마트 계약이 체결되었습니다. 분쟁 시 AI 조정관이 지원합니다.`);
}

function submitAdvisorProfile() {
  const name = document.getElementById('adv-reg-name').value.trim();
  const nickname = document.getElementById('adv-reg-nickname').value.trim();
  const phone = document.getElementById('adv-reg-phone').value.trim();
  const email = document.getElementById('adv-reg-email').value.trim();
  const domain = document.getElementById('adv-reg-domain').value;
  const kwInput = document.getElementById('adv-reg-keywords').value.trim();
  const projName = document.getElementById('adv-reg-project-name').value.trim();
  const projRole = document.getElementById('adv-reg-project-role').value.trim();
  const projDesc = document.getElementById('adv-reg-project-desc').value.trim();
  const years = parseInt(document.getElementById('adv-reg-years').value) || 30;
  const rate = parseFloat(document.getElementById('adv-reg-rate').value) || 3.0;

  if (!nickname) {
    alert('공개될 닉네임을 입력해 주세요.');
    return;
  }

  // Generate 4-part UUID from name+phone+nickname+email hashing simulation
  const uuid = 'uuid:adv-2026-' + Array.from({length: 4}, () => Math.floor(Math.random()*16).toString(16)).join('');

  const domainLabels = {
    it: '💻 IT · SW · AI',
    manufacturing: '🏭 제조 · 사출 · 품질',
    finance: '💼 금융 · 여신 · 심사',
    logistics: '🚚 운수 · 물류',
    agri: '🌾 농업 · 어업',
    etc: '📝 전문 자문'
  };

  const domainAvatars = {
    it: '💻',
    manufacturing: '⚙️',
    finance: '📈',
    logistics: '🚚',
    agri: '🌾',
    etc: '🧑‍💼'
  };

  const keywords = kwInput ? kwInput.split(',').map(s => s.trim()).filter(Boolean).slice(0, 5) : ['도메인전문가', '현장경력'];

  const newAdv = {
    uuid: uuid,
    name: name ? name.charAt(0) + '*' + (name.length > 2 ? name.charAt(name.length-1) : '') : '익명',
    nickname: nickname,
    domain: domain,
    domainLabel: domainLabels[domain] || '전문 자문',
    years: years,
    rate: rate,
    avatar: domainAvatars[domain] || '🧑‍💼',
    keywords: keywords,
    project: {
      name: projName || '도메인 핵심 프로젝트 현장 지휘',
      role: projRole || '총괄 기술 자문',
      desc: projDesc || '30년 현장 경험 기반 실무 노하우 전수'
    }
  };

  State.advisors.unshift(newAdv);
  renderAdvisorCards();
  closeModal('modal-advisor-register');
  playBeepSuccess();

  showToast(`[${nickname}] 시니어 어드바이저 등록 성공! (UUID: ${uuid})`, '🎉');
  speakText(`축하합니다! ${nickname} 님, 시니어 어드바이저로 성공적으로 등록되었습니다.`);
}

// --- Modal Helper Functions ---
function openModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.add('active');
}

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.remove('active');
}

// --- UI Update & Sync ---
function updateUI() {
  // Sync credit balances
  document.querySelectorAll('.sync-credits').forEach(el => {
    el.innerText = State.credits.toFixed(1);
  });
  
  // Sync vital status
  const vitalBox = document.getElementById('vital-status-box');
  const vitalText = document.getElementById('vital-time-text');
  if (vitalText) vitalText.innerText = State.lastVitalTime;
  
  // Sync meal check count
  const mealCountEl = document.getElementById('kiosk-meal-count');
  if (mealCountEl) mealCountEl.innerText = State.dailyMealCount;
  
  // Sync Ledger table
  const ledgerBox = document.getElementById('tx-ledger-list');
  if (ledgerBox) {
    ledgerBox.innerHTML = State.transactions.map(tx => `
      <div class="job-item">
        <div class="job-meta">
          <h4>${tx.title}</h4>
          <span style="font-size:0.8em; color:var(--text-muted);">${tx.date} · 해시: ${tx.hash}</span>
        </div>
        <div class="job-reward" style="color: ${tx.type === 'earn' ? 'var(--success)' : 'var(--danger)'}; font-size:1.1em;">
          ${tx.type === 'earn' ? '+' : '-'}${tx.amount.toFixed(1)} SM
        </div>
      </div>
    `).join('');
  }

  // Sync Admin Risk Table
  const riskBox = document.getElementById('admin-risk-list');
  if (riskBox) {
    riskBox.innerHTML = State.riskUnits.map(unit => `
      <div class="danger-unit-item" style="border-left: 5px solid ${unit.status === 'sos' ? 'red' : (unit.days >= 3 ? '#e11d48' : '#f59e0b')};">
        <div>
          <div style="font-weight:800; font-size:1.05em; display:flex; align-items:center; gap:6px;">
            <span>${unit.name}</span>
            <span style="background:${unit.status === 'sos' ? '#fee2e2' : '#ffe4e6'}; color:${unit.status === 'sos' ? '#b91c1c' : '#be123c'}; font-size:0.75em; padding:2px 8px; border-radius:10px;">
              ${unit.status === 'sos' ? '🚨 긴급 SOS 발동' : `${unit.days}일 연속 미태깅`}
            </span>
          </div>
          <div style="font-size:0.85em; color:var(--text-sub); margin-top:2px;">
            ${unit.address} (${unit.age}세) · 연락처: ${unit.phone}
          </div>
        </div>
        <div>
          ${unit.handOver ? 
            `<span style="color:var(--success); font-weight:800; font-size:0.85em;">✅ 전자서명 이관완료</span>` : 
            `<button class="btn-danger-outline" onclick="signHandOver('${unit.id}')">✍️ DID 조기 이관 서명</button>`
          }
        </div>
      </div>
    `).join('');
  }

  // Sync Anchoring Table
  const anchorBox = document.getElementById('admin-anchoring-list');
  if (anchorBox) {
    anchorBox.innerHTML = State.anchoringRecords.map(rec => `
      <div style="padding:10px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; font-size:0.85em;">
        <div>
          <strong>${rec.batchDate} 배치</strong> (${rec.count}건)
          <div style="font-family:monospace; color:var(--text-muted); font-size:0.85em;">Root: ${rec.merkleRoot}</div>
        </div>
        <div><span class="kbtf-tag">${rec.status}</span></div>
      </div>
    `).join('');
  }

  // Render Top 3 Grid, Market items, and Advisor cards
  renderTop3Grid();
  renderMarketItems();
  renderAdvisorCards();
}

// --- App Initialization ---
document.addEventListener('DOMContentLoaded', () => {
  // 1. Render QR codes
  renderMockQRCode('qr-canvas-resident', 'did:kbtf:kr:2026:08:702-KIM-YOUNGSOO');
  renderMockQRCode('qr-canvas-laundry', 'PAY-LAUNDRY-2.0TC-SANAM-103B1');
  
  // 2. Setup Senior Controls
  document.getElementById('btn-font-normal')?.addEventListener('click', () => {
    document.body.className = '';
    if (State.highContrast) document.body.classList.add('high-contrast');
    document.querySelectorAll('.font-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-font-normal').classList.add('active');
  });
  
  document.getElementById('btn-font-large')?.addEventListener('click', () => {
    document.body.className = 'font-large';
    if (State.highContrast) document.body.classList.add('high-contrast');
    document.querySelectorAll('.font-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-font-large').classList.add('active');
  });
  
  document.getElementById('btn-font-xlarge')?.addEventListener('click', () => {
    document.body.className = 'font-xlarge';
    if (State.highContrast) document.body.classList.add('high-contrast');
    document.querySelectorAll('.font-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-font-xlarge').classList.add('active');
  });

  document.getElementById('btn-toggle-contrast')?.addEventListener('click', () => {
    State.highContrast = !State.highContrast;
    document.body.classList.toggle('high-contrast', State.highContrast);
    showToast(State.highContrast ? '고대비 어르신 모드가 켜졌습니다.' : '일반 화면 모드로 전환되었습니다.');
  });

  document.getElementById('btn-toggle-tts')?.addEventListener('click', (e) => {
    State.ttsEnabled = !State.ttsEnabled;
    e.target.innerText = State.ttsEnabled ? '🔊 음성 켜짐' : '🔇 음성 꺼짐';
    showToast(State.ttsEnabled ? '음성 안내(TTS)가 켜졌습니다.' : '음성 안내가 꺼졌습니다.');
  });

  // 3. User Switcher
  document.getElementById('user-profile-select')?.addEventListener('change', (e) => {
    State.currentUser = e.target.value;
    if (State.currentUser === 'user1') {
      document.getElementById('user-name-display').innerText = '김영수 어르신';
      document.getElementById('user-addr-display').innerText = '청주 산남 2-1단지 104동 702호';
      document.getElementById('track-smartphone-card').style.display = 'block';
      document.getElementById('track-physical-nfc-card').style.display = 'none';
      switchTab('tab-resident-id');
    } else if (State.currentUser === 'user2') {
      document.getElementById('user-name-display').innerText = '박정자 어르신 (2G폰)';
      document.getElementById('user-addr-display').innerText = '청주 산남 2-1단지 104동 302호';
      document.getElementById('track-smartphone-card').style.display = 'none';
      document.getElementById('track-physical-nfc-card').style.display = 'block';
      switchTab('tab-resident-id');
    } else if (State.currentUser === 'admin') {
      switchTab('tab-admin');
    }
  });

  // 4. Two-Track Switcher
  document.getElementById('btn-track-smart')?.addEventListener('click', () => {
    document.getElementById('btn-track-smart').classList.add('active');
    document.getElementById('btn-track-nfc').classList.remove('active');
    document.getElementById('track-smartphone-card').style.display = 'block';
    document.getElementById('track-physical-nfc-card').style.display = 'none';
  });

  document.getElementById('btn-track-nfc')?.addEventListener('click', () => {
    document.getElementById('btn-track-nfc').classList.add('active');
    document.getElementById('btn-track-smart').classList.remove('active');
    document.getElementById('track-smartphone-card').style.display = 'none';
    document.getElementById('track-physical-nfc-card').style.display = 'block';
  });

  // 5. Navigation Tab Items
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');
      switchTab(tabId);
    });
  });

  // 6. Edeum-Chat Submit
  document.getElementById('chat-send-btn')?.addEventListener('click', () => {
    const text = document.getElementById('chat-input-text').value;
    ChatBot.send(text);
  });
  
  document.getElementById('chat-input-text')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      const text = document.getElementById('chat-input-text').value;
      ChatBot.send(text);
    }
  });

  // Quick Tags
  document.querySelectorAll('.quick-tag').forEach(tag => {
    tag.addEventListener('click', () => {
      const text = tag.innerText;
      ChatBot.send(text);
    });
  });

  // 7. PWA Service Worker Registration
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js')
      .then(reg => console.log('[PWA] Service Worker registered with scope:', reg.scope))
      .catch(err => console.warn('[PWA] Service Worker registration failed:', err));
  }

  // 8. PWA Install Prompt Listener
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    State.pwaDeferredPrompt = e;
    const installBanner = document.getElementById('install-pwa-bar');
    if (installBanner) installBanner.style.display = 'flex';
  });

  document.getElementById('btn-install-pwa')?.addEventListener('click', async () => {
    if (State.pwaDeferredPrompt) {
      State.pwaDeferredPrompt.prompt();
      const { outcome } = await State.pwaDeferredPrompt.userChoice;
      if (outcome === 'accepted') {
        showToast('우리단지 ON 앱이 홈 화면에 성공적으로 설치되었습니다!', '📱');
      }
      State.pwaDeferredPrompt = null;
      document.getElementById('install-pwa-bar').style.display = 'none';
    } else {
      showToast('브라우저 설정 메뉴에서 [홈 화면에 추가]를 눌러주세요!', 'ℹ️');
    }
  });

  updateUI();
});

