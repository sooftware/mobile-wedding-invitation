# 🤖 AI 챗봇 가이드

[English](./CHATBOT.md) | **한국어**

이 가이드는 AI 결혼 청첩장의 챗봇 기능을 설정하고 커스터마이징하는 방법을 설명합니다.

## 📋 목차

- [개요](#개요)
- [챗봇 작동 방식](#챗봇-작동-방식)
- [지식베이스 작성하기](#지식베이스-작성하기)
- [프롬프트 커스터마이징](#프롬프트-커스터마이징)
- [고급 설정](#고급-설정)
- [문제 해결](#문제-해결)

## 개요

AI 챗봇은 LangGraph와 LangChain을 기반으로 구축되었으며, RAG (Retrieval-Augmented Generation) 방식을 사용하여 신랑신부에 대한 질문에 답변합니다.

### 주요 기능

- 📚 **지식베이스 검색**: 벡터 데이터베이스를 활용한 의미론적 검색
- 🔄 **자동 재시도**: 실패 시 exponential backoff로 재시도
- ⏱️ **타임아웃 처리**: 무한 루프 방지
- 📊 **LangSmith 추적**: (선택) 대화 흐름 모니터링

### 챗봇 워크플로우

```
사용자 질문
    ↓
키워드 추출 (LLM)
    ↓
문서 검색 (Vector DB)
    ↓
신뢰도 계산
    ↓
답변 생성 (LLM) or Fallback
    ↓
사용자에게 응답
```

## 챗봇 작동 방식

### 1. 키워드 추출
사용자의 질문에서 핵심 키워드를 LLM을 사용하여 추출합니다.

```python
"두 분은 어떻게 만나셨나요?" 
→ ["만남", "첫 만남", "처음"]
```

### 2. 벡터 검색
추출된 키워드로 Chroma 벡터 데이터베이스에서 관련 문서를 검색합니다.

### 3. 신뢰도 계산
검색된 문서의 개수와 관련성을 바탕으로 신뢰도를 계산합니다.

```python
confidence = min(0.8, num_docs * 0.3)
should_fallback = confidence < 0.3
```

### 4. 답변 생성
- 신뢰도가 높으면: 검색된 컨텍스트를 바탕으로 답변 생성
- 신뢰도가 낮으면: 사전 정의된 fallback 메시지 반환

## 지식베이스 작성하기

지식베이스는 `config/couple_knowledge.json` 파일에 JSON 형식으로 작성합니다.

### 기본 구조

```json
[
  {
    "id": "unique_identifier",
    "topic": "주제 이름",
    "content": "실제 답변 내용"
  }
]
```

### 작성 가이드

#### 1. 필수 정보

**첫 만남**
```json
{
  "id": "first_meeting",
  "topic": "첫 만남",
  "content": "2018년 대학교에서 '모바일 프로그래밍' 수업을 통해 처음 만났어요."
}
```

**사귄 날**
```json
{
  "id": "start_date",
  "topic": "사귄 날",
  "content": "2019년 5월 5일 어린이날에 사귀기 시작했어요! 💕"
}
```

**프러포즈**
```json
{
  "id": "proposal",
  "topic": "프러포즈",
  "content": "2025년 2월에 신부 집에서 저녁을 먹다가 신랑이 프로포즈했어요. 신랑은 떨려서 실수도 많이 했고, 신부는 전혀 예상하지 못했답니다."
}
```

**신혼여행**
```json
{
  "id": "honeymoon",
  "topic": "신혼여행",
  "content": "두바이, 몰디브, 싱가포르 3개국을 여행할 예정이에요! 결혼식 다음날 출발합니다. ✈️"
}
```

#### 2. 개인 정보

**취미**
```json
{
  "id": "hobbies_groom",
  "topic": "신랑 취미",
  "content": "신랑은 코딩하는 것을 좋아하고, 독서와 영화 감상을 즐겨요."
},
{
  "id": "hobbies_bride",
  "topic": "신부 취미",
  "content": "신부는 요리와 베이킹을 좋아하고, 여행 다니는 것을 즐겨요."
}
```

**직업**
```json
{
  "id": "job_groom",
  "topic": "신랑 직업",
  "content": "신랑은 AI 엔지니어로 튜닙이라는 스타트업에서 일하고 있어요."
},
{
  "id": "job_bride",
  "topic": "신부 직업",
  "content": "신부는 제일기획에서 데이터 분석과 마케팅 전략 업무를 담당하고 있어요."
}
```

#### 3. 결혼식 정보

**결혼식 장소**
```json
{
  "id": "wedding_venue",
  "topic": "결혼식 장소",
  "content": "2026년 5월 17일 오후 2시에 라시따시어터에서 결혼식을 진행해요. 주소는 서울특별시 서초구 매헌로 16 1층입니다."
}
```

**드레스 코드**
```json
{
  "id": "dress_code",
  "topic": "드레스 코드",
  "content": "편안하고 단정한 복장으로 참석해주시면 됩니다. 특별한 드레스 코드는 없어요!"
}
```

#### 4. 재미있는 에피소드

**첫 데이트**
```json
{
  "id": "first_date",
  "topic": "첫 데이트",
  "content": "2019년 중간고사 끝나고 개봉한 어벤져스 영화를 같이 보러 갔어요! 💕"
}
```

**기억에 남는 순간**
```json
{
  "id": "memorable_moment",
  "topic": "기억에 남는 순간",
  "content": "작년 파리 여행이 가장 기억에 남아요. 에펠탑 앞에서 찍은 사진들이 지금 청첩장에 들어간 스냅 사진이에요!"
}
```

### 작성 팁

#### ✅ 좋은 예시

**자연스러운 말투**
```json
{
  "content": "2018년 대학교에서 처음 만났어요. 같은 수업을 들었는데, 팀 프로젝트를 같이 하게 되면서 친해졌답니다!"
}
```

**이모지 활용**
```json
{
  "content": "신혼여행은 두바이, 몰디브, 싱가포르를 다녀올 예정이에요! ✈️ 정말 기대돼요!"
}
```

**구체적인 정보**
```json
{
  "content": "2019년 5월 5일 어린이날에 사귀기 시작했어요. 벌써 7년이 됐네요!"
}
```

#### ❌ 피해야 할 예시

**너무 딱딱한 말투**
```json
{
  "content": "2018년에 만남. 대학교 수업에서 알게 됨."
}
```

**불명확한 정보**
```json
{
  "content": "언젠가 만났어요. 정확히 기억은 안나요."
}
```

**너무 긴 문장**
```json
{
  "content": "우리는 2018년 대학교 1학기에 모바일 프로그래밍이라는 수업을 들었는데 그 수업에서 팀 프로젝트를 같이 하게 되었고 그때부터 친해지기 시작했고 나중에는 더 친해져서 같이 밥도 먹고 영화도 보러 다니다가 결국 사귀게 되었어요."
}
```

### 완전한 예시

```json
[
  {
    "id": "first_meeting",
    "topic": "첫 만남",
    "content": "2018년 대학교 21살 신부와 24살 신랑이 '모바일 프로그래밍'이란 수업에서 처음 만났어요."
  },
  {
    "id": "first_date",
    "topic": "첫 데이트",
    "content": "첫 데이트는 2019년에 중간고사를 끝내고 당시에 개봉했던 어벤져스를 같이 보러 갔어요! 💕"
  },
  {
    "id": "start_date",
    "topic": "사귄 날",
    "content": "2019년 5월 5일 어린이날에 사귀기 시작했어요!"
  },
  {
    "id": "proposal",
    "topic": "프러포즈",
    "content": "2025년 2월에 신부 집에서 같이 저녁을 먹다가 신랑이 프로포즈를 했어요. 신랑은 떨려서 여러 실수도 했고, 신부는 전혀 예상 못한 상황이었답니다."
  },
  {
    "id": "honeymoon",
    "topic": "신혼여행",
    "content": "신혼여행은 두바이, 몰디브, 싱가포르 3개국을 다녀오기로 했어요. 결혼 다음날 출발하는 일정이에요! ✈️"
  },
  {
    "id": "age",
    "topic": "나이",
    "content": "신랑은 95년생, 신부는 98년생이에요. (2026년 기준 한국 나이로 신랑 32세, 신부 29세)"
  },
  {
    "id": "job_groom",
    "topic": "신랑 직업",
    "content": "신랑은 AI 엔지니어예요. 현재는 '튜닙'이라는 스타트업 공동창업자로 일하고 있어요."
  },
  {
    "id": "job_bride",
    "topic": "신부 직업",
    "content": "신부는 '제일기획'에서 데이터 분석과 마케팅 전략 업무를 담당하고 있어요."
  },
  {
    "id": "wedding_venue",
    "topic": "결혼식 장소",
    "content": "결혼식은 2026년 5월 17일 오후 2시에 라시따시어터에서 진행돼요. 주소는 서울특별시 서초구 매헌로 16 1층이에요."
  }
]
```

## 프롬프트 커스터마이징

챗봇의 말투와 성격은 `app/chatbot/prompts.json` 파일에서 설정할 수 있습니다.

### 프롬프트 구조

```json
{
  "keyword_extraction": {
    "system": "키워드 추출 시스템 프롬프트",
    "user_template": "사용자 메시지 템플릿"
  },
  "chatbot_response": {
    "system_template": "챗봇 응답 시스템 프롬프트",
    "user_template": "사용자 질문 템플릿"
  },
  "messages": {
    "fallback": "정보가 없을 때 메시지",
    "error": "오류 발생 시 메시지"
  }
}
```

### 챗봇 성격 설정

`chatbot_response.system_template` 섹션을 수정하여 챗봇의 성격을 변경할 수 있습니다.

#### 예시 1: 친근하고 귀여운 말투 (기본)
```json
{
  "system_template": "당신은 {groom_name}님과 {bride_name}님의 결혼식을 위한 AI 도우미입니다.\n\n성격:\n- 친근하고 귀여운 말투를 사용합니다\n- 이모지를 적절히 활용합니다\n- 존댓말을 사용하되 너무 딱딱하지 않게 합니다\n\n답변 가이드라인:\n- 제공된 정보를 바탕으로 정확하게 답변합니다\n- 답변은 2-3문장 정도로 적당한 길이로 합니다\n\n관련 정보:\n{context}"
}
```

#### 예시 2: 격식있고 우아한 말투
```json
{
  "system_template": "당신은 {groom_name}님과 {bride_name}님의 결혼식 안내를 담당하는 AI 도우미입니다.\n\n성격:\n- 격식있고 우아한 말투를 사용합니다\n- 정중하고 예의바른 어조를 유지합니다\n- 축하와 존경의 마음을 담아 답변합니다\n\n답변 가이드라인:\n- 명확하고 정확한 정보를 제공합니다\n- 간결하면서도 따뜻한 답변을 작성합니다\n\n관련 정보:\n{context}"
}
```

#### 예시 3: 재미있고 유머러스한 말투
```json
{
  "system_template": "당신은 {groom_name}님과 {bride_name}님의 즐거운 결혼식 가이드입니다! 😄\n\n성격:\n- 유머러스하고 재미있는 말투 사용\n- 이모지를 많이 활용해서 생동감 있게 표현\n- 친구처럼 편안하고 재미있게 대화\n\n답변 가이드라인:\n- 정보는 정확하게, 표현은 재미있게!\n- 적절한 농담과 유머를 섞어서\n- 하객들이 즐겁게 읽을 수 있도록\n\n관련 정보:\n{context}"
}
```

### Fallback 메시지 커스터마이징

정보가 없을 때 표시되는 메시지를 수정할 수 있습니다.

```json
{
  "messages": {
    "fallback": "죄송해요 😅 해당 질문에 대한 정보가 없네요 😢 다른 궁금한 것이 있으시면 언제든 물어보세요!",
    "error": "앗! 잠시 문제가 생겼네요 😅 조금 후에 다시 시도해주세요!",
    "thinking": "생각하고 있어요... 🤔"
  }
}
```

### 추천 질문 설정

`config.json` 파일의 `content.chatbot.welcome.suggested_questions` 섹션에서 추천 질문을 설정할 수 있습니다.

```json
{
  "content": {
    "chatbot": {
      "welcome": {
        "suggested_questions": [
          "두 분은 어떻게 만나셨나요?",
          "첫 데이트는 어디서 하셨어요?",
          "신혼여행은 어디로 가세요?",
          "취미가 뭐예요?"
        ]
      }
    }
  }
}
```

## 고급 설정

### 환경변수 설정

`.env` 파일에서 챗봇 관련 설정을 조정할 수 있습니다.

```bash
# OpenAI 설정
OPENAI_API_KEY=your_api_key
CHAT_MODEL=gpt-4o-mini              # 또는 gpt-4, gpt-3.5-turbo
CHAT_TEMPERATURE=0.7                # 0.0 (정확) ~ 1.0 (창의적)
MAX_TOKENS=300                      # 최대 응답 길이

# 임베딩 설정
EMBEDDING_MODEL=text-embedding-3-small  # 또는 text-embedding-3-large

# 검색 설정
TOP_K_RESULTS=3                     # 검색할 문서 개수

# LangSmith 추적 (선택)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=wedding-chatbot
```

### 모델 선택 가이드

#### GPT-4o-mini (기본, 권장)
- **장점**: 빠르고 저렴
- **단점**: 복잡한 질문에 약간 부족할 수 있음
- **비용**: $0.15 / 1M tokens (입력)
- **추천**: 대부분의 경우 충분

#### GPT-4
- **장점**: 가장 정확하고 자연스러운 답변
- **단점**: 느리고 비쌈
- **비용**: $5.00 / 1M tokens (입력)
- **추천**: 프리미엄 경험을 원할 때

#### GPT-3.5-turbo
- **장점**: 매우 빠르고 저렴
- **단점**: 답변 품질이 다소 떨어질 수 있음
- **비용**: $0.50 / 1M tokens (입력)
- **추천**: 예산이 매우 제한적일 때

### Temperature 설정

```bash
CHAT_TEMPERATURE=0.7  # 기본값
```

- **0.0-0.3**: 매우 정확하고 일관된 답변 (추천)
- **0.4-0.6**: 정확하면서도 약간의 창의성
- **0.7-1.0**: 창의적이지만 일관성이 떨어질 수 있음

### 검색 문서 개수 (TOP_K)

```bash
TOP_K_RESULTS=3  # 기본값
```

- **1-2**: 빠르지만 정보가 부족할 수 있음
- **3-5**: 적절한 균형 (권장)
- **6-10**: 느리지만 더 많은 컨텍스트

### LangSmith 추적 설정

LangSmith를 사용하면 챗봇의 동작을 상세하게 모니터링할 수 있습니다.

1. [LangSmith](https://smith.langchain.com/) 가입
2. API 키 생성
3. `.env` 파일에 추가

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=my-wedding-chatbot
```

LangSmith 대시보드에서 확인할 수 있는 정보:
- 각 대화의 전체 흐름
- LLM 호출 횟수 및 비용
- 검색된 문서 내용
- 응답 시간 분석

## 문제 해결

### 챗봇이 응답하지 않아요

**원인 1: OpenAI API 키 오류**
```bash
# .env 파일 확인
OPENAI_API_KEY=sk-...  # 올바른 API 키인지 확인
```

**원인 2: 네트워크 오류**
```bash
# 로그 확인
python main.py
# 콘솔에서 에러 메시지 확인
```

**원인 3: 지식베이스가 비어있음**
```json
// config/couple_knowledge.json 파일 확인
// 최소 5-10개의 항목이 있는지 확인
```

### 챗봇이 엉뚱한 답변을 해요

**해결 1: 지식베이스 개선**
- 더 구체적이고 명확한 내용 작성
- 관련 키워드를 포함
- 중복되는 정보 정리

**해결 2: Temperature 낮추기**
```bash
CHAT_TEMPERATURE=0.3  # 더 정확한 답변
```

**해결 3: 프롬프트 개선**
```json
{
  "system_template": "... 반드시 제공된 정보만을 바탕으로 답변하세요. 추측하거나 지어내지 마세요. ..."
}
```

### 챗봇 응답이 너무 느려요

**해결 1: 모델 변경**
```bash
CHAT_MODEL=gpt-3.5-turbo  # 더 빠른 모델
```

**해결 2: 문서 개수 줄이기**
```bash
TOP_K_RESULTS=2  # 검색 문서 감소
```

**해결 3: 최대 토큰 수 줄이기**
```bash
MAX_TOKENS=200  # 더 짧은 답변
```

### 챗봇 비용이 너무 많이 나와요

**해결 1: 저렴한 모델 사용**
```bash
CHAT_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
```

**해결 2: 최대 토큰 수 제한**
```bash
MAX_TOKENS=200  # 비용 절감
```

**해결 3: 캐싱 활용**
- 자주 묻는 질문에 대한 답변을 캐싱
- (고급) Redis 등 캐시 서버 연동

### Fallback 메시지가 너무 자주 나와요

**해결 1: 지식베이스 확장**
- 더 다양한 주제의 정보 추가
- 같은 주제를 다른 표현으로 여러 개 추가

**해결 2: 신뢰도 임계값 낮추기**
```python
# app/chatbot/chatbot.py 수정
should_fallback = confidence < 0.2  # 0.3에서 0.2로 변경
```

**해결 3: TOP_K 늘리기**
```bash
TOP_K_RESULTS=5  # 더 많은 문서 검색
```

## 테스트 및 개선

### 1. 로컬에서 테스트

```bash
# 서버 실행
python main.py

# 브라우저에서 테스트
http://localhost:8000
```

### 2. 다양한 질문 테스트

다음과 같은 질문들로 테스트해보세요:

- "두 분은 어떻게 만나셨나요?"
- "첫 데이트 장소는 어디예요?"
- "신랑 취미가 뭐예요?"
- "언제 결혼하시나요?"
- "신혼여행 어디로 가세요?"

### 3. 피드백 수집

실제 하객들의 피드백을 받아 개선:

1. 어떤 질문이 많이 들어오는지 파악
2. 답변이 부족한 부분 보완
3. 말투나 이모지 사용 조정

## 다음 단계

- [설정 가이드](./CONFIGURATION.ko.md) - 청첩장 전체 설정
- [커스터마이징 가이드](./CUSTOMIZATION.ko.md) - 디자인 및 기능 커스터마이징
- [FAQ](./FAQ.ko.md) - 자주 묻는 질문

## 도움이 필요하신가요?

- 📧 [이메일 문의](mailto:your.email@example.com)
- 💬 [디스코드 커뮤니티](https://discord.gg/your-server)
- 🐛 [GitHub Issues](https://github.com/yourusername/wedding-invitation/issues)