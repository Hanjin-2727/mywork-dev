#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3TierMD.py - 기술 문서 웹사이트 3계층 크롤링 및 Markdown 변환기
NotebookLM에 입력하기에 최적화된 형태로 최대 3계층까지 문서를 수집하여 MD 파일로 생성합니다.
"""

import os
import sys
import time
import re
import argparse
from urllib.parse import urlparse, urljoin, urldefrag
from collections import deque
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
    import html2text
except ImportError as e:
    print(f"[오류] 필수 라이브러리가 설치되어 있지 않습니다: {e}")
    print("다음 명령어로 설치해주세요: pip install requests beautifulsoup4 html2text")
    sys.exit(1)


# 기술문서 외 불필요한 바이너리/미디어 파일 확장자 필터
EXCLUDED_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
    '.pdf', '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
    '.exe', '.dmg', '.iso', '.bin',
    '.mp4', '.webm', '.avi', '.mov', '.mp3', '.wav',
    '.css', '.js', '.json', '.xml', '.wasm', '.map'
}


def sanitize_filename(name: str, max_length: int = 80) -> str:
    """파일명으로 사용할 수 없는 특수문자 제거 및 길이 제한"""
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    name = re.sub(r'\s+', '_', name).strip('._ ')
    if not name:
        name = "untitled"
    return name[:max_length]


def normalize_url(url: str) -> str:
    """URL에서 해시(#anchor)를 제거하고 정규화"""
    clean_url, _ = urldefrag(url)
    return clean_url.rstrip('/')


def get_doc_root_path(url: str) -> str:
    """기술문서 URL에서 문서의 루트 경로를 스마트하게 추출"""
    parsed = urlparse(url)
    path = parsed.path.rstrip('/')
    
    # docs.xxx.com 과 같이 호스트 자체가 문서 서브도메인인 경우
    if parsed.netloc.lower().startswith(('docs.', 'doc.')):
        # 만약 /doc/docs 나 /docs 같은 공통 접두어가 있다면 해당 접두어를 루트로 지정
        for common_prefix in ['/doc/docs', '/docs', '/doc', '/manual', '/guide']:
            idx = path.lower().find(common_prefix)
            if idx != -1:
                return path[:idx + len(common_prefix)]
        return ""  # 서브도메인 전체를 문서 루트로 간주

    # 일반 도메인에서 기술문서 공통 접두어 탐색
    for common_prefix in ['/doc/docs', '/docs', '/doc', '/guide', '/manual', '/tutorial', '/book']:
        idx = path.lower().find(common_prefix)
        if idx != -1:
            return path[:idx + len(common_prefix)]

    # 접두어가 없으면 파일명 제외한 상위 디렉터리 반환
    if '.' in os.path.basename(path):
        return os.path.dirname(path)
    return path


def is_valid_doc_url(url: str, base_netloc: str, base_path: str = "", strict_prefix: bool = False) -> bool:
    """유효한 기술 문서 URL인지 확인 (도메인 범위, 확장자, 프로토콜 검사)"""
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # http / https 프로토콜만 수집
    if parsed.scheme not in ('http', 'https'):
        return False

    # 동일 도메인(호스트) 검사
    if parsed.netloc.lower() != base_netloc.lower():
        return False

    # 엄격 경로 제한이 켜져 있을 때만 접두어 검사
    if strict_prefix and base_path:
        parsed_path = parsed.path.rstrip('/')
        clean_base_path = base_path.rstrip('/')
        if clean_base_path and not parsed_path.startswith(clean_base_path):
            return False

    # 불필요한 확장자 필터링
    path_lower = parsed.path.lower()
    for ext in EXCLUDED_EXTENSIONS:
        if path_lower.endswith(ext):
            return False

    return True


def clean_html_content(soup: BeautifulSoup) -> BeautifulSoup:
    """기술문서 본문 이외의 내비게이션, 헤더, 푸터, 스크립트 등 불필요 태그 제거"""
    # 제거 대상 태그
    unwanted_tags = [
        'script', 'style', 'noscript', 'iframe', 'svg',
        'nav', 'header', 'footer', 'aside',
        'form', 'button', 'input'
    ]
    for tag in soup.find_all(unwanted_tags):
        tag.decompose()

    # 기술문서 흔한 본문 영역 우선 탐색 (Docusaurus, GitBook, MkDocs, Sphinx 등)
    content_candidates = [
        soup.find('main'),
        soup.find('article'),
        soup.find('div', {'role': 'main'}),
        soup.find('div', class_=re.compile(r'(markdown-body|content|theme-doc-markdown|document|post-content|article-content)', re.I)),
        soup.find('div', id=re.compile(r'(content|main|article)', re.I)),
    ]

    for candidate in content_candidates:
        if candidate:
            return candidate

    return soup.body if soup.body else soup


def html_to_markdown(html_content: str) -> str:
    """HTML을 정돈된 Markdown 텍스트로 변환"""
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.images_to_alt = True
    converter.body_width = 0  # 코드 블록/문단 자동 줄바꿈 비활성화 (NotebookLM 가독성 최적화)
    converter.unicode_snob = True
    converter.protect_links = True
    converter.ignore_emphasis = False

    return converter.handle(html_content).strip()


def crawl_and_export_3tier(
    start_url: str,
    output_dir: str = "output_3tier_md",
    max_depth: int = 3,
    delay: float = 0.3,
    strict_prefix: bool = True
):
    """
    BFS(너비 우선 탐색)로 시작 URL부터 max_depth(기본 3계층)까지 기술 문서를 크롤링하여
    각 계층별 MD 파일 및 NotebookLM 업로드용 단일 병합 MD 파일을 생성합니다.
    """
    parsed_start = urlparse(start_url)
    if not parsed_start.scheme or not parsed_start.netloc:
        print(f"[오류] 잘못된 URL 형식입니다: {start_url}")
        return

    base_netloc = parsed_start.netloc
    base_path = get_doc_root_path(start_url)

    # 출력 디렉터리 생성
    os.makedirs(output_dir, exist_ok=True)
    for d in range(1, max_depth + 1):
        os.makedirs(os.path.join(output_dir, f"tier_{d}"), exist_ok=True)

    session = requests.Session()
    session.headers.update({
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 NotebookLM-Ingest/1.0'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    })

    start_url_norm = normalize_url(start_url)
    # 큐: (url, current_tier)
    queue = deque([(start_url_norm, 1)])
    visited = {start_url_norm}

    crawled_results = []  # [(tier, title, url, filepath, md_content)]
    total_processed = 0

    print("=" * 65)
    print(f"🚀 [3TierMD] 기술문서 수집 시작")
    print(f" - 시작 URL: {start_url_norm}")
    print(f" - 도메인: {base_netloc}")
    print(f" - 최대 수집 계층: {max_depth}계층")
    print(f" - 경로 엄격 제한: {'활성화' if strict_prefix else '비활성화 (도메인 전체)'}")
    print(f" - 저장 폴더: {os.path.abspath(output_dir)}")
    print("=" * 65)

    while queue:
        current_url, current_tier = queue.popleft()
        total_processed += 1
        print(f"[{total_processed}] [Tier {current_tier}/{max_depth}] 수집 중: {current_url}")

        try:
            resp = session.get(current_url, timeout=15)
            # HTML 컨텐츠만 처리
            content_type = resp.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                print(f"    ⏭️ HTML 문서가 아님 ({content_type}) -> 스킵")
                continue

            if resp.status_code != 200:
                print(f"    ⚠️ HTTP {resp.status_code} 오류 -> 스킵")
                continue

            # 인코딩 처리
            if resp.encoding is None or resp.encoding == 'ISO-8859-1':
                resp.encoding = resp.apparent_encoding or 'utf-8'

            soup = BeautifulSoup(resp.text, 'html.parser')

            # 문서 제목 추출
            title = ""
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.find('h1'):
                title = soup.find('h1').get_text().strip()
            if not title:
                title = os.path.basename(urlparse(current_url).path) or "Untitled"

            # 링크 추출 (다음 계층 탐색용: current_tier < max_depth 인 경우)
            discovered_links = []
            if current_tier < max_depth:
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href'].strip()
                    abs_url = normalize_url(urljoin(current_url, href))

                    if abs_url not in visited and is_valid_doc_url(abs_url, base_netloc, base_path, strict_prefix):
                        visited.add(abs_url)
                        queue.append((abs_url, current_tier + 1))
                        discovered_links.append(abs_url)

            # 불필요 요소 제거 후 본문 영역 추출
            cleaned_soup = clean_html_content(soup)
            md_body = html_to_markdown(str(cleaned_soup))

            # MD 파일 상단 메타데이터 구성 (NotebookLM 참조용)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            md_doc = f"""# {title}

- **출처 URL**: [{current_url}]({current_url})
- **계층 (Tier)**: {current_tier}
- **수집 일시**: {timestamp}

---

{md_body}
"""
            # 개별 MD 파일 저장
            safe_title = sanitize_filename(f"t{current_tier}_{total_processed:03d}_{title}")
            filename = f"{safe_title}.md"
            filepath = os.path.join(output_dir, f"tier_{current_tier}", filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_doc)

            crawled_results.append((current_tier, title, current_url, filepath, md_doc))
            print(f"    ✅ 저장 완료: {filepath} (다음 계층 링크 {len(discovered_links)}개 발견)")

            if delay > 0:
                time.sleep(delay)

        except requests.exceptions.RequestException as req_err:
            print(f"    ❌ 요청 실패: {req_err}")
        except Exception as err:
            print(f"    ❌ 처리 오류: {err}")

    # 크롤링 완료 후 통합 파일 및 인덱스 생성
    print("\n" + "=" * 65)
    print("📊 수집 완료 및 NotebookLM 통합 파일 생성 중...")

    # 1. 목차(Index) 파일 생성
    index_path = os.path.join(output_dir, "INDEX.md")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(f"# 기술문서 크롤링 인덱스 (총 {len(crawled_results)}개 문서)\n\n")
        f.write(f"- **시작 URL**: {start_url}\n")
        f.write(f"- **수집 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **계층 구조**: 최대 {max_depth}계층\n\n")
        f.write("## 문서 목록\n\n")

        for tier in range(1, max_depth + 1):
            tier_docs = [doc for doc in crawled_results if doc[0] == tier]
            f.write(f"### 📂 Tier {tier} ({len(tier_docs)}개 문서)\n\n")
            for _, title, url, path, _ in tier_docs:
                rel_path = os.path.relpath(path, output_dir)
                f.write(f"- [{title}]({rel_path}) - [원문 링크]({url})\n")
            f.write("\n")

    # 2. NotebookLM 전용 단일 병합 파일 생성 (NotebookLM은 단일 대용량 파일 업로드 시 일관된 검색에 매우 유리)
    combined_path = os.path.join(output_dir, "NOTEBOOKLM_COMBINED_ALL_TIERS.md")
    with open(combined_path, 'w', encoding='utf-8') as f:
        f.write(f"# 기술 문서 전체 모음집 (NotebookLM 전용)\n\n")
        f.write(f"> 기준 URL: {start_url}\n")
        f.write(f"> 총 수집 문서: {len(crawled_results)}건\n\n")
        f.write("===\n\n")

        for idx, (tier, title, url, _, md_content) in enumerate(crawled_results, 1):
            f.write(f"\n\n<!-- DOCUMENT START: [{idx}] {title} (Tier {tier}) -->\n")
            f.write(md_content)
            f.write(f"\n\n<!-- DOCUMENT END: [{idx}] -->\n")
            f.write("\n---\n")

    print(f"✨ 작업이 모두 완료되었습니다!")
    print(f" - 총 수집 문서 수: {len(crawled_results)}개")
    print(f" - 계층별 개별 파일: {output_dir}/tier_1/, tier_2/, tier_3/")
    print(f" - 전체 목차 파일: {index_path}")
    print(f" - NotebookLM 원클릭 업로드용 통합 파일: {combined_path}")
    print("=" * 65)


def prompt_interactive_inputs():
    """사용자에게 단계별로 질문하여 크롤링 설정값을 입력받는 대화형(문답식) 함수"""
    print("=" * 65)
    print("  📚 NotebookLM 기술 문서 3계층 Markdown 추출기 (3TierMD)")
    print("=" * 65)
    print("대화형 문답 모드로 실행됩니다. 질문에 답변을 입력해 주세요.")
    print("(대괄호 [ ] 안의 값은 아무것도 입력하지 않고 Enter를 쳤을 때의 기본값입니다.)\n")

    # 1. URL 입력
    target_url = ""
    while not target_url:
        try:
            target_url = input("👉 [1/4] 🌐 수집할 기술 문서 URL을 입력해 주세요:\n   > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n작업이 취소되었습니다.")
            sys.exit(0)

        if not target_url:
            print("   ⚠️ URL은 필수 입력값입니다. 다시 입력해 주세요.\n")

    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    parsed = urlparse(target_url)
    domain_clean = sanitize_filename(parsed.netloc.replace(':', '_'))

    # 2. 계층 깊이
    max_depth = 3
    depth_input = input(f"\n👉 [2/4] 📑 탐색할 최대 계층 깊이를 입력해 주세요 [기본값: 3계층]:\n   > ").strip()
    if depth_input:
        try:
            val = int(depth_input)
            if val >= 1:
                max_depth = val
        except ValueError:
            print("   ⚠️ 숫자가 아니므로 기본값(3계층)으로 진행합니다.")

    # 3. 저장 디렉토리명
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    default_output = f"output_3tier_{domain_clean}_{timestamp}"
    output_dir_input = input(f"\n👉 [3/4] 📁 저장할 폴더명을 입력해 주세요 [기본값: {default_output}]:\n   > ").strip()
    output_dir = output_dir_input if output_dir_input else default_output

    # 4. 수집 범위 설정
    print("\n👉 [4/4] 🌐 수집 범위를 선택해 주세요:")
    print("   1) 도메인 내 모든 관련 기술 문서 수집 (추천: 가이드, API, 튜토리얼 등 전체 포함)")
    print("   2) 시작 URL의 하위 경로만 엄격히 수집 (특정 소챕터 폴더만 한정)")
    scope_input = input("   선택 번호 입력 [기본값: 1]: ").strip()
    strict_prefix = True if scope_input == '2' else False

    print("\n" + "-" * 65)
    print("📋 [입력 확인]")
    print(f" - 시작 URL: {target_url}")
    print(f" - 탐색 깊이: {max_depth}계층")
    print(f" - 저장 폴더: {os.path.abspath(output_dir)}")
    print(f" - 수집 범위: {'하위 특정 폴더만 엄격 수집' if strict_prefix else '사이트 내 전체 기술 문서 수집 (권장)'}")
    print("-" * 65 + "\n")

    return target_url, output_dir, max_depth, 0.2, strict_prefix


def main():
    parser = argparse.ArgumentParser(
        description="기술 문서 사이트를 최대 3계층까지 탐색하여 NotebookLM용 Markdown 파일로 저장합니다."
    )
    parser.add_argument("url", nargs="?", default=None, help="수집할 기술 문서의 시작 URL (생략 시 문답식 모드로 실행)")
    parser.add_argument(
        "-d", "--depth", type=int, default=3,
        help="탐색할 최대 계층 깊이 (기본값: 3)"
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="Markdown 파일을 저장할 디렉터리 경로 (기본값: ./output_3tier_<도메인>_<일시>)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.2,
        help="요청 간 딜레이(초) - 서버 부하 방지 (기본값: 0.2)"
    )
    parser.add_argument(
        "--no-strict-prefix", action="store_true",
        help="하위 경로 제한을 해제하고 동일 도메인 전체를 수집 대상에 포함"
    )

    args = parser.parse_args()

    # 인자 없이 실행되거나 URL이 없으면 문답식 대화형 모드 실행
    if not args.url:
        target_url, output_dir, max_depth, delay, strict_prefix = prompt_interactive_inputs()
    else:
        target_url = args.url
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url

        if not args.output:
            netloc = urlparse(target_url).netloc.replace(':', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = f"output_3tier_{sanitize_filename(netloc)}_{timestamp}"
        else:
            output_dir = args.output

        max_depth = args.depth
        delay = args.delay
        strict_prefix = not args.no_strict_prefix

    crawl_and_export_3tier(
        start_url=target_url,
        output_dir=output_dir,
        max_depth=max_depth,
        delay=delay,
        strict_prefix=strict_prefix
    )


if __name__ == "__main__":
    main()

