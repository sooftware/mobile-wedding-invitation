📋 Wedding Chatbot RAG 시스템 플로우

```
┌─────────────────────────────────────────────────────────────────┐
│                         사용자 질문 입력                          │
│                    "신혼여행은 어디로 가세요?"                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   1. Extract Keywords Node    │
         │   (LLM으로 키워드 추출)       │
         │   → ["신혼여행", "여행"]      │
         └───────────┬───────────────────┘
                     │ ❌ 실패?
                     ├──────────┐
                     │          ▼
                     │    [Retry Handler]
                     │    (2초 대기 → 재시도)
                     │          │
                     │◄─────────┘
                     │ ✅ 성공
                     ▼
         ┌───────────────────────────────┐
         │  2. Retrieve Documents Node   │
         │  (Chroma Vector Search)       │
         │  → 유사도 검색 (Top 3)        │
         │  → ["신혼여행", "신혼집", ...] │
         └───────────┬───────────────────┘
                     │ ❌ 실패?
                     ├──────────┐
                     │          ▼
                     │    [Retry Handler]
                     │    (4초 대기 → 재시도)
                     │          │
                     │◄─────────┘
                     │ ✅ 성공
                     ▼
         ┌───────────────────────────────┐
         │ 3. Calculate Confidence Node  │
         │ (신뢰도 계산)                 │
         │ confidence = min(0.8, 3*0.3)  │
         │ → 0.8 (높음)                  │
         └───────────┬───────────────────┘
                     │
                     ▼
              [신뢰도 체크]
           confidence >= 0.3?
                     │
         ┌───────────┴───────────┐
         │                       │
    YES  │                  NO   │
         ▼                       ▼
┌────────────────────┐   ┌──────────────────┐
│ 4. Generate        │   │ 5. Fallback      │
│    Response Node   │   │    Response Node │
│ (LLM 응답 생성)    │   │                  │
│                    │   │ "죄송해요 😅     │
│ Context + 프롬프트 │   │  해당 질문에     │
│ → LLM (GPT-4o)     │   │  대한 정보가     │
│ → "신혼여행은 아직 │   │  없네요 😢"      │
│    결정 안됐어요"  │   │                  │
└──────┬─────────────┘   └────────┬─────────┘
       │ ❌ 실패?                  │
       ├──────────┐                │
       │          ▼                │
       │    [Retry Handler]        │
       │    (8초 대기 → 재시도)    │
       │          │                │
       │◄─────────┘                │
       │ ✅ 성공                   │
       ▼                           │
       └───────────┬───────────────┘
                   ▼
         ┌─────────────────────┐
         │    최종 응답 반환    │
         │                     │
         │ {                   │
         │   success: true,    │
         │   response: "...",  │
         │   confidence: 0.8,  │
         │   retry_count: 0    │
         │ }                   │
         └─────────────────────┘
```

🔄 재시도 메커니즘 (각 노드별)

Extract Keywords ─┐
                  │
Retrieve Docs ────┼─ 실패 시 ─→ Retry Handler
                  │              (지수 백오프)
Generate Response─┘              1회: 2초
                                 2회: 4초
                                 3회: 8초
                                 ↓
                            최대 3회 초과 시
                                 ↓
                            Fallback Response


🛡️ 안전 장치

1. Recursion Limit: 25 (최대 25단계)
2. Timeout: 60초 (60초 초과 시 중단)
3. Max Retries: 3 (최대 3회 재시도)
4. Error Handling: 모든 노드에 try-except


📊 상태 추적 (State)

ChatbotState {
  query: "신혼여행은 어디로 가세요?",
  keywords: ["신혼여행"],
  retrieved_docs: [Doc1, Doc2, Doc3],
  matched_topics: ["신혼여행", "신혼집"],
  confidence: 0.8,
  should_fallback: false,
  response: "신혼여행은 아직...",
  error: null,
  retry_count: 0,
  failed_nodes: []
}


🔍 LangSmith 트레이싱

chat (전체 2.1초)
├─ extract_keywords (0.5초) ✅
├─ retrieve_documents (0.3초) ✅
├─ calculate_confidence (0.01초) ✅
└─ generate_response (1.2초) ✅

→ 모든 단계가 LangSmith에 기록됨