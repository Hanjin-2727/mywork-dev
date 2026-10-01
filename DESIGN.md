# DESIGN.md

> **디자인 시스템 명세서 (Design System Specification)**
> **핵심 원칙: 순백색 배경 기반 + 3색 엄격 통제 + 단일 블루 하이라이트 시스템**

---

## 1. 📌 핵심 디자인 3대 불변 규칙 (Core Immutable Rules)

1. **배경은 무조건 '순백색(#FFFFFF)'만 사용**
   - 페이지 전체 배경, 대시보드, 모달, 카드, 폼 등 모든 캔버스 배경은 예외 없이 순백색(`#FFFFFF`)으로 통일합니다.
   - 어두운 배경, 그라데이션 배경, 유채색 배경을 일체 금지합니다.

2. **시스템 전체 색상은 '단 3가지'로만 엄격히 통제**
   - 시스템 내에서 허용되는 색상은 **① 흰색(배경), ② 검정색(콘텐츠/텍스트), ③ 파란색(하이라이트)** 3가지뿐입니다.
   - 빨강, 노랑, 초록 등 다른 유채색을 임의로 추가할 수 없습니다.
   - 별도의 회색 헥스 코드(예: `#e5e7eb`, `#9ca3af`)를 새로 생성하지 않으며, 계층 표현은 오직 **검정색(`#000000`)의 투명도(Alpha)**만 사용합니다.

3. **파란색(Accent)은 '하이라이트 및 액션 포인터'에만 독점 사용**
   - 파란색은 사용자의 시선이 즉각 꽂혀야 하는 **주요 CTA 버튼, 활성(Active) 메뉴, 인풋 포커스 링, 링크, 핵심 강조 지표**에만 제한적으로 사용합니다.
   - 넓은 면적의 배경이나 단순 장식용으로 남용하지 않습니다.

---

## 2. 🎨 3색 팔레트 토큰 정의 (Color Palette)

