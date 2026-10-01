import urllib.request
import ssl
import os
import re
import urllib.parse
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def decode_filename(raw_str):
    if not raw_str:
        return "downloaded_file"
    raw_str = raw_str.strip('"\'; ')
    # Try RFC 5987 / URL unquote
    try:
        if raw_str.startswith("UTF-8''"):
            raw_str = raw_str[7:]
        decoded = urllib.parse.unquote(raw_str)
        # Check if it was double-encoded as latin1/iso-8859-1 representation of utf-8
        try:
            latin_bytes = decoded.encode("latin1")
            decoded_utf8 = latin_bytes.decode("utf-8")
            return decoded_utf8
        except Exception:
            return decoded
    except Exception:
        return raw_str

def download_bizinfo_files(pblanc_id, prefix_label=""):
    url = f"https://www.bizinfo.go.kr/sii/siia/selectSIIA200Detail.do?pblancId={pblanc_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return

    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.find("h2") or soup.find("h3") or soup.find("title")
    title_text = title_el.get_text(strip=True) if title_el else pblanc_id
    print(f"\n==================================================")
    print(f"[{prefix_label}] 공고명: {title_text}")
    print(f"URL: {url}")
    print(f"==================================================")

    # Save summary text as well
    summary_file = f"{prefix_label}_공고개요.txt"
    desc_el = soup.select_one(".view_cont") or soup.select_one("#contents") or soup.select_one("body")
    if desc_el:
        with open(summary_file, "w", encoding="utf-8") as sf:
            sf.write(f"공고명: {title_text}\n원문링크: {url}\n\n")
            sf.write(desc_el.get_text("\n", strip=True))
        print(f"  -> 공고 상세 안내 텍스트 저장 완료: {summary_file}")

    # find file links
    links = []
    for a in soup.select("a[href*='fileDown.do']"):
        href = a["href"]
        links.append(href)
    
    if not links:
        print(f"No direct fileDown links found for {pblanc_id}")
        return

    for href in set(links):
        file_url = "https://www.bizinfo.go.kr" + href if href.startswith("/") else href
        try:
            freq = urllib.request.Request(file_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(freq, context=ctx, timeout=30) as fresp:
                disp = fresp.headers.get("Content-Disposition", "")
                fname = f"{prefix_label}_첨부파일.bin"
                if "filename=" in disp or "filename*=" in disp:
                    m = re.search(r"filename\*?=(?:UTF-8\'\')?\"?([^;\"]+)\"?", disp)
                    if m:
                        fname = decode_filename(m.group(1))
                
                fname = re.sub(r'[\\/*?:"<>|]', "", fname)
                final_fname = f"{prefix_label}_{fname}"
                with open(final_fname, "wb") as out:
                    out.write(fresp.read())
                print(f"  -> 파일 다운로드 완료: {final_fname} ({os.path.getsize(final_fname):,} bytes)")
        except Exception as fe:
            print(f"  -> Error downloading {file_url}: {fe}")

# Remove old files with corrupted names
for f in os.listdir("."):
    if f.startswith("ì") or f.startswith("(ê"):
        try:
            os.remove(f)
        except Exception:
            pass

# 1. 창업성장기술개발사업(디딤돌)
download_bizinfo_files("PBLN_000000000107184", "01_창업성장기술개발_디딤돌")

# 2. TIPS (팁스 창업기업 지원계획)
download_bizinfo_files("PBLN_000000000093595", "02_TIPS_프로그램")

# 3. KIRIA 서비스로봇 실증사업
download_bizinfo_files("PBLN_000000000120052", "03_KIRIA_지능형로봇실증")

