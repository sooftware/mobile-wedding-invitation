/**
 * 챗봇 클라이언트 사이드 JavaScript
 * 사용자 인터페이스 및 API 통신 처리
 */

class WeddingChatbot {
    constructor() {
        this.chatArea = null;
        this.chatInput = null;
        this.sendButton = null;
        this.isLoading = false;
        this.messageId = 0;
        this.config = null;
        this.chatHistory = [];  // 대화 히스토리 추적
        this.threadId = this.generateThreadId();  // 세션별 고유 ID

        this.init();
    }

    generateThreadId() {
        // 세션별 고유 ID 생성 (타임스탬프 + 랜덤)
        return `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    init() {
        console.log('🤖 챗봇 초기화 시작'); // 디버깅 로그 추가
        // Config 로드
        this.loadConfig();

        // DOM 요소 찾기
        this.chatArea = document.getElementById('chat-area');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('chat-send-button');

        console.log('📋 DOM 요소 찾기 결과:', {
            chatArea: !!this.chatArea,
            chatInput: !!this.chatInput,
            sendButton: !!this.sendButton
        }); // 디버깅 로그 추가

        if (!this.chatArea || !this.chatInput || !this.sendButton) {
            console.error('챗봇 DOM 요소를 찾을 수 없습니다.');
            return;
        }

        // 이벤트 리스너 등록
        this.setupEventListeners();

        // 초기 상태 설정
        this.showWelcomeMessage();

        console.log('✅ 챗봇 초기화 완료'); // 디버깅 로그 추가
    }

    loadConfig() {
        const configElement = document.getElementById('config-data');
        if (configElement) {
            this.config = JSON.parse(configElement.textContent);
        } else {
            console.error('Config data not found');
        }
    }

    setupEventListeners() {
        // 전송 버튼 클릭
        this.sendButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Enter 키 전송 (컴퓨터에서는 Enter만 전송, 줄바꿈 없음)
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                // 항상 기본 동작 방지 (줄바꿈 방지)
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 입력창 자동 크기 조절
        this.chatInput.addEventListener('input', () => {
            this.adjustInputHeight();
        });

        // 추천 질문 클릭
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggested-question') ||
                e.target.classList.contains('example-question')) {
                this.handleSuggestedQuestion(e.target.textContent.trim());
            }
        });
    }

    adjustInputHeight() {
        this.chatInput.style.height = 'auto';
        const newHeight = Math.min(this.chatInput.scrollHeight, 120);
        this.chatInput.style.height = newHeight + 'px';
    }

    showWelcomeMessage() {
        if (!this.config) {
            console.error('Config not loaded');
            return;
        }

        const chatbotConfig = this.config.content.chatbot;
        const groomName = this.config.wedding.groom.display_name;
        const brideName = this.config.wedding.bride.display_name;

        // 인사말에 이름 치환
        const greeting = chatbotConfig.welcome.greeting
            .replace('{groom_name}', groomName)
            .replace('{bride_name}', brideName);

        const welcomeHTML = `
            <div class="empty-chat">
                <div class="empty-chat-text">
                    ${greeting}<br>
                </div>
                <div class="suggested-questions">
                    ${chatbotConfig.welcome.suggested_questions.map(question => 
                        `<div class="suggested-question">${question}</div>`
                    ).join('')}
                </div>
            </div>
        `;

        this.chatArea.innerHTML = welcomeHTML;
    }

    handleSuggestedQuestion(question) {
        this.chatInput.value = question;
        this.sendMessage();
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();
        console.log('📤 메시지 전송 시도:', message); // 디버깅 로그 추가

        if (!message || this.isLoading) {
            console.log('❌ 메시지가 비어있거나 로딩 중'); // 디버깅 로그 추가
            return;
        }

        console.log('✅ 메시지 전송 진행'); // 디버깅 로그 추가

        // 빈 채팅 상태면 초기화
        if (this.chatArea.querySelector('.empty-chat')) {
            this.chatArea.innerHTML = '';
        }

        // 사용자 메시지 표시
        this.addMessage(message, 'user');

        // 대화 히스토리에 사용자 메시지 추가
        this.chatHistory.push({
            role: 'user',
            content: message
        });

        // 입력창 초기화
        this.chatInput.value = '';
        this.adjustInputHeight();

        // 로딩 상태 시작
        this.setLoading(true);
        this.showTypingIndicator();

        try {
            // API 호출 (대화 히스토리 포함)
            const response = await this.callChatbotAPI(message);

            // 타이핑 인디케이터 제거
            this.hideTypingIndicator();

            if (response.success) {
                // 봇 응답 표시
                this.addMessage(response.response, 'bot');

                // 대화 히스토리에 봇 응답 추가
                this.chatHistory.push({
                    role: 'assistant',
                    content: response.response
                });
            } else {
                // 에러 메시지 표시
                const errorMsg = response.response ||
                    (this.config?.content?.chatbot?.error_message ||
                     '죄송해요 😅 문제가 발생했네요. 다시 시도해주세요!');
                this.addMessage(errorMsg, 'bot');
            }

        } catch (error) {
            console.error('챗봇 API 호출 실패:', error);
            this.hideTypingIndicator();

            const errorMsg = this.config?.content?.chatbot?.error_message ||
                '앗! 잠시 문제가 생겼네요 😅 조금 후에 다시 시도해주세요!';
            this.addMessage(errorMsg, 'bot');
        } finally {
            this.setLoading(false);
        }
    }

    async callChatbotAPI(message) {
        console.log('🌐 API 호출 시작:', message); // 디버깅 로그 추가

        // 현재 사용자 메시지를 제외한 이전 대화 히스토리만 전송
        const previousHistory = this.chatHistory.slice(0, -1);

        console.log('📜 대화 히스토리:', previousHistory); // 디버깅 로그 추가

        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                chat_history: previousHistory,
                thread_id: this.threadId
            })
        });

        console.log('📡 API 응답 상태:', response.status); // 디버깅 로그 추가

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('📥 API 응답 데이터:', result); // 디버깅 로그 추가

        return result;
    }

    addMessage(text, sender) {
        const messageId = ++this.messageId;
        const timestamp = this.formatTimestamp(new Date());

        const messageHTML = `
            <div class="message-bubble ${sender}" data-message-id="${messageId}">
                <div class="message-text">${text}</div>
                <div class="message-time">${timestamp}</div>
            </div>
        `;

        this.chatArea.insertAdjacentHTML('beforeend', messageHTML);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const thinkingMsg = this.config?.content?.chatbot?.thinking_message || '생각하고 있어요...';

        const typingHTML = `
            <div class="typing-indicator" id="typing-indicator">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <div class="typing-text">${thinkingMsg}</div>
            </div>
        `;

        this.chatArea.insertAdjacentHTML('beforeend', typingHTML);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    setLoading(isLoading) {
        this.isLoading = isLoading;
        this.sendButton.disabled = isLoading;
        this.chatInput.disabled = isLoading;

        if (isLoading) {
            this.sendButton.innerHTML = '<i data-lucide="loader-2" class="animate-spin"></i>';
        } else {
            this.sendButton.innerHTML = '<i data-lucide="send"></i>';
        }

        // Lucide 아이콘 다시 초기화
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    scrollToBottom() {
        // 부드러운 스크롤
        setTimeout(() => {
            this.chatArea.scrollTo({
                top: this.chatArea.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }

    formatTimestamp(date) {
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / (1000 * 60));

        if (diffMins < 1) {
            return '방금 전';
        } else if (diffMins < 60) {
            return `${diffMins}분 전`;
        } else {
            const hours = date.getHours();
            const minutes = date.getMinutes();
            const ampm = hours >= 12 ? '오후' : '오전';
            const displayHours = hours % 12 || 12;
            const displayMinutes = minutes.toString().padStart(2, '0');
            return `${ampm} ${displayHours}:${displayMinutes}`;
        }
    }
}

// 전역 챗봇 인스턴스
let weddingChatbot;

// 챗봇 초기화 함수
function initializeChatbot() {
    weddingChatbot = new WeddingChatbot();
}

// DOM 로드 완료 후 초기화
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChatbot);
} else {
    initializeChatbot();
}

// CSS 애니메이션 클래스 추가 - 변수명 충돌 방지
const chatbotStyle = document.createElement('style');
chatbotStyle.textContent = `
    .animate-spin {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(chatbotStyle);