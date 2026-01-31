# 🎨 커스터마이징 가이드

[English](./CUSTOMIZATION.md) | **한국어**

이 가이드는 AI 결혼 청첩장의 디자인과 기능을 커스터마이징하는 방법을 설명합니다.

## 📋 목차

- [색상 변경](#색상-변경)
- [폰트 변경](#폰트-변경)
- [레이아웃 수정](#레이아웃-수정)
- [섹션 추가/제거](#섹션-추가제거)
- [애니메이션 커스터마이징](#애니메이션-커스터마이징)
- [이미지 변경](#이미지-변경)
- [기능 추가](#기능-추가)

## 색상 변경

### CSS 변수 사용

모든 색상은 `static/css/variables.css`에서 관리됩니다.

**기본 색상 팔레트:**
```css
/* static/css/variables.css */

:root {
  /* 메인 색상 */
  --primary-color: #B59493;        /* 로즈 골드 */
  --primary-light: #E8DCD9;        /* 연한 로즈 */
  --primary-dark: #8B7170;         /* 진한 로즈 */
  
  /* 보조 색상 */
  --secondary-color: #E8DCD9;
  --accent-color: #D4A5A5;
  
  /* 배경 색상 */
  --background-color: #FFFFFF;
  --background-secondary: #FAF8F7;
  
  /* 텍스트 색상 */
  --text-primary: #333333;
  --text-secondary: #666666;
  --text-light: #999999;
  
  /* 기타 */
  --border-color: #E5E5E5;
  --shadow-color: rgba(0, 0, 0, 0.1);
}
```

### 색상 테마 변경

**예시 1: 민트 테마**
```css
:root {
  --primary-color: #A8DADC;        /* 민트 */
  --primary-light: #E3F5F6;
  --primary-dark: #457B9D;
  --accent-color: #F1FAEE;
}
```

**예시 2: 라벤더 테마**
```css
:root {
  --primary-color: #B8A9C9;        /* 라벤더 */
  --primary-light: #E6E0EF;
  --primary-dark: #8B7FA7;
  --accent-color: #D4C5E2;
}
```

**예시 3: 페일 블루 테마**
```css
:root {
  --primary-color: #A3C4D9;        /* 페일 블루 */
  --primary-light: #D9E8F3;
  --primary-dark: #6B9BBD;
  --accent-color: #B8D8E8;
}
```

**예시 4: 샴페인 골드 테마**
```css
:root {
  --primary-color: #D4AF37;        /* 골드 */
  --primary-light: #F5E8C7;
  --primary-dark: #B8941F;
  --accent-color: #E8D4A0;
}
```

### 다크 모드 추가

```css
/* 다크 모드 토글 */
[data-theme="dark"] {
  --background-color: #1A1A1A;
  --background-secondary: #2D2D2D;
  --text-primary: #FFFFFF;
  --text-secondary: #CCCCCC;
  --text-light: #999999;
  --border-color: #404040;
  --shadow-color: rgba(255, 255, 255, 0.1);
}
```

**JavaScript로 토글:**
```javascript
// static/js/main.js에 추가

function toggleDarkMode() {
  const html = document.documentElement;
  const currentTheme = html.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
}

// 페이지 로드 시 테마 복원
document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
});
```

### 그라데이션 배경

```css
/* 섹션별 그라데이션 */
.cover {
  background: linear-gradient(
    135deg,
    var(--primary-light) 0%,
    var(--primary-color) 100%
  );
}

.letter {
  background: linear-gradient(
    to bottom,
    #FFFFFF 0%,
    var(--background-secondary) 100%
  );
}
```

## 폰트 변경

### 웹 폰트 추가

**Google Fonts 사용:**
```css
/* static/css/variables.css */

/* 폰트 import */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Playfair+Display:wght@400;700&display=swap');

:root {
  /* 본문 폰트 */
  --font-family-main: 'Noto Sans KR', sans-serif;
  
  /* 제목 폰트 */
  --font-family-heading: 'Playfair Display', serif;
  
  /* 영문 폰트 */
  --font-family-english: 'Playfair Display', serif;
}
```

**적용:**
```css
body {
  font-family: var(--font-family-main);
}

h1, h2, h3 {
  font-family: var(--font-family-heading);
}
```

### 한글 웹폰트 추천

**세리프 (우아한 느낌):**
- Noto Serif KR
- Gowun Batang
- Nanum Myeongjo

**산세리프 (현대적인 느낌):**
- Noto Sans KR (기본)
- Spoqa Han Sans Neo
- Pretendard

**손글씨 (친근한 느낌):**
- Nanum Pen Script
- Gamja Flower
- Poor Story

**적용 예시:**
```css
@import url('https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&display=swap');

:root {
  --font-family-main: 'Gowun Batang', serif;
}
```

### 폰트 크기 조정

```css
:root {
  /* 기본 크기 */
  --font-size-base: 16px;
  
  /* 제목 크기 */
  --font-size-h1: 2.5rem;    /* 40px */
  --font-size-h2: 2rem;      /* 32px */
  --font-size-h3: 1.5rem;    /* 24px */
  
  /* 본문 크기 */
  --font-size-body: 1rem;    /* 16px */
  --font-size-small: 0.875rem;  /* 14px */
  --font-size-tiny: 0.75rem; /* 12px */
}

/* 모바일에서 크기 조정 */
@media (max-width: 768px) {
  :root {
    --font-size-base: 14px;
    --font-size-h1: 2rem;
    --font-size-h2: 1.5rem;
  }
}
```

## 레이아웃 수정

### 최대 너비 변경

```css
/* 콘텐츠 최대 너비 */
:root {
  --max-width: 800px;  /* 기본값 */
}

/* 더 넓게 */
:root {
  --max-width: 1200px;
}

/* 더 좁게 (모바일 친화적) */
:root {
  --max-width: 600px;
}
```

### 여백 조정

```css
/* 섹션 간격 */
:root {
  --section-spacing: 80px;  /* 기본값 */
}

/* 모바일 */
@media (max-width: 768px) {
  :root {
    --section-spacing: 40px;
  }
}
```

### 2컬럼 레이아웃

```css
/* 예: 신랑신부 정보를 나란히 */
.couple-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
}

/* 모바일에서는 세로로 */
@media (max-width: 768px) {
  .couple-info {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}
```

## 섹션 추가/제거

### 섹션 제거

**방법 1: HTML 주석 처리**
```html
<!-- templates/index.html -->

<!-- Q&A 섹션 숨기기 -->
<!--
<section class="qna-section">
  ...
</section>
-->
```

**방법 2: CSS로 숨기기**
```css
/* static/css/main.css */

.qna-section {
  display: none;
}
```

### 섹션 추가

**예시: 프러포즈 스토리 섹션**

```html
<!-- templates/index.html -->

<section class="proposal-section">
  <div class="container">
    <div class="header">
      <h2>💍 프러포즈 스토리</h2>
      <p>특별한 순간을 공유합니다</p>
    </div>
    
    <div class="proposal-content">
      <img src="/static/assets/images/proposal.webp" alt="프러포즈">
      <div class="proposal-text">
        <p>2025년 2월 14일 발렌타인데이</p>
        <p>신부가 가장 좋아하는 레스토랑에서</p>
        <p>멋지게(?) 프러포즈를 했습니다.</p>
        <p>물론 신부는 예상하지 못했고...</p>
        <p>신랑은 너무 떨려서 대본을 잊어버렸지만</p>
        <p>행복하게 YES라고 대답해주었습니다! 💕</p>
      </div>
    </div>
  </div>
</section>
```

**스타일 추가:**
```css
/* static/css/main.css */

.proposal-section {
  padding: 80px 20px;
  background: var(--background-secondary);
}

.proposal-content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.proposal-content img {
  width: 100%;
  border-radius: 12px;
  margin-bottom: 30px;
}

.proposal-text p {
  margin: 10px 0;
  font-size: 1.1rem;
  line-height: 1.8;
}
```

### 섹션 순서 변경

HTML에서 `<section>` 태그의 순서를 바꾸면 됩니다:

```html
<!-- 원래 순서 -->
<section class="letter">...</section>
<section class="calendar">...</section>
<section class="gallery">...</section>

<!-- 변경된 순서 -->
<section class="gallery">...</section>
<section class="letter">...</section>
<section class="calendar">...</section>
```

## 애니메이션 커스터마이징

### 스크롤 애니메이션 속도 조정

```css
/* static/css/animations.css */

.fade-in-up {
  transition: all 0.6s ease-out;  /* 기본: 0.6s */
}

/* 더 느리게 */
.fade-in-up {
  transition: all 1s ease-out;
}

/* 더 빠르게 */
.fade-in-up {
  transition: all 0.3s ease-out;
}
```

### 꽃잎 애니메이션 조정

```javascript
// static/js/animations.js

class NaturalPetalRain {
  constructor(container) {
    // 꽃잎 개수 조정
    this.maxPetals = window.innerWidth <= 768 ? 6 : 10;  // 기본값
    
    // 더 많이
    this.maxPetals = window.innerWidth <= 768 ? 10 : 20;
    
    // 더 적게
    this.maxPetals = window.innerWidth <= 768 ? 3 : 5;
  }
}
```

### 호버 효과 추가

```css
/* 버튼에 호버 효과 */
.btn {
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px var(--shadow-color);
}

/* 이미지에 확대 효과 */
.photo-item img {
  transition: transform 0.3s ease;
}

.photo-item:hover img {
  transform: scale(1.05);
}
```

### 커스텀 애니메이션 추가

```css
/* 하트 펄스 애니메이션 */
@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.heart-icon {
  animation: heartbeat 1.5s ease-in-out infinite;
}

/* 반짝이는 효과 */
@keyframes shimmer {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.shimmer {
  animation: shimmer 2s ease-in-out infinite;
}
```

## 이미지 변경

### 커버 이미지

```json
// config/config.json
{
  "assets": {
    "cover_image": "/static/assets/images/my-cover.webp"
  }
}
```

이미지 파일을 `static/assets/images/` 폴더에 저장합니다.

### 배경 이미지 오버레이

```css
/* 커버 이미지에 어두운 오버레이 */
.cover::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);  /* 투명도 조정 */
  z-index: 1;
}

.cover > * {
  position: relative;
  z-index: 2;
}
```

### 아이콘 변경

프로젝트는 [Lucide Icons](https://lucide.dev/)를 사용합니다.

**아이콘 변경:**
```html
<!-- 기존 -->
<i data-lucide="heart"></i>

<!-- 변경 -->
<i data-lucide="heart-handshake"></i>
```

**사용 가능한 아이콘:**
- `heart`, `heart-handshake`, `heart-pulse`
- `calendar`, `map-pin`, `phone`
- `gift`, `camera`, `music`
- [전체 목록](https://lucide.dev/icons/)

### 파비콘 변경

```html
<!-- templates/index.html -->

<link rel="icon" type="image/x-icon" href="/static/assets/images/favicon.ico">

<!-- 또는 PNG -->
<link rel="icon" type="image/png" href="/static/assets/images/favicon.webp">
```

**파비콘 생성:**
- [Favicon Generator](https://favicon.io/)
- 크기: 32x32px 또는 16x16px
- 형식: ICO 또는 PNG

## 기능 추가

### 카운트다운 타이머

```javascript
// static/js/main.js에 추가

function updateCountdown() {
  const weddingDate = new Date('2026-05-17T14:00:00');
  const now = new Date();
  const diff = weddingDate - now;
  
  if (diff <= 0) {
    document.getElementById('countdown').textContent = '오늘입니다! 🎉';
    return;
  }
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);
  
  document.getElementById('countdown').innerHTML = `
    <div class="countdown-unit">
      <span class="countdown-value">${days}</span>
      <span class="countdown-label">일</span>
    </div>
    <div class="countdown-unit">
      <span class="countdown-value">${hours}</span>
      <span class="countdown-label">시간</span>
    </div>
    <div class="countdown-unit">
      <span class="countdown-value">${minutes}</span>
      <span class="countdown-label">분</span>
    </div>
    <div class="countdown-unit">
      <span class="countdown-value">${seconds}</span>
      <span class="countdown-label">초</span>
    </div>
  `;
}

// 1초마다 업데이트
setInterval(updateCountdown, 1000);
updateCountdown();
```

**HTML 추가:**
```html
<div id="countdown" class="countdown-container"></div>
```

**스타일:**
```css
.countdown-container {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin: 30px 0;
}

.countdown-unit {
  text-align: center;
}

.countdown-value {
  display: block;
  font-size: 2.5rem;
  font-weight: bold;
  color: var(--primary-color);
}

.countdown-label {
  display: block;
  font-size: 0.875rem;
  color: var(--text-secondary);
}
```

### 출석 확인 QR 코드

```python
# 새 엔드포인트 추가 (main.py)

from qrcode import QRCode
from io import BytesIO
from fastapi.responses import StreamingResponse

@app.get("/qr/{guest_id}")
async def generate_qr(guest_id: int):
    qr = QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"https://your-domain.com/checkin/{guest_id}")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/png")
```

### 방문자 통계

```javascript
// Google Analytics 추가

<!-- templates/index.html의 <head>에 추가 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### 이메일 RSVP 알림

```python
# main.py에 추가

import smtplib
from email.mime.text import MIMEText

@app.post("/rsvp")
async def submit_rsvp(entry: RSVPEntry):
    # 기존 RSVP 저장 코드...
    
    # 이메일 알림 전송
    send_rsvp_notification(entry)
    
    return RedirectResponse(url="/thanks", status_code=303)

def send_rsvp_notification(entry: RSVPEntry):
    msg = MIMEText(f"""
    새로운 RSVP 응답이 도착했습니다!
    
    이름: {entry.guest_name}
    측: {entry.which_side}
    참석: {entry.can_attend}
    """)
    
    msg['Subject'] = f'새 RSVP: {entry.guest_name}'
    msg['From'] = 'noreply@wedding.com'
    msg['To'] = 'your-email@example.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'your-app-password')
        server.send_message(msg)
```

## 반응형 디자인 조정

### 모바일 최적화

```css
/* 모바일에서 더 큰 터치 영역 */
@media (max-width: 768px) {
  button {
    min-height: 48px;  /* 터치 친화적 */
    font-size: 16px;   /* iOS 자동 줌 방지 */
  }
  
  input, textarea {
    font-size: 16px;   /* iOS 자동 줌 방지 */
  }
}
```

### 태블릿 레이아웃

```css
/* 태블릿 (768px - 1024px) */
@media (min-width: 768px) and (max-width: 1024px) {
  .photo-grid {
    grid-template-columns: repeat(3, 1fr);  /* 3컬럼 */
  }
  
  .container {
    padding: 0 40px;
  }
}
```

### 대형 화면 최적화

```css
/* 데스크톱 (1440px+) */
@media (min-width: 1440px) {
  :root {
    --max-width: 1200px;
  }
  
  .photo-grid {
    grid-template-columns: repeat(4, 1fr);  /* 4컬럼 */
  }
}
```

## 테스트 도구

### 브라우저 개발자 도구

**Chrome DevTools:**
- F12 키로 열기
- Elements 탭: HTML/CSS 실시간 수정
- Console 탭: JavaScript 에러 확인
- Network 탭: 리소스 로딩 확인

### 모바일 테스트

**Chrome 모바일 에뮬레이터:**
1. F12로 개발자 도구 열기
2. Device Toolbar 토글 (Ctrl+Shift+M)
3. 다양한 기기 선택하여 테스트

**실제 기기 테스트:**
```bash
# 같은 네트워크의 모바일에서 접속
# 내부 IP 확인
ipconfig  # Windows
ifconfig  # Mac/Linux

# 모바일에서 접속
http://192.168.1.x:8000
```

## 버전 관리

### Git으로 변경사항 추적

```bash
# 변경 전 백업
git add .
git commit -m "Before customization"

# 실험적 변경
git checkout -b custom-design

# 만족하면 병합
git checkout main
git merge custom-design

# 마음에 안 들면 되돌리기
git checkout main
git branch -D custom-design
```

## 다음 단계

- [설정 가이드](./CONFIGURATION.ko.md) - 컨텐츠 수정
- [AI 챗봇 가이드](./CHATBOT.ko.md) - 챗봇 커스터마이징
- [배포 가이드](./DEPLOYMENT.ko.md) - 변경사항 배포

## 도움이 필요하신가요?

- 📧 [이메일 문의](mailto:your.email@example.com)
- 💬 [디스코드](https://discord.gg/your-server)
- 🐛 [GitHub Issues](https://github.com/yourusername/wedding-invitation/issues)