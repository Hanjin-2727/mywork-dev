#!/usr/bin/env python3
"""
Timeslot Video Frame Extractor & Interactive Viewer Generator
Developed by AI Expert 4-Agent Team (Orchestrator, Frontend/Design, Backend/DeepTech, Gov Expert)
"""

import os
import sys
import json
import shutil
import zipfile
import av
from PIL import Image

def extract_timeslot(
    video_path: str,
    output_base_dir: str,
    interval_sec: float = 3.0,
    target_width: int = 1920,
    quality: int = 80,
    format_type: str = "WEBP"
):
    """
    Extracts frames at regular time intervals and generates metadata.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    frames_dir = os.path.join(output_base_dir, f"frames_{int(interval_sec)}s")
    os.makedirs(frames_dir, exist_ok=True)

    container = av.open(video_path)
    stream = container.streams.video[0]
    fps = float(stream.average_rate) if stream.average_rate else 30.0
    duration = float(stream.duration * stream.time_base) if stream.duration else (stream.frames / fps if stream.frames else 0.0)

    print(f"[*] Processing: {os.path.basename(video_path)}")
    print(f"[*] Duration: {duration:.2f}s ({duration/60:.2f} min), Original FPS: {fps:.2f}, Res: {stream.width}x{stream.height}")
    print(f"[*] Extracting 1 frame every {interval_sec} seconds (Target Format: {format_type}, Quality: {quality})")

    frame_step = int(round(fps * interval_sec))
    if frame_step < 1:
        frame_step = 1

    extracted_frames = []
    saved_count = 0
    total_bytes = 0

    ext = "webp" if format_type.upper() == "WEBP" else "jpg"

    for i, frame in enumerate(container.decode(stream)):
        if i % frame_step == 0:
            current_sec = i / fps
            mins = int(current_sec // 60)
            secs = int(current_sec % 60)
            millis = int((current_sec - int(current_sec)) * 1000)
            
            time_label = f"{mins:02d}:{secs:02d}"
            filename = f"timeslot_{saved_count+1:03d}_{mins:02d}m{secs:02d}s.{ext}"
            filepath = os.path.join(frames_dir, filename)

            img = frame.to_image()
            if target_width and img.width > target_width:
                aspect = img.height / img.width
                new_h = int(target_width * aspect)
                img = img.resize((target_width, new_h), Image.Resampling.LANCZOS)

            img.save(filepath, format=format_type, quality=quality)
            file_sz = os.path.getsize(filepath)
            total_bytes += file_sz
            saved_count += 1

            extracted_frames.append({
                "index": saved_count,
                "frame_num": i,
                "timestamp_sec": round(current_sec, 2),
                "time_label": time_label,
                "filename": filename,
                "rel_path": f"frames_{int(interval_sec)}s/{filename}",
                "size_kb": round(file_sz / 1024, 1)
            })

    total_mb = total_bytes / (1024 * 1024)
    print(f"[+] Successfully extracted {saved_count} frames! Total size: {total_mb:.2f} MB")

    # Save metadata JSON
    meta = {
        "video_name": os.path.basename(video_path),
        "orig_size_mb": round(os.path.getsize(video_path) / (1024 * 1024), 2),
        "total_extracted_mb": round(total_mb, 2),
        "duration_sec": round(duration, 2),
        "interval_sec": interval_sec,
        "total_frames_extracted": saved_count,
        "frames": extracted_frames
    }

    meta_path = os.path.join(output_base_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    return meta


def create_interactive_viewer(output_base_dir: str, meta: dict):
    """
    Generates a modern, responsive HTML/JS interactive timeslot storyboard player.
    """
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>타임슬롯 비디오 인터랙티브 뷰어 - {meta['video_name']}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;600;700;800&display=swap');
    body {{
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: #0f172a;
      color: #f8fafc;
    }}
    .custom-scrollbar::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    .custom-scrollbar::-webkit-scrollbar-track {{
      background: #1e293b;
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{
      background: #475569;
      border-radius: 3px;
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {{
      background: #64748b;
    }}
    .active-thumb {{
      border-color: #3b82f6 !important;
      transform: scale(1.04);
      box-shadow: 0 0 15px rgba(59, 130, 246, 0.6);
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col">

  <!-- 상단 네비게이션 & 통계 바 -->
  <header class="bg-slate-900/90 backdrop-blur border-b border-slate-800 px-6 py-4 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <i class="fa-solid fa-film text-white text-lg"></i>
        </div>
        <div>
          <h1 class="text-lg font-bold text-white flex items-center gap-2">
            <span>{meta['video_name']}</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              용량 절감 {round((1 - meta['total_extracted_mb']/meta['orig_size_mb']) * 100, 1)}% 🚀
            </span>
          </h1>
          <p class="text-xs text-slate-400">타임슬롯 기반 고화질 프레임 뷰어 (추출 간격: {meta['interval_sec']}초)</p>
        </div>
      </div>

      <!-- 용량 및 통계 배지 -->
      <div class="flex items-center gap-3 text-xs">
        <div class="bg-slate-800/80 border border-slate-700/60 px-3 py-1.5 rounded-lg">
          <span class="text-slate-400">원본 용량:</span>
          <span class="text-rose-400 font-bold ml-1">{meta['orig_size_mb']} MB</span>
        </div>
        <div class="text-slate-500"><i class="fa-solid fa-arrow-right"></i></div>
        <div class="bg-blue-950/60 border border-blue-600/40 px-3 py-1.5 rounded-lg">
          <span class="text-blue-300">타임슬롯 용량:</span>
          <span class="text-emerald-400 font-bold ml-1">{meta['total_extracted_mb']} MB</span>
        </div>
        <div class="bg-slate-800/80 border border-slate-700/60 px-3 py-1.5 rounded-lg">
          <span class="text-slate-400">총 프레임:</span>
          <span class="text-white font-bold ml-1">{meta['total_frames_extracted']}장</span>
        </div>
      </div>
    </div>
  </header>

  <!-- 메인 뷰어 영역 -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 flex flex-col gap-6">

    <!-- 대화면 플레이어 스테이지 -->
    <div class="relative bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col group">
      
      <!-- 메인 이미지 디스플레이 -->
      <div class="relative w-full aspect-video flex items-center justify-center bg-black select-none cursor-ew-resize" id="displayContainer">
        <img id="mainImage" src="{meta['frames'][0]['rel_path']}" alt="Timeslot Frame" class="w-full h-full object-contain transition-opacity duration-75">
        
        <!-- 타임스탬프 오버레이 배지 -->
        <div class="absolute top-4 left-4 bg-black/70 backdrop-blur-md border border-white/10 px-3 py-1.5 rounded-xl flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
          <span id="currentTimestamp" class="font-mono text-sm font-semibold text-white tracking-wider">00:00</span>
          <span class="text-slate-500 text-xs">/</span>
          <span class="text-slate-400 text-xs font-mono">{meta['frames'][-1]['time_label']}</span>
        </div>

        <!-- 프레임 인덱스 & 용량 -->
        <div class="absolute top-4 right-4 bg-black/70 backdrop-blur-md border border-white/10 px-3 py-1.5 rounded-xl text-xs font-mono text-slate-300 flex items-center gap-2">
          <span id="frameCounter">1 / {meta['total_frames_extracted']}</span>
          <span class="text-slate-600">|</span>
          <span id="frameSize" class="text-blue-400">{meta['frames'][0]['size_kb']} KB</span>
        </div>

        <!-- 좌/우 이동 오버레이 버튼 -->
        <button onclick="prevFrame()" class="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/40 hover:bg-blue-600/80 text-white backdrop-blur flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all shadow-lg hover:scale-110">
          <i class="fa-solid fa-chevron-left text-lg"></i>
        </button>
        <button onclick="nextFrame()" class="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/40 hover:bg-blue-600/80 text-white backdrop-blur flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all shadow-lg hover:scale-110">
          <i class="fa-solid fa-chevron-right text-lg"></i>
        </button>
      </div>

      <!-- 타임라인 컨트롤 바 -->
      <div class="bg-slate-900 border-t border-slate-800 p-4 flex flex-col gap-3">
        <!-- 슬라이더 트랙 -->
        <div class="flex items-center gap-3">
          <input type="range" id="frameSlider" min="0" max="{meta['total_frames_extracted'] - 1}" value="0"
            class="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50">
        </div>

        <!-- 버튼 툴바 -->
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-2">
            <!-- 재생 / 일시정지 -->
            <button id="playBtn" onclick="togglePlay()" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold flex items-center gap-2 transition shadow-md shadow-blue-600/20">
              <i class="fa-solid fa-play" id="playIcon"></i>
              <span id="playText">자동 재생</span>
            </button>
            <!-- 이전/다음 -->
            <button onclick="prevFrame()" class="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs transition">
              <i class="fa-solid fa-backward-step"></i>
            </button>
            <button onclick="nextFrame()" class="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs transition">
              <i class="fa-solid fa-forward-step"></i>
            </button>
            <!-- 재생 속도 선택 -->
            <select id="playSpeed" class="bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded-xl px-2.5 py-2 focus:outline-none">
              <option value="1500">0.5x (1.5초)</option>
              <option value="800" selected>1.0x (0.8초)</option>
              <option value="400">2.0x (0.4초)</option>
              <option value="200">4.0x (0.2초)</option>
            </select>
          </div>

          <!-- 보기 모드 및 다운로드 -->
          <div class="flex items-center gap-2 text-xs">
            <button onclick="toggleFullscreen()" class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition flex items-center gap-1.5">
              <i class="fa-solid fa-expand"></i>
              <span>전체화면</span>
            </button>
            <a id="downloadSingleBtn" href="{meta['frames'][0]['rel_path']}" download class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition flex items-center gap-1.5">
              <i class="fa-solid fa-download"></i>
              <span>현재 프레임 저장</span>
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- 하단 타임슬롯 썸네일 그리드 / 타임라인 뷰 -->
    <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col gap-4">
      <div class="flex items-center justify-between">
        <h2 class="text-sm font-bold text-slate-200 flex items-center gap-2">
          <i class="fa-solid fa-table-cells text-blue-400"></i>
          <span>전체 타임슬롯 키프레임 목록 ({meta['total_frames_extracted']}개)</span>
        </h2>
        <span class="text-xs text-slate-400">썸네일을 클릭하면 해당 시간대로 즉시 점프합니다.</span>
      </div>

      <!-- 가로 스크롤 타임라인 썸네일 -->
      <div class="flex gap-3 overflow-x-auto pb-3 custom-scrollbar" id="thumbnailBar">
"""
    for idx, f in enumerate(meta['frames']):
        active_cls = "active-thumb" if idx == 0 else ""
        html_content += f"""
        <div onclick="goToFrame({idx})" class="thumb-card flex-shrink-0 cursor-pointer group flex flex-col gap-1.5 w-36 transition-all duration-200" id="thumb_{idx}">
          <div class="relative rounded-lg overflow-hidden border-2 border-slate-700/80 bg-slate-950 aspect-video group-hover:border-blue-400 transition-all {active_cls}">
            <img src="{f['rel_path']}" loading="lazy" alt="{f['time_label']}" class="w-full h-full object-cover">
            <div class="absolute bottom-1 right-1 bg-black/80 px-1.5 py-0.5 rounded text-[10px] font-mono text-white">
              {f['time_label']}
            </div>
          </div>
          <div class="flex justify-between text-[11px] text-slate-400 font-mono px-0.5">
            <span>#{idx+1:02d}</span>
            <span class="text-slate-500">{f['size_kb']}K</span>
          </div>
        </div>
"""

    html_content += f"""
      </div>
    </div>

  </main>

  <footer class="bg-slate-900 border-t border-slate-800 py-4 px-6 text-center text-xs text-slate-500">
    <p>AI Expert 4-Agent Team Orchestrated • Timeslot Frame Extraction & Optimization System</p>
  </footer>

  <script>
    const frames = {json.dumps(meta['frames'], ensure_ascii=False)};
    let currentIndex = 0;
    let isPlaying = false;
    let playInterval = null;

    const mainImage = document.getElementById('mainImage');
    const currentTimestamp = document.getElementById('currentTimestamp');
    const frameCounter = document.getElementById('frameCounter');
    const frameSize = document.getElementById('frameSize');
    const frameSlider = document.getElementById('frameSlider');
    const playIcon = document.getElementById('playIcon');
    const playText = document.getElementById('playText');
    const playSpeed = document.getElementById('playSpeed');
    const downloadSingleBtn = document.getElementById('downloadSingleBtn');
    const displayContainer = document.getElementById('displayContainer');

    function updateView(idx) {{
      if (idx < 0) idx = 0;
      if (idx >= frames.length) idx = frames.length - 1;
      currentIndex = idx;

      const f = frames[currentIndex];
      mainImage.src = f.rel_path;
      currentTimestamp.innerText = f.time_label;
      frameCounter.innerText = `${{currentIndex + 1}} / ${{frames.length}}`;
      frameSize.innerText = `${{f.size_kb}} KB`;
      frameSlider.value = currentIndex;
      downloadSingleBtn.href = f.rel_path;

      // Update thumbnail active status
      document.querySelectorAll('.thumb-card > div').forEach((el, i) => {{
        if (i === currentIndex) {{
          el.classList.add('active-thumb');
          el.scrollIntoView({{ behavior: 'smooth', inline: 'center', block: 'nearest' }});
        }} else {{
          el.classList.remove('active-thumb');
        }}
      }});
    }}

    function nextFrame() {{
      if (currentIndex < frames.length - 1) {{
        updateView(currentIndex + 1);
      }} else if (isPlaying) {{
        updateView(0); // loop
      }}
    }}

    function prevFrame() {{
      if (currentIndex > 0) {{
        updateView(currentIndex - 1);
      }}
    }}

    function goToFrame(idx) {{
      updateView(idx);
    }}

    function togglePlay() {{
      if (isPlaying) {{
        clearInterval(playInterval);
        isPlaying = false;
        playIcon.className = "fa-solid fa-play";
        playText.innerText = "자동 재생";
      }} else {{
        isPlaying = true;
        playIcon.className = "fa-solid fa-pause";
        playText.innerText = "일시 정지";
        const speed = parseInt(playSpeed.value, 10);
        playInterval = setInterval(nextFrame, speed);
      }}
    }}

    playSpeed.addEventListener('change', () => {{
      if (isPlaying) {{
        clearInterval(playInterval);
        const speed = parseInt(playSpeed.value, 10);
        playInterval = setInterval(nextFrame, speed);
      }}
    }});

    frameSlider.addEventListener('input', (e) => {{
      updateView(parseInt(e.target.value, 10));
    }});

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === ' ') {{
        e.preventDefault();
        nextFrame();
      }} else if (e.key === 'ArrowLeft') {{
        e.preventDefault();
        prevFrame();
      }} else if (e.key === 'k' || e.key === 'K') {{
        togglePlay();
      }}
    }});

    // Drag / Wheel navigation
    let isDragging = false;
    let startX = 0;
    displayContainer.addEventListener('mousedown', (e) => {{
      isDragging = true;
      startX = e.clientX;
    }});
    window.addEventListener('mouseup', () => isDragging = false);
    window.addEventListener('mousemove', (e) => {{
      if (!isDragging) return;
      const diff = e.clientX - startX;
      if (Math.abs(diff) > 20) {{
        if (diff > 0) prevFrame();
        else nextFrame();
        startX = e.clientX;
      }}
    }});

    displayContainer.addEventListener('wheel', (e) => {{
      e.preventDefault();
      if (e.deltaY > 0) nextFrame();
      else prevFrame();
    }}, {{ passive: false }});

    function toggleFullscreen() {{
      if (!document.fullscreenElement) {{
        displayContainer.requestFullscreen().catch(err => alert(err.message));
      }} else {{
        document.exitFullscreen();
      }}
    }}
  </script>
</body>
</html>
"""
    viewer_path = os.path.join(output_base_dir, "timeslot_viewer.html")
    with open(viewer_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[+] Interactive viewer generated: {viewer_path}")
    return viewer_path


def create_zip_archive(output_base_dir: str, zip_filename: str = "timeslot_package.zip"):
    """
    Creates a standalone zip archive of the entire timeslot extraction and viewer.
    """
    zip_path = os.path.join(output_base_dir, zip_filename)
    print(f"[*] Creating ZIP archive: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_base_dir):
            for file in files:
                if file == zip_filename:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_base_dir)
                zipf.write(file_path, arcname)
    zip_sz_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"[+] ZIP created successfully: {zip_sz_mb:.2f} MB")
    return zip_path


def main():
    video_path = "/home/tomkim/다운로드/이듬스튜디오_최종_오프닝_엔딩.mp4"
    output_dir = "/home/tomkim/다운로드/이듬스튜디오_타임슬롯_분산추출"
    
    # 3초 간격 추출 실행
    meta = extract_timeslot(
        video_path=video_path,
        output_base_dir=output_dir,
        interval_sec=3.0,
        target_width=1920,
        quality=82,
        format_type="WEBP"
    )
    
    # HTML 인터랙티브 뷰어 생성
    create_interactive_viewer(output_dir, meta)
    
    # ZIP 패키지 생성
    create_zip_archive(output_dir, "이듬스튜디오_타임슬롯_패키지.zip")
    
    print("\n" + "="*60)
    print("✨ All tasks completed successfully!")
    print(f"📁 Output Directory: {output_dir}")
    print(f"🌐 HTML Viewer: {os.path.join(output_dir, 'timeslot_viewer.html')}")
    print(f"📦 ZIP Archive: {os.path.join(output_dir, '이듬스튜디오_타임슬롯_패키지.zip')}")
    print("="*60)

if __name__ == "__main__":
    main()
