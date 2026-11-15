#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timbr 공식 문서 5대 섹션 전체 수집 및 NotebookLM용 단일 Markdown 통합 스크립트
대상 섹션:
1. Getting Started (/doc/docs/getting-started/)
2. Timbr Platform (/doc/docs/platform/)
3. SQL Reference (/doc/docs/sql/)
4. API (/doc/docs/api/)
5. Integrations (/doc/docs/integration/)
"""

import os
import sys
import time
import re
from urllib.parse import urljoin, urldefrag, urlparse
from collections import deque
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import html2text

# 수집 대상 섹션 접두어 정의
TARGET_SECTIONS = [
    {
        "name": "Getting Started",
        "url": "https://docs.timbr.ai/doc/docs/getting-started/intro-timbr",
        "prefix": "/doc/docs/getting-started"
    },
    {
        "name": "Timbr Platform",
        "url": "https://docs.timbr.ai/doc/docs/platform/",
        "prefix": "/doc/docs/platform"
    },
    {
        "name": "SQL Reference",
        "url": "https://docs.timbr.ai/doc/docs/sql/",
        "prefix": "/doc/docs/sql"
    },
    {
        "name": "API",
        "url": "https://docs.timbr.ai/doc/docs/api/",
        "prefix": "/doc/docs/api"
    },
    {
        "name": "Integrations",
        "url": "https://docs.timbr.ai/doc/docs/integration/",
        "prefix": "/doc/docs/integration"
    }
]

EXCLUDED_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
    '.pdf', '.zip', '.tar', '.gz', '.mp4', '.css', '.js'
}


def normalize_url(url: str) -> str:
    clean, _ = urldefrag(url)
    return clean.rstrip('/')


def is_target_url(url: str) -> bool:
    try:
        p = urlparse(url)
    except Exception:
        return False

    if p.netloc.lower() != 'docs.timbr.ai':
        return False

    path_lower = p.path.lower()
    for ext in EXCLUDED_EXTENSIONS:
        if path_lower.endswith(ext):
            return False

    # 5대 섹션 중 하나에 속하는지 확인
    for sec in TARGET_SECTIONS:
        if path_lower.startswith(sec["prefix"].lower()):
            return True
    return False


def get_section_name(url: str) -> str:
    path_lower = urlparse(url).path.lower()
    for sec in TARGET_SECTIONS:
        if path_lower.startswith(sec["prefix"].lower()):
            return sec["name"]
    return "General"


def extract_clean_content(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, 'html.parser')

    # 타이틀 추출
    title = ""
    if soup.find('h1'):
        title = soup.find('h1').get_text().strip()
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()
    if not title:
        title = "Untitled Document"

    # 불필요한 태그 제거
    for tag in soup.find_all(['script', 'style', 'noscript', 'nav', 'header', 'footer', 'aside', 'iframe', 'svg']):
        tag.decompose()

    # Docusaurus 본문 영역 탐색
    content_candidate = (
        soup.find('article') or
        soup.find('div', class_=re.compile(r'(markdown|theme-doc-markdown)', re.I)) or
        soup.find('main') or
        soup.body
    )

    if not content_candidate:
        return title, ""

    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.images_to_alt = True
    converter.body_width = 0  # 자동 줄바꿈 해제
    converter.unicode_snob = True
    converter.protect_links = True
    converter.ignore_emphasis = False

    md = converter.handle(str(content_candidate)).strip()
    return title, md


def main():
    print("=" * 70)
    print("🚀 Timbr 기술 문서 5대 섹션 수집 및 단일 NotebookLM 마크다운 생성기")
    print("   1) Getting Started")
    print("   2) Timbr Platform")
    print("   3) SQL Reference")
    print("   4) API")
    print("   5) Integrations")
    print("=" * 70)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })

    # 탐색 큐 및 방문 기록
    queue = deque()
    visited = set()

    # 시작점 추가
    for sec in TARGET_SECTIONS:
        norm = normalize_url(sec["url"])
        queue.append(norm)
        visited.add(norm)

    # 또한 doc 메인 페이지도 탐색하여 모든 하위 링크 긁어오기
    doc_root = "https://docs.timbr.ai/doc/"
    try:
        r_root = session.get(doc_root, timeout=15)
        soup_root = BeautifulSoup(r_root.text, 'html.parser')
        for a in soup_root.find_all('a', href=True):
            cand = normalize_url(urljoin(doc_root, a['href']))
            if is_target_url(cand) and cand not in visited:
                visited.add(cand)
                queue.append(cand)
    except Exception as e:
        print(f"⚠️ 루트 페이지 탐색 중 참고: {e}")

    crawled_pages = []  # dict: {section, title, url, md}
    count = 0

    print(f"\n총 {len(queue)}개 시작 URL로 탐색을 시작합니다...\n")

    while queue:
        url = queue.popleft()
        count += 1
        sec_name = get_section_name(url)
        print(f"[{count:02d}] [{sec_name}] 수집 중: {url}")

        try:
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"    ⚠️ HTTP {resp.status_code} -> 스킵")
                continue

            content_type = resp.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                continue

            if resp.encoding is None or resp.encoding == 'ISO-8859-1':
                resp.encoding = resp.apparent_encoding or 'utf-8'

            raw_html = resp.text
            soup = BeautifulSoup(raw_html, 'html.parser')

            # 사이드바 및 페이지 내부 링크 수집 (다음 탐색 대상)
            new_links = 0
            for a_tag in soup.find_all('a', href=True):
                abs_link = normalize_url(urljoin(url, a_tag['href']))
                if is_target_url(abs_link) and abs_link not in visited:
                    visited.add(abs_link)
                    queue.append(abs_link)
                    new_links += 1

            # 본문 추출 및 마크다운 변환
            title, md_content = extract_clean_content(raw_html)
            if md_content:
                crawled_pages.append({
                    "section": sec_name,
                    "title": title,
                    "url": url,
                    "md": md_content
                })
                print(f"    ✅ 본문 변환 완료 ({len(md_content)}자, 신규 링크 +{new_links}개)")
            else:
                print(f"    ⚠️ 본문 내용 없음 -> 스킵")

            time.sleep(0.15)  # 서버 부하 방지

        except Exception as err:
            print(f"    ❌ 오류 발생: {err}")

    # 섹션별 정렬
    section_order = {
        "Getting Started": 1,
        "Timbr Platform": 2,
        "SQL Reference": 3,
        "API": 4,
        "Integrations": 5,
        "General": 6
    }
    crawled_pages.sort(key=lambda x: (section_order.get(x["section"], 99), x["title"]))

    # 단일 NotebookLM용 마크다운 파일 작성
    output_filename = "/home/hanginthomaskim/mywork/skill/Timbr_Complete_Documentation_NotebookLM.md"
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    print("\n" + "=" * 70)
    print(f"📝 총 {len(crawled_pages)}건의 문서를 단일 파일로 병합 생성 중...")

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(output_filename, 'w', encoding='utf-8') as f:
        # 헤더
        f.write("# Timbr Complete Documentation (for NotebookLM)\n\n")
        f.write(f"> - **수집 대상**: Getting Started, Timbr Platform, SQL Reference, API, Integrations\n")
        f.write(f"> - **기준 URL**: https://docs.timbr.ai/doc/\n")
        f.write(f"> - **수집 일시**: {now_str}\n")
        f.write(f"> - **총 수집 문서 수**: {len(crawled_pages)}개 문서\n\n")
        f.write("---\n\n")

        # 목차 (Table of Contents)
        f.write("## 📑 Table of Contents (목차)\n\n")
        current_sec = None
        for i, page in enumerate(crawled_pages, 1):
            if page["section"] != current_sec:
                current_sec = page["section"]
                f.write(f"\n### 📁 {current_sec}\n\n")
            anchor = re.sub(r'[^a-zA-Z0-9가-힣_-]', '', page["title"].lower().replace(' ', '-'))
            f.write(f"{i}. [{page['title']}](#doc-{i}-{anchor})  *(원문: {page['url']})*\n")

        f.write("\n\n" + "=" * 60 + "\n\n")

        # 본문 병합
        current_sec = None
        for i, page in enumerate(crawled_pages, 1):
            if page["section"] != current_sec:
                current_sec = page["section"]
                f.write(f"\n\n# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                f.write(f"# SECTION: {current_sec.upper()}\n")
                f.write(f"# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

            anchor = re.sub(r'[^a-zA-Z0-9가-힣_-]', '', page["title"].lower().replace(' ', '-'))
            f.write(f"<a id=\"doc-{i}-{anchor}\"></a>\n\n")
            f.write(f"## [{i}] {page['title']}\n\n")
            f.write(f"- **분류 (Section)**: {page['section']}\n")
            f.write(f"- **출처 (URL)**: [{page['url']}]({page['url']})\n\n")
            f.write(f"{page['md']}\n\n")
            f.write("\n---\n\n")

    print(f"🎉 성공적으로 파일이 생성되었습니다!")
    print(f"👉 파일 위치: {output_filename}")
    print(f"👉 파일 크기: {os.path.getsize(output_filename):,} 바이트")
    print("=" * 70)


if __name__ == "__main__":
    main()