| 역할 (Role) | 색상명 | Hex Code | 시각적 비중 | 적용 위치 |
| :--- | :--- | :--- | :--- | :--- |
| **기본 배경 (Canvas)** | Pure White | `#FFFFFF` | **~60%** | 모든 페이지 배경, 카드 컨테이너, 모달, 팝오버 |
| **콘텐츠 (Ink)** | Pitch Black | `#000000` | **~30%** | 타이틀, 본문 텍스트, 아이콘, 1px 구조적 외곽선 |
| **하이라이트 (Accent)** | Electric Indigo/Blue | `#635BFF` *(또는 #0070F3)* | **~10%** | 메인 액션 버튼(CTA), 활성 탭, 포커스 링, 핵심 지표 |

### 🔍 검정 투명도 체계 (Alpha Modifiers - 추가 색상 생성 방지)
회색 색상을 새로 추가하지 않고, 검정색 투명도만으로 깊이감을 형성합니다:
- **본문 기본 텍스트 (Primary Text)**: `#000000` (`opacity: 0.90`)
- **보조/설명 텍스트 (Muted Text)**: `rgba(0, 0, 0, 0.60)`
- **플레이스홀더/비활성 (Disabled)**: `rgba(0, 0, 0, 0.35)`
- **기본 경계선/구분선 (Border/Divider)**: `rgba(0, 0, 0, 0.12)`
- **미세 인터랙션 배경 (Hover Surface)**: `rgba(0, 0, 0, 0.04)`

---

## 3. 🔤 타이포그래피 (Typography)

* **기본 폰트 (한글/영문 통합)**: `"Pretendard"`, `"Inter"`, `-apple-system`, `BlinkMacSystemFont`, `"Segoe UI"`, `sans-serif`
  > **안내**: `Inter`는 영문 전용이므로, 한글 환경에서는 영문 Inter와 1:1 매칭되는 **`Pretendard`**를 최우선 적용합니다.
* **코드 / 고정폭 (Code)**: `"JetBrains Mono"`, `"Fira Code"`, `monospace`

| 계층 | 크기 (Size) | 굵기 (Weight) | 자간/행간 | 색상 (Color) |
| :--- | :--- | :--- | :--- | :--- |
| **H1 (페이지 제목)** | `28px ~ 36px` | `700 (Bold)` | `line-height: 1.25` | `#000000` |
| **H2 (섹션 제목)** | `20px ~ 24px` | `700 (Bold)` | `line-height: 1.3` | `#000000` |
| **H3 (카드/모듈 제목)**| `16px ~ 18px` | `600 (SemiBold)` | `line-height: 1.4` | `#000000` |
| **Body (본문)** | `14px ~ 15px` | `400 (Regular)` | `line-height: 1.5` | `rgba(0, 0, 0, 0.88)` |
| **Caption (설명/캡션)**| `12px ~ 13px` | `400 (Regular)` | `line-height: 1.4` | `rgba(0, 0, 0, 0.60)` |
| **Highlight (강조 문구)**| `14px ~ 15px` | `600 (SemiBold)` | `line-height: 1.5` | `var(--accent)` (파란색) |

---

## 4. 🧩 컴포넌트별 적용 가이드 (Component Specs)

### ① 버튼 (Buttons)
* **메인 CTA 버튼 (Primary Button - 하이라이트)**
  * 배경: `#635BFF` (단일 파란색)
  * 글자: `#FFFFFF` (순백색)
  * 테두리: `none`
  * 호버 상태: `filter: brightness(0.92)`
  * 포커스 상태: `outline: 2px solid #635BFF`, `outline-offset: 2px`
* **보조 버튼 (Secondary / Outline Button)**
  * 배경: `#FFFFFF`
  * 글자: `#000000`
  * 테두리: `1px solid rgba(0, 0, 0, 0.15)`
  * 호버 상태: `background-color: rgba(0, 0, 0, 0.04)`

### ② 카드 및 컨테이너 (Cards & Surfaces)
* 배경: `#FFFFFF` (순백색)
* 테두리: `1px solid rgba(0, 0, 0, 0.10)`
* 그림자: `none` 또는 극도로 은은한 그림자 `0 1px 3px rgba(0, 0, 0, 0.05)`
* 활성/선택된 카드: 테두리 색상이 `#635BFF`로 전환되어 인터랙션 표시

### ③ 입력 폼 (Form Inputs)
* 배경: `#FFFFFF`
* 텍스트: `#000000`
* 기본 테두리: `1px solid rgba(0, 0, 0, 0.20)`
* **포커스 링 (Focus State)**: `border-color: #635BFF`, `box-shadow: 0 0 0 3px rgba(99, 91, 255, 0.15)`

### ④ 상태 뱃지 및 링크 (Badges & Links)
* **Active / High-priority Badge**:
  * 텍스트: `#635BFF`
  * 테두리: `1px solid #635BFF`
  * 배경: `transparent` (또는 `rgba(99, 91, 255, 0.08)`)
* **일반 텍스트 링크**:
  * 기본 텍스트 색상 `#000000` 유지, 호버 시 파란색(`#635BFF`)으로 전환

---

## 5. 💻 코드 템플릿 (Implementation Snippets)

### CSS Variables (`:root`)
```css
:root {
  /* Strict 3-Color Tokens */
  --bg-base: #FFFFFF;        /* 1. 흰색 배경 */
  --text-primary: #000000;   /* 2. 검정 콘텐츠 */
  --accent: #635BFF;         /* 3. 파란색 하이라이트 */

  /* Black Alpha Hierarchy */
  --text-muted: rgba(0, 0, 0, 0.60);
  --border-subtle: rgba(0, 0, 0, 0.12);
  --hover-subtle: rgba(0, 0, 0, 0.04);
  --accent-focus-ring: rgba(99, 91, 255, 0.15);

  /* Typography */
  --font-sans: "Pretendard", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

body {
  background-color: var(--bg-base);
  color: var(--text-primary);
  font-family: var(--font-sans);
  margin: 0;
  padding: 0;
}
```

### Tailwind CSS (`tailwind.config.js`)
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        canvas: '#FFFFFF', // 흰색 배경
        ink: {
          DEFAULT: '#000000', // 검정 텍스트
          muted: 'rgba(0, 0, 0, 0.60)',
          border: 'rgba(0, 0, 0, 0.12)',
          hover: 'rgba(0, 0, 0, 0.04)',
        },
        accent: {
          DEFAULT: '#635BFF', // 파란색 하이라이트
          hover: '#534BE0',
          ring: 'rgba(99, 91, 255, 0.15)',
        }
      },
      fontFamily: {
        sans: ['Pretendard', 'Inter', '-apple-system', 'sans-serif'],
      }
    }
  }
}
```
