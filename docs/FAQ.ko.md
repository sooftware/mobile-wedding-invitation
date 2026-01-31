# ❓ 자주 묻는 질문 (FAQ)

[English](./FAQ.md) | **한국어**

AI 결혼 청첩장에 대해 자주 묻는 질문들을 모았습니다.

## 📋 목차

- [일반](#일반)
- [설치 및 배포](#설치-및-배포)
- [AI 챗봇](#ai-챗봇)
- [방명록 및 RSVP](#방명록-및-rsvp)
- [관리자 기능](#관리자-기능)
- [비용](#비용)
- [보안](#보안)
- [커스터마이징](#커스터마이징)

## 일반

### Q: 이 프로젝트는 무료인가요?

**A:** 프로젝트 자체는 무료 오픈소스입니다 (CC BY-NC-SA 라이선스). 하지만 사용하려면 몇 가지 외부 서비스 비용이 발생할 수 있습니다:

✅ **무료로 사용 가능:**
- Railway 무료 티어 ($5 크레딧/월)
- PostgreSQL (Railway 포함)
- 기본 기능 모두

💰 **비용 발생 가능:**
- OpenAI API (챗봇 사용 시, ~$2-5/월)
- 카카오 개발자 계정 (무료이지만 앱 등록 필요)
- LangSmith (선택, 무료 티어 있음)

**예상 총 비용:** 월 $3-7 (소규모 결혼식 기준)

---

### Q: 프로그래밍을 모르는데 사용할 수 있나요?

**A:** 기본적인 컴퓨터 사용 능력과 영어 독해 능력이 있다면 가능합니다!

**필요한 기술:**
- ✅ 파일 복사/붙여넣기
- ✅ 텍스트 에디터 사용
- ✅ 터미널 기본 명령어 (복사/붙여넣기 수준)
- ✅ JSON 파일 편집 (간단)

**자세한 가이드 제공:**
- [빠른 시작 가이드](./QUICKSTART.ko.md)
- [설치 가이드](./INSTALLATION.ko.md)
- [설정 가이드](./CONFIGURATION.ko.md)

---

### Q: 모바일에서도 잘 작동하나요?

**A:** 네! 완전 반응형 디자인으로 모바일에 최적화되어 있습니다.

**테스트된 기기:**
- 📱 iPhone (Safari, Chrome)
- 📱 Android (Chrome, Samsung Internet)
- 📱 태블릿 (iPad, Galaxy Tab)
- 💻 데스크톱 (Chrome, Firefox, Safari, Edge)

**모바일 특화 기능:**
- 터치 제스처 지원
- 모바일 네비게이션
- 빠른 로딩 (WebP 이미지)
- 작은 화면 최적화 레이아웃

---

### Q: 다른 언어로 번역할 수 있나요?

**A:** 네! `config/config.json` 파일의 모든 텍스트를 수정할 수 있습니다.

**현재 지원:**
- 한국어 (기본)
- 영어 (문서 제공)

**추가하려면:**
1. `config.json`의 모든 텍스트 번역
2. `couple_knowledge.json` 번역
3. `app/chatbot/prompts.json` 번역

**커뮤니티 번역 환영!**
중국어, 일본어 등 다른 언어 번역을 기여하실 분을 찾고 있습니다.

---

## 설치 및 배포

### Q: Railway 외에 다른 플랫폼에도 배포할 수 있나요?

**A:** 네! Python을 지원하는 대부분의 플랫폼에 배포 가능합니다.

**추천 플랫폼:**

1. **Railway** (권장) ⭐
   - 장점: 무료, 간편, PostgreSQL 통합
   - 단점: 제한적인 무료 티어
   - [배포 가이드](./DEPLOYMENT.ko.md)

2. **Heroku**
   - 장점: 안정적, 많은 문서
   - 단점: 무료 티어 없음 ($5/월~)
   - PostgreSQL 애드온 사용

3. **Render**
   - 장점: 무료 티어, 간편
   - 단점: 느린 콜드 스타트
   - PostgreSQL 무료 제공

4. **AWS/GCP/Azure**
   - 장점: 강력하고 확장 가능
   - 단점: 복잡하고 비쌈
   - Docker 사용 권장

5. **직접 서버 (VPS)**
   - 장점: 완전한 제어
   - 단점: 서버 관리 필요
   - DigitalOcean, Linode 등

---

### Q: 로컬에서만 사용할 수 있나요?

**A:** 네! 인터넷 배포 없이 로컬에서만 실행 가능합니다.

**사용 시나리오:**
- 결혼식 당일 태블릿에서 운영
- 테스트 및 개발
- 오프라인 데모

**로컬 실행:**
```bash
python main.py
# 브라우저에서 http://localhost:8000 접속
```

**주의사항:**
- 하객들이 접속하려면 같은 네트워크에 있어야 함
- 인터넷 없이는 AI 챗봇 작동 안 함 (OpenAI API 필요)

---

### Q: 도메인이 꼭 필요한가요?

**A:** 아니요! Railway가 무료 도메인을 제공합니다.

**옵션:**

1. **Railway 기본 도메인 (무료)**
   ```
   your-app.railway.app
   ```
   - 바로 사용 가능
   - HTTPS 자동 적용

2. **커스텀 도메인 (선택)**
   ```
   wedding.yourdomain.com
   ```
   - 도메인 구매 필요 (~₩10,000/년)
   - 더 기억하기 쉬움
   - 전문적인 느낌

**추천:** 무료 도메인으로 충분합니다!

---

## AI 챗봇

### Q: AI 챗봇 없이도 사용할 수 있나요?

**A:** 네! 챗봇 없이도 모든 핵심 기능을 사용할 수 있습니다.

**챗봇 비활성화 방법:**
1. OpenAI API 키를 설정하지 않으면 자동 비활성화
2. 챗봇 섹션이 표시되지 않음
3. 다른 기능은 정상 작동

**챗봇 없이 사용 가능한 기능:**
- ✅ 방명록
- ✅ RSVP
- ✅ 갤러리
- ✅ 지도 및 정보
- ✅ 관리자 페이지

---

### Q: OpenAI API 비용이 얼마나 나오나요?

**A:** 소규모 결혼식 기준 월 $2-5 정도입니다.

**비용 계산:**

**임베딩 (지식베이스 생성):**
```
20개 지식 항목 × 500 토큰 = 10,000 토큰
= $0.00001 × 10 = $0.0001 (거의 무료)
```

**챗봇 대화:**
```
하객 150명 × 평균 2번 질문 = 300번 대화
300 × (입력 50 토큰 + 출력 100 토큰) = 45,000 토큰
= $0.15 (gpt-4o-mini 기준)
```

**총 예상 비용:**
- 결혼 준비 기간: $1-2/월
- 결혼식 당월: $3-5
- 결혼식 후: $0 (서비스 중지)

**비용 절감 팁:**
```bash
# .env 파일에서 저렴한 모델 사용
CHAT_MODEL=gpt-3.5-turbo  # 더 저렴
MAX_TOKENS=150  # 토큰 수 제한
```

---

### Q: 챗봇이 틀린 정보를 말하면 어떻게 하나요?

**A:** 지식베이스를 개선하면 됩니다.

**해결 방법:**

1. **지식베이스 확인**
   ```json
   // config/couple_knowledge.json
   {
     "id": "wrong_info",
     "topic": "문제가 되는 주제",
     "content": "올바른 정보로 수정"
   }
   ```

2. **더 구체적으로 작성**
   - ❌ 나쁜 예: "대학교에서 만남"
   - ✅ 좋은 예: "2018년 광운대학교 '모바일 프로그래밍' 수업에서 처음 만남"

3. **Temperature 낮추기**
   ```bash
   CHAT_TEMPERATURE=0.3  # 더 정확한 답변
   ```

4. **프롬프트 개선**
   ```json
   // app/chatbot/prompts.json
   "반드시 제공된 정보만 사용하세요. 추측하지 마세요."
   ```

자세한 내용은 [챗봇 가이드](./CHATBOT.ko.md)를 참고하세요.

---

### Q: 챗봇이 한국어 외에 다른 언어도 지원하나요?

**A:** 네! OpenAI GPT 모델은 다국어를 지원합니다.

**설정 방법:**

1. **지식베이스를 원하는 언어로 작성**
   ```json
   [
     {
       "id": "first_meeting",
       "topic": "First Meeting",
       "content": "We first met at university in 2018."
     }
   ]
   ```

2. **프롬프트 언어 변경**
   ```json
   // app/chatbot/prompts.json
   {
     "system_template": "You are an AI assistant for the wedding..."
   }
   ```

3. **자동 언어 감지**
   - 사용자가 영어로 질문하면 영어로 답변
   - 한국어로 질문하면 한국어로 답변

---

## 방명록 및 RSVP

### Q: 방명록 메시지를 수정/삭제하려면 어떻게 하나요?

**A:** 비밀번호를 알아야 수정/삭제할 수 있습니다.

**사용자가 직접:**
1. 방명록 카드의 ✏️ 또는 × 버튼 클릭
2. 작성 시 입력한 비밀번호 입력
3. 수정 또는 삭제

**관리자가:**
1. `/admin` 페이지 로그인
2. 방명록 탭에서 삭제 버튼 클릭
3. 비밀번호 없이 바로 삭제 가능

---

### Q: RSVP 응답을 수정할 수 있나요?

**A:** 현재 버전에서는 RSVP 수정 기능이 없습니다.

**해결 방법:**

**옵션 1: 관리자가 직접 수정**
- 관리자 페이지에서 기존 응답 삭제
- 하객에게 다시 제출 요청

**옵션 2: 데이터베이스 직접 수정**
```bash
# Railway CLI로 접속
railway run psql $DATABASE_URL

# 수정
UPDATE rsvp SET can_attend = '참석할게요' WHERE id = 123;
```

**향후 업데이트 예정:**
- RSVP 수정 기능 추가
- 전화번호로 본인 확인

---

### Q: 방명록에 사진을 첨부할 수 있나요?

**A:** 현재 버전에서는 텍스트만 지원합니다.

**대안:**

**옵션 1: 외부 링크 사용**
```
축하합니다! 🎉
사진: https://imgur.com/abc123
```

**옵션 2: 갤러리 활용**
- 하객들이 보낸 사진을 수동으로 갤러리에 추가
- `static/assets/images/guest-photos/`

**향후 업데이트 예정:**
- 이미지 업로드 기능
- 포토부스 연동

---

### Q: 방명록을 비공개로 설정할 수 있나요?

**A:** 현재는 모든 방명록이 공개됩니다.

**커스텀 구현:**

`templates/index.html` 수정:
```html
<!-- 방명록 섹션 주석 처리 또는 삭제 -->
<!--
<section class="guestbook-section">
  ...
</section>
-->
```

또는 CSS로 숨기기:
```css
.guestbook-section {
  display: none;
}
```

**관리자만 보기:**
- 방명록은 `/admin` 페이지에서만 확인 가능

---

## 관리자 기능

### Q: 관리자 비밀번호를 잊어버렸어요!

**A:** 새 비밀번호 해시를 생성하여 재설정할 수 있습니다.

**로컬 환경:**
```bash
# 1. 새 해시 생성
python scripts/generate_password_hash.py

# 2. .env 파일 수정
ADMIN_PASSWORD_HASH=새로_생성한_해시

# 3. 서버 재시작
python main.py
```

**Railway 배포:**
```bash
# 1. 새 해시 생성
python scripts/generate_password_hash.py

# 2. Railway 환경변수 업데이트
railway variables set ADMIN_PASSWORD_HASH="새로_생성한_해시"

# 3. 자동으로 재배포됨
```

---

### Q: 관리자를 여러 명 추가할 수 있나요?

**A:** 현재 버전은 단일 관리자만 지원합니다.

**같은 계정 공유:**
- 신랑과 신부가 같은 아이디/비밀번호 사용
- 안전하게 공유 (메신저 X, 직접 전달 O)

**향후 업데이트 예정:**
- 다중 관리자 지원
- 역할 기반 권한 (읽기 전용, 편집 등)

---

### Q: 관리자 페이지에 접속할 수 없어요!

**A:** 몇 가지 원인이 있을 수 있습니다.

**체크리스트:**

1. **올바른 URL인지 확인**
   ```
   https://your-app.railway.app/admin/login
   ```

2. **아이디/비밀번호 확인**
   ```bash
   # 환경변수 확인
   railway variables | grep ADMIN
   ```

3. **비밀번호 해시 확인**
   ```bash
   # 해시가 올바른지 재확인
   python scripts/generate_password_hash.py
   ```

4. **브라우저 캐시 삭제**
   - Ctrl+Shift+Delete (Windows)
   - Cmd+Shift+Delete (Mac)

5. **시크릿 모드에서 시도**

---

### Q: RSVP 데이터를 엑셀로 내보낼 수 있나요?

**A:** 네! CSV 형식으로 내보낼 수 있습니다.

**방법:**
1. `/admin` 페이지 로그인
2. RSVP 탭 선택
3. "CSV 내보내기" 버튼 클릭
4. 파일 저장

**CSV를 엑셀로 열기:**
1. 엑셀 실행
2. "데이터" → "텍스트/CSV에서"
3. 저장한 CSV 파일 선택
4. "쉼표"로 구분 설정
5. UTF-8 인코딩 선택

---

## 비용

### Q: 완전 무료로 운영할 수 있나요?

**A:** AI 챗봇을 제외하면 거의 무료입니다.

**무료 구성:**
```
Railway 무료 티어: $5 크레딧/월
웹 호스팅: ~$3/월
PostgreSQL: ~$1/월
남은 크레딧: ~$1/월 (여유분)
총 비용: $0
```

**챗봇 추가 시:**
```
OpenAI API: $2-5/월
총 비용: $2-5/월
```

**결혼식 기간만 운영:**
- 2개월 운영: $4-10
- 결혼식 후 pause: $0

---

### Q: Railway 무료 티어로 충분한가요?

**A:** 소규모 결혼식(~200명)은 충분합니다.

**무료 티어 제한:**
- 월 $5 크레딧
- 512 MB RAM
- 1 GB 디스크 
- 100 GB 대역폭

**예상 사용량 (하객 200명):**
- 웹 서비스: ~$3/월
- PostgreSQL: ~$1/월
- 대역폭: ~20 GB/월

**초과 시:**
- Hobby Plan 업그레이드 ($5/월)
- 또는 다른 플랫폼 고려

---

### Q: 결혼식 후에도 계속 비용이 나오나요?

**A:** Railway 프로젝트를 pause하면 비용이 발생하지 않습니다.

**Pause 방법:**
```bash
# CLI로
railway pause

# 또는 대시보드에서
프로젝트 → Settings → Pause Project
```

**Pause 효과:**
- 모든 서비스 중지
- 데이터는 보존
- 비용 $0

**Resume 방법:**
```bash
railway resume
```

언제든지 다시 시작 가능!

---

## 보안

### Q: 방명록 비밀번호는 안전한가요?

**A:** 네! SHA-256 해시로 암호화되어 저장됩니다.

**보안 조치:**
- 원본 비밀번호는 저장하지 않음
- 해시값만 데이터베이스에 저장
- 해시는 역산 불가능

**비밀번호 예시:**
```
사용자 입력: "my-password123"
저장되는 값: "a665a45920422f9d417e4867efdc4fb8..."
```

해커가 데이터베이스를 얻어도 원본 비밀번호는 알 수 없습니다.

---

### Q: 개인정보는 어떻게 보호되나요?

**A:** 최소한의 정보만 수집하고 안전하게 보관합니다.

**수집 정보:**

**방명록:**
- 이름
- 메시지
- 비밀번호 (해시)
- 작성 시간

**RSVP:**
- 이름
- 신랑/신부측
- 참석 여부
- 전화번호 뒷자리 (선택)

**수집하지 않는 정보:**
- 주민등록번호
- 전체 전화번호
- 주소
- 이메일 (수집 선택 가능)

**보안:**
- HTTPS 암호화 통신
- 데이터베이스 접근 제한
- Railway 보안 인프라

---

### Q: SQL Injection 같은 공격으로부터 안전한가요?

**A:** 네! FastAPI와 SQLAlchemy의 파라미터 바인딩을 사용합니다.

**보안 기능:**

1. **Prepared Statements**
   ```python
   # 안전한 쿼리
   cursor.execute("SELECT * FROM guestbook WHERE id = ?", (id,))
   ```

2. **입력 검증**
   - Pydantic으로 타입 검증
   - 길이 제한
   - 특수문자 필터링

3. **CORS 설정**
   - 허용된 도메인만 접근
   - XSS 방지

4. **세션 관리**
   - SECRET_KEY 암호화
   - 세션 타임아웃

---

### Q: Railway는 안전한가요?

**A:** 네! Railway는 보안이 검증된 플랫폼입니다.

**Railway 보안:**
- SOC 2 Type II 인증
- 암호화된 환경변수
- 자동 SSL 인증서
- DDoS 방어
- 정기 보안 감사

**추가 보안 팁:**
1. 강력한 관리자 비밀번호 사용
2. SECRET_KEY를 랜덤하게 생성
3. API 키를 절대 GitHub에 커밋하지 않기
4. 정기적으로 백업

---

## 커스터마이징

### Q: 디자인을 바꿀 수 있나요?

**A:** 네! CSS를 수정하여 원하는 대로 커스터마이징할 수 있습니다.

**기본 수정:**
```css
/* static/css/variables.css */

/* 색상 변경 */
--primary-color: #B59493;  /* 메인 색상 */
--secondary-color: #E8DCD9;  /* 보조 색상 */

/* 폰트 변경 */
--font-family-main: 'Noto Sans KR', sans-serif;
```

**고급 수정:**
- 레이아웃 변경
- 애니메이션 추가
- 새로운 섹션 추가

자세한 내용은 [커스터마이징 가이드](./CUSTOMIZATION.ko.md)를 참고하세요.

---

### Q: 로고나 아이콘을 바꿀 수 있나요?

**A:** 네! 이미지 파일을 교체하면 됩니다.

**파비콘 (브라우저 탭 아이콘):**
```
static/assets/images/favicon.ico
```

**오픈그래프 이미지 (SNS 공유 썸네일):**
```json
// config/config.json
{
  "content": {
    "meta": {
      "image": "/static/assets/images/my-thumbnail.jpg"
    }
  }
}
```

**기타 아이콘:**
- Lucide Icons 사용 (변경 쉬움)
- 또는 직접 SVG/PNG 추가

---

### Q: 섹션을 추가하거나 제거할 수 있나요?

**A:** 네! HTML 템플릿을 수정하면 됩니다.

**섹션 제거:**
```html
<!-- templates/index.html -->

<!-- 제거하고 싶은 섹션 주석 처리 -->
<!--
<section class="qna-section">
  ...
</section>
-->
```

**섹션 추가:**
```html
<!-- 새 섹션 추가 -->
<section class="my-custom-section">
  <h2>새로운 섹션</h2>
  <p>내용...</p>
</section>
```

**섹션 순서 변경:**
- HTML에서 `<section>` 태그 순서 바꾸기

---

### Q: 배경음악을 바꿀 수 있나요?

**A:** 네! 음악 파일을 교체하면 됩니다.

**방법:**
1. 새 음악 파일 준비 (MP3 권장)
2. 파일 위치:
   ```
   static/assets/audio/wedding-music.mp3
   ```
3. 같은 파일명으로 교체하거나
4. `config.json`에서 경로 변경:
   ```json
   {
     "assets": {
       "background_music": "/static/assets/audio/my-song.mp3"
     }
   }
   ```

**음악 추천:**
- 저작권 걱정 없는 음악 사용
- YouTube Audio Library
- Epidemic Sound
- Artlist

---

### Q: 언어를 영어로 바꿀 수 있나요?

**A:** 네! 모든 텍스트를 영어로 번역하면 됩니다.

**변경할 파일:**

1. `config/config.json` - 모든 텍스트
2. `config/couple_knowledge.json` - 챗봇 지식
3. `app/chatbot/prompts.json` - 챗봇 프롬프트

**예시:**
```json
// config/config.json
{
  "content": {
    "page_title": "Soohwan ♥ Soyoung's Wedding",
    "letter": {
      "title": "We're Getting Married",
      "content": "We invite you to celebrate..."
    }
  }
}
```

---

## 기술 지원

### 여전히 문제가 해결되지 않았나요?

**도움을 받을 수 있는 곳:**

1. **문서 확인**
   - [설치 가이드](./INSTALLATION.ko.md)
   - [배포 가이드](./DEPLOYMENT.ko.md)
   - [챗봇 가이드](./CHATBOT.ko.md)
   - [설정 가이드](./CONFIGURATION.ko.md)

2. **커뮤니티 지원**
   - 💬 [디스코드 참여](https://discord.gg/your-server)
   - 📖 [GitHub Discussions](https://github.com/yourusername/wedding-invitation/discussions)

3. **버그 리포트**
   - 🐛 [GitHub Issues](https://github.com/yourusername/wedding-invitation/issues)

4. **직접 문의**
   - 📧 [이메일](mailto:your.email@example.com)

---

**이 FAQ가 도움이 되셨나요?** 

더 궁금한 점이 있다면 언제든지 문의해주세요! 🎉