# ⚙️ 설정 가이드

[English](./CONFIGURATION.md) | **한국어**

이 가이드는 `config/config.json` 파일의 모든 설정 항목을 상세히 설명합니다.

## 📋 목차

- [파일 구조](#파일-구조)
- [결혼 정보 (wedding)](#결혼-정보-wedding)
- [계좌 정보 (accounts)](#계좌-정보-accounts)
- [자주 묻는 질문 (qna)](#자주-묻는-질문-qna)
- [컨텐츠 설정 (content)](#컨텐츠-설정-content)
- [외부 링크 (external_links)](#외부-링크-external_links)
- [에셋 경로 (assets)](#에셋-경로-assets)
- [예시 파일](#예시-파일)

## 파일 구조

`config/config.json`은 청첩장의 모든 정보와 컨텐츠를 관리하는 핵심 파일입니다.

**기본 구조:**
```json
{
  "wedding": { ... },        // 결혼 정보
  "accounts": { ... },       // 계좌 정보
  "qna": [ ... ],           // FAQ
  "content": { ... },       // 페이지 컨텐츠
  "external_links": { ... }, // 외부 링크
  "assets": { ... }         // 파일 경로
}
```

## 결혼 정보 (wedding)

### 신랑 정보 (groom)

```json
{
  "wedding": {
    "groom": {
      "name_kr": "김수환",           // 한글 이름 (전체)
      "name_en": "Soohwan",         // 영문 이름
      "display_name": "수환",        // 표시용 이름 (짧게)
      "birth_order": "장남",         // 장남/차남/삼남 등
      "parents": {
        "father": "김은희",          // 아버지 성함
        "mother": "김미자"           // 어머니 성함
      }
    }
  }
}
```

**필드 설명:**
- `name_kr`: 공식 문서용 전체 이름
- `name_en`: 영문 페이지나 국제 하객용
- `display_name`: 청첩장에 표시되는 짧은 이름
- `birth_order`: 혼주 소개 시 사용
- `parents`: 혼주 연락처 섹션에 표시

**사용 예시:**
```
"수환 ♥ 소영의 결혼식"  (display_name 사용)
"신랑 김수환씨 장남"     (name_kr + birth_order 사용)
```

### 신부 정보 (bride)

```json
{
  "bride": {
    "name_kr": "조소영",
    "name_en": "Soyoung",
    "display_name": "소영",
    "birth_order": "장녀",
    "parents": {
      "father": "조병의",
      "mother": "변시내"
    }
  }
}
```

구조는 신랑 정보와 동일합니다.

### 결혼식 날짜 및 시간 (date)

```json
{
  "date": {
    "year": 2026,                  // 연도
    "month": 5,                    // 월 (1-12)
    "day": 17,                     // 일 (1-31)
    "time": "14:00",              // 24시간 형식
    "day_of_week": "일",           // 요일
    "display_time": "오후 2시",     // 표시용 시간
    "iso_format": "2026-05-17T14:00:00"  // ISO 형식 (캘린더용)
  }
}
```

**필드 설명:**
- `year`, `month`, `day`: D-Day 계산에 사용
- `time`: 24시간 형식 (14:00, 18:30 등)
- `day_of_week`: 한글 요일 (월/화/수/목/금/토/일)
- `display_time`: 사용자 친화적 표시 (오후 2시, 오전 11시 등)
- `iso_format`: Google Calendar 연동에 필요

**ISO 형식 생성 방법:**
```python
from datetime import datetime
dt = datetime(2026, 5, 17, 14, 0)
iso = dt.isoformat()  # "2026-05-17T14:00:00"
```

### 결혼식 장소 (venue)

```json
{
  "venue": {
    "name": "라시따시어터",
    "address": "서울특별시 서초구 매헌로 16 1층",
    "full_address": "서울특별시 서초구 매헌로 16 1층"
  }
}
```

**필드 설명:**
- `name`: 웨딩홀 이름
- `address`: 간단한 주소
- `full_address`: 전체 주소 (복사 기능에 사용)

**팁:**
- 도로명 주소 사용 권장
- 랜드마크 정보 추가 가능
  ```json
  "address": "서울특별시 서초구 매헌로 16 1층 (양재동, 라시따빌딩)"
  ```

## 계좌 정보 (accounts)

### 구조

```json
{
  "accounts": {
    "groom": [
      {
        "name": "김은희",                    // 예금주
        "bank": "국민은행",                  // 은행명
        "number": "123-1234-1234-12",      // 계좌번호
        "kakaopay_url": "https://qr.kakaopay.com/FFFFFFFFFF"  // 카카오페이 URL
      }
    ],
    "bride": [ ... ]
  }
}
```

### 신랑측 계좌

```json
{
  "groom": [
    {
      "name": "김은희",
      "bank": "국민은행",
      "number": "123-1234-1234-12",
      "kakaopay_url": "https://qr.kakaopay.com/FFFFFFFFFF"
    },
    {
      "name": "김미자",
      "bank": "국민은행",
      "number": "123456-12-123456",
      "kakaopay_url": "https://qr.kakaopay.com/FFFFFFFFFF"
    },
    {
      "name": "김수환",
      "bank": "카카오뱅크",
      "number": "3333-06-1234567",
      "kakaopay_url": "https://qr.kakaopay.com/FFFFFFFFFF"
    }
  ]
}
```

**계좌 순서:**
1. 아버지 계좌
2. 어머니 계좌
3. 신랑/신부 본인 계좌

### 신부측 계좌

구조는 신랑측과 동일합니다.

### 카카오페이 QR 생성

1. [카카오페이](https://www.kakaopay.com/) 앱 실행
2. "송금" → "QR코드 송금"
3. "받기 QR코드 만들기"
4. URL 복사하여 `kakaopay_url`에 입력

**QR 없이 사용:**
```json
{
  "name": "김수환",
  "bank": "카카오뱅크",
  "number": "3333-06-1234567",
  "kakaopay_url": ""  // 빈 문자열로 설정
}
```

## 자주 묻는 질문 (qna)

### 구조

```json
{
  "qna": [
    {
      "id": 1,
      "question": "결혼식은 언제, 어디서 하나요?",
      "answer": "2026년 5월 17일 (일) 오후 2시에 라시따시어터에서 진행됩니다."
    }
  ]
}
```

### 기본 FAQ 항목

```json
{
  "qna": [
    {
      "id": 1,
      "question": "결혼식은 언제, 어디서 하나요?",
      "answer": "2026년 5월 17일 (일) 오후 2시에 라시따시어터에서 진행됩니다.<br>주소: 서울특별시 서초구 매헌로 16 1층"
    },
    {
      "id": 2,
      "question": "주차가 가능한가요?",
      "answer": "네, 라시따시어터 건물 내 주차장을 이용하실 수 있습니다.<br>주차장 인포데스크에서 차량번호를 등록해주세요."
    },
    {
      "id": 3,
      "question": "대중교통으로 어떻게 가나요?",
      "answer": "신분당선 양재시민의숲역 5번 출구에서 셔틀버스가 운영됩니다.<br>자세한 교통편은 아래 지도를 참고해주세요."
    },
    {
      "id": 4,
      "question": "드레스코드가 있나요?",
      "answer": "특별한 드레스코드는 없습니다.<br>편안하고 단정한 복장으로 참석해주시면 됩니다."
    },
    {
      "id": 5,
      "question": "축의금은 어떻게 전달하나요?",
      "answer": "결혼식 당일 리셉션에서 전달하시거나,<br>아래 '마음전하기' 버튼을 통해 미리 송금하실 수 있습니다."
    },
    {
      "id": 6,
      "question": "식사는 제공되나요?",
      "answer": "네, 결혼식 후 피로연에서 식사가 제공됩니다.<br>특별한 식단이 필요하시면 미리 연락주세요."
    }
  ]
}
```

**HTML 태그 사용:**
- `<br>`: 줄바꿈
- `<strong>`: 강조
- `<a href="...">`: 링크 (필요시)

**추가 FAQ 예시:**
```json
{
  "id": 7,
  "question": "아이와 함께 가도 되나요?",
  "answer": "물론입니다! 아이들을 환영합니다.<br>다만 예식장이 조용한 편이니 참고 부탁드립니다."
},
{
  "id": 8,
  "question": "사진 촬영이 가능한가요?",
  "answer": "네, 자유롭게 촬영하셔도 됩니다.<br>단, 예식 중에는 플래시를 끄고 촬영해주세요."
}
```

## 컨텐츠 설정 (content)

### 페이지 메타 정보 (meta)

```json
{
  "content": {
    "page_title": "김수환 ♥ 조소영의 결혼식에 초대합니다",
    "meta": {
      "title": "수환 ♥ 소영의 결혼식",
      "description": "2026년 5월 17일 (일) 오후 2시, 라시따시어터에서 진행됩니다",
      "image": "https://your-domain.com/static/assets/images/thumbnail.jpg"
    }
  }
}
```

**필드 설명:**
- `page_title`: 브라우저 탭 제목
- `meta.title`: SNS 공유 시 제목
- `meta.description`: SNS 공유 시 설명
- `meta.image`: SNS 공유 시 썸네일 (절대 URL)

**썸네일 이미지 권장 사항:**
- 크기: 1200 x 630px (Facebook OG 기준)
- 형식: JPG 또는 PNG
- 용량: 300KB 이하

### 초대 편지 (letter)

```json
{
  "letter": {
    "title": "두 사람의 결혼식에 초대합니다.",
    "content": "지금까지 함께해 주시며 나누었던 소중한 순간들이 저희에게 큰 기쁨과 힘이 되었습니다.<br>이제 저희 인생의 또 하나의 특별한 순간을 맞이하며, 소중한 여러분을 이 자리에 초대하고 싶습니다."
  }
}
```

**작성 팁:**
- 진심이 담긴 짧은 문장
- 과도한 형식보다는 솔직한 마음
- HTML 줄바꿈 태그 (`<br>`) 사용

**예시 편지:**
```json
{
  "content": "서로 다른 길을 걷던 저희 둘이<br>하나의 길에서 만나 사랑하게 되었습니다.<br><br>이제 함께 새로운 인생을 시작하려 합니다.<br>저희의 시작을 축복해 주시면<br>더없이 큰 기쁨이 되겠습니다."
}
```

### D-Day 표시 (d_day)

```json
{
  "d_day": {
    "prefix": "수환",
    "suffix": "소영의 결혼식이",
    "symbol": "♥︎"
  }
}
```

**표시 결과:**
```
수환 ♥︎ 소영의 결혼식이
D-123일 남았습니다
```

### RSVP 섹션 (rsvp)

```json
{
  "rsvp": {
    "title": "RSVP",
    "subtitle": "참석 의사를 전해주세요",
    "button_text": "참석 의사 전달하기"
  }
}
```

### 갤러리 (gallery)

```json
{
  "gallery": {
    "title": "Gallery",
    "subtitle": "사진을 클릭하면 더 크게 볼 수 있습니다",
    "total_photos": 28
  }
}
```

**`total_photos` 설정:**
- `static/assets/images/wedding-snaps/` 폴더의 이미지 개수
- 파일명: `1.webp`, `2.webp`, ..., `28.webp`

### 방명록 (guestbook)

```json
{
  "guestbook": {
    "title": "Guestbook",
    "subtitle": "신랑신부에게 따뜻한 축하 메시지를 남겨주세요",
    "preview_text": "여러분의 소중한 축하 메시지를<br>방명록에 남겨주세요",
    "button_text": "축하 메세지 작성하기",
    "messages_title": "축하 메시지",
    "empty_message": "아직 남겨진 메시지가 없습니다",
    "empty_subtitle": "첫 번째 축하 메시지를 남겨보세요!"
  }
}
```

### 연락처 (contact_section)

```json
{
  "contact_section": {
    "title": "연락처",
    "subtitle": "궁금한 점이 있으시면 언제든지 연락주세요",
    "groom_title": "신랑",
    "bride_title": "신부",
    "groom_contact_title": "신랑 측 혼주",
    "bride_contact_title": "신부 측 혼주",
    "father_label": "아버지",
    "mother_label": "어머니"
  }
}
```

### 계좌 정보 (account_section)

```json
{
  "account_section": {
    "title": "마음 전하기",
    "groom_button": "신랑 측 계좌번호",
    "bride_button": "신부 측 계좌번호",
    "modal_title_groom": "신랑측",
    "modal_title_bride": "신부측",
    "copy_button_text": "복사하기",
    "kakaopay_alt_text": "카카오페이",
    "copy_success_message": "계좌번호가 복사되었습니다! 💰",
    "copy_error_message": "복사에 실패했습니다. 다시 시도해주세요."
  }
}
```

### 위치 정보 (location)

```json
{
  "location": {
    "title": "Location",
    "copy_address_text": "클릭하면 주소가 복사됩니다",
    "map_click_hint": "클릭하면 크게 볼 수 있습니다",
    "map_buttons": {
      "naver": "네이버맵",
      "kakao": "카카오맵",
      "tmap": "티맵"
    }
  }
}
```

### 공유하기 (share)

```json
{
  "share": {
    "title": "공유하기",
    "subtitle": "소중한 분들과 함께 저희의 특별한 날을 공유해주세요",
    "message": "소중한 분들과 함께 저희의 특별한 날을<br>공유해주세요 💕",
    "buttons": {
      "kakao": "카카오톡 공유",
      "link": "링크 복사",
      "native": "공유하기"
    },
    "kakao_share": {
      "title": "💒 수환 ♥ 소영의 결혼식",
      "description": "2026년 5월 17일 (일) 오후 2시\n라시따시어터에서 진행됩니다.\n\n소중한 분을 모시고 참석해주시면 감사하겠습니다.",
      "button_title": "청첩장 보기"
    }
  }
}
```

### AI 챗봇 (chatbot)

```json
{
  "chatbot": {
    "name": "수환 & 소영 💕",
    "title": "궁금한 것이 있으신가요?",
    "subtitle": "저희에 대해 궁금한 것이 있으시면 언제든 물어보세요! 💕",
    "placeholder": "예: 두 분은 어떻게 만나셨나요?",
    "submit_button": "질문하기",
    "fallback_message": "죄송해요 😅 해당 질문에 대한 정보가 없네요 😢",
    "error_message": "앗! 잠시 문제가 생겼네요 😅",
    "thinking_message": "생각하고 있어요... 🤔",
    "profile_image": "/static/assets/images/chatbot-profile.webp",
    "welcome": {
      "greeting": "안녕하세요! 저희에 대해 궁금한 걸 물어보세요! 😊",
      "description": "저희 커플에 대해 궁금한 것이 있으시면 언제든 물어보세요!",
      "suggested_questions": [
        "두 분은 어떻게 만나셨나요?",
        "첫 데이트는 어디서 하셨어요?",
        "신혼여행은 어디로 가세요?",
        "취미가 뭐예요?"
      ]
    }
  }
}
```

**`suggested_questions` 커스터마이징:**
- 실제로 자주 받는 질문들로 구성
- 4-6개 권장
- 지식베이스에 답변이 있는 질문만

### 푸터 (footer)

```json
{
  "footer": {
    "signature": "Copyright 2025. Soohwan & Soyoung All rights reserved.",
    "github_url": "https://github.com/yourusername"
  }
}
```

## 외부 링크 (external_links)

### 지도 앱 연동

```json
{
  "external_links": {
    "maps": {
      "naver": "https://naver.me/xAFClJVG",
      "kakao": "https://kko.kakao.com/Eo2w9mM40X",
      "tmap": "https://tmap.life/1306a1ab"
    }
  }
}
```

**링크 생성 방법:**

**네이버 지도:**
1. [네이버 지도](https://map.naver.com/) 접속
2. 장소 검색
3. "공유" 버튼 → "URL 복사"

**카카오맵:**
1. [카카오맵](https://map.kakao.com/) 접속
2. 장소 검색
3. "공유" 버튼 → "링크 복사"

**티맵:**
1. [티맵](https://www.tmap.co.kr/) 접속
2. 장소 검색
3. "공유" 버튼 → "링크 복사"

## 에셋 경로 (assets)

### 파일 경로 설정

```json
{
  "assets": {
    "background_music": "/static/assets/audio/wedding-music.mp3",
    "cover_image": "/static/assets/images/cover.webp",
    "gallery_path": "/static/assets/images/wedding-snaps/",
    "map_image": "/static/assets/images/lacitta.webp",
    "share_background_image": "/static/assets/images/couple-bridge.webp",
    "kakaopay_icon": "/static/assets/images/payment_icon_yellow_small.webp"
  }
}
```

**파일 위치:**
```
static/
├── assets/
│   ├── audio/
│   │   └── wedding-music.mp3
│   └── images/
│       ├── cover.webp
│       ├── lacitta.webp
│       ├── couple-bridge.webp
│       ├── payment_icon_yellow_small.webp
│       └── wedding-snaps/
│           ├── 1.webp
│           ├── 2.webp
│           └── ...
```

**이미지 최적화 팁:**
```bash
# WebP 변환 및 리사이즈
python scripts/resize_image.py
```

## 예시 파일

### 완전한 config.json 예시

실제 사용 가능한 완전한 설정 파일을 프로젝트에 포함되어 있습니다:

```
config/config.json.example
```

### 최소 설정 예시

빠르게 시작하기 위한 최소 설정:

```json
{
  "wedding": {
    "groom": {
      "name_kr": "홍길동",
      "display_name": "길동"
    },
    "bride": {
      "name_kr": "김영희",
      "display_name": "영희"
    },
    "date": {
      "year": 2026,
      "month": 6,
      "day": 15,
      "time": "14:00",
      "display_time": "오후 2시"
    },
    "venue": {
      "name": "그랜드 웨딩홀",
      "address": "서울시 강남구 테헤란로 123"
    }
  },
  "content": {
    "page_title": "길동 ♥ 영희의 결혼식",
    "letter": {
      "title": "결혼합니다",
      "content": "저희 결혼식에 초대합니다."
    }
  }
}
```

## 검증 및 테스트

### JSON 유효성 검사

온라인 도구 사용:
- [JSONLint](https://jsonlint.com/)
- [JSON Formatter](https://jsonformatter.org/)

또는 Python으로:
```bash
python -m json.tool config/config.json
```

### 로컬 테스트

```bash
# 서버 실행
python main.py

# 브라우저에서 확인
http://localhost:8000
```

### 체크리스트

- [ ] 모든 이름과 날짜가 정확한가?
- [ ] 계좌번호가 올바른가?
- [ ] 지도 링크가 작동하는가?
- [ ] 이미지 경로가 올바른가?
- [ ] JSON 문법 오류가 없는가?
- [ ] 특수문자가 올바르게 escape 되었는가?

## 다음 단계

- [AI 챗봇 가이드](./CHATBOT.ko.md) - 지식베이스 작성
- [커스터마이징 가이드](./CUSTOMIZATION.ko.md) - 디자인 수정
- [배포 가이드](./DEPLOYMENT.ko.md) - Railway 배포

## 도움이 필요하신가요?

- 📧 [이메일 문의](mailto:your.email@example.com)
- 💬 [디스코드](https://discord.gg/your-server)
- 🐛 [GitHub Issues](https://github.com/yourusername/wedding-invitation/issues)