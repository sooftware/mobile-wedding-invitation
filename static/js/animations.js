/* =========================
   청첩장 오프닝 애니메이션 JavaScript
   static/js/animations.js
========================= */

// 스크롤 애니메이션 관리자
class WeddingAnimationManager {
    constructor() {
        this.scrollElements = [];
        this.petalRain = null;
        this.introShown = false;
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // 입장 애니메이션이 먼저 실행되고, 완료 후 다른 애니메이션 시작
        this.initIntroAnimation();
    }

    // 손글씨 애니메이션을 위한 Vara.js 초기화
    initHandwritingAnimation() {
        const container = document.getElementById('vara-container');
        if (!container) {
            console.warn('Vara container not found');
            return;
        }
        
        // 기존 내용 제거
        container.innerHTML = '';

        // 화면 크기에 따른 폰트 사이즈 조정
        const isMobile = window.innerWidth <= 768;
        const fontSize = isMobile ? 50 : 90;
        const strokeWidth = isMobile ? 1.5 : 2;

        // 텍스트 설정
        // y값은 fromCurrentPosition이 false일 경우 절대 좌표, true일 경우 이전 위치로부터의 상대 좌표입니다.
        // fromCurrentPosition: { y: false }로 설정하고 절대 좌표(y)를 직접 지정하여 줄 간격을 제어합니다.

        // 줄 간격 설정
        const lineHeight = fontSize * 1.2;
        const startY = 50; // 시작 Y 위치

        // 대각선 배치를 위한 x 오프셋 (오른쪽으로 갈수록 증가)
        const diagonalShift = isMobile ? 15 : 30; // 각 줄마다 오른쪽으로 이동하는 거리

        const texts = [
            {
                text: "We're",
                fontSize: fontSize,
                strokeWidth: strokeWidth,
                color: '#fff',
                duration: 700,  // 빠르게 쓰기
                textAlign: 'center',
                x: -diagonalShift,  // 왼쪽으로 시작
                y: startY,
                fromCurrentPosition: { x: false, y: false }
            },
            {
                text: 'getting',
                fontSize: fontSize,
                strokeWidth: strokeWidth,
                color: '#fff',
                duration: 700,  // 빠르게 쓰기
                textAlign: 'center',
                x: 0,  // 중앙
                y: startY + lineHeight,
                fromCurrentPosition: { x: false, y: false }
            },
            {
                text: 'married!',
                fontSize: fontSize,
                strokeWidth: strokeWidth,
                color: '#fff',
                duration: 400,  // 더 빠르게 쫙 써지도록
                textAlign: 'center',
                x: diagonalShift,  // 오른쪽으로
                y: startY + (lineHeight * 2),
                fromCurrentPosition: { x: false, y: false }
            }
        ];

        // Vara 인스턴스 생성
        try {
            if (typeof Vara === 'undefined') {
                console.error('Vara.js library not loaded');
                return;
            }

            // 컨테이너 강제 노출 (계산 위해)
            // Vara.js는 container가 보여야(display: none이 아니어야) 올바르게 초기화됨
            // opacity나 visibility로 숨겨져 있어도 display가 block이면 계산 가능
            
            const vara = new Vara(
                '#vara-container',
                '/static/assets/fonts/json/Parisienne.json',
                texts,
                {
                    strokeWidth: strokeWidth,
                    fontSize: fontSize,
                    textAlign: 'center',
                    autoAnimation: false // 자동 시작 방지 (이벤트 기반 시작을 위해)
                }
            );
            
            // 애니메이션 준비 완료 로그 및 이벤트 바인딩
            vara.ready(() => {
                console.log('Vara.js 애니메이션 준비 완료');

                // 컨테이너 내의 SVG 스타일 조정 (중앙 정렬 보정)
                const svgs = container.querySelectorAll('svg');
                svgs.forEach(svg => {
                    svg.style.overflow = 'visible';
                });

                // 준비 완료 신호 발송 (전역 변수 또는 이벤트)
                window.isVaraReady = true;
                document.dispatchEvent(new Event('vara-ready'));

                // Vara 인스턴스 저장
                this.varaInstance = vara;

                // married 밑줄 애니메이션 준비 (나중에 실행됨)
                this.prepareMarriedUnderline(container, fontSize, isMobile);
            });
            
        } catch (e) {
            console.error('Vara.js 초기화 실패:', e);
        }

        console.log('필기체 애니메이션(Vara.js) 초기화 완료');
    }

    // married 텍스트 밑줄 애니메이션 준비
    prepareMarriedUnderline(container, fontSize, isMobile) {
        // married 텍스트의 SVG가 그려진 후에 밑줄을 추가하기 위한 준비
        // 이 함수는 Vara ready 콜백에서 호출되지만, 실제 밑줄 그리기는
        // married 텍스트 애니메이션이 완료된 후에 시작됨
        this.underlineContainer = container;
        this.underlineFontSize = fontSize;
        this.underlineIsMobile = isMobile;
    }

    // married 밑줄 애니메이션 시작
    startMarriedUnderline() {
        if (!this.underlineContainer) {
            console.warn('밑줄 컨테이너가 준비되지 않았습니다.');
            return;
        }

        const container = this.underlineContainer;
        const fontSize = this.underlineFontSize;
        const isMobile = this.underlineIsMobile;

        // Vara.js는 하나의 SVG 안에 모든 텍스트를 그룹으로 생성
        const svg = container.querySelector('svg');
        if (!svg) {
            console.warn('SVG를 찾을 수 없습니다.');
            return;
        }

        console.log('SVG 찾음:', svg);

        // 모든 path 요소를 찾아서 married 텍스트의 path들 확인
        const allPaths = svg.querySelectorAll('path');
        console.log('전체 path 개수:', allPaths.length);

        if (allPaths.length === 0) {
            console.warn('path를 찾을 수 없습니다.');
            return;
        }

        // married 텍스트의 bounding box 계산
        // Vara.js는 각 텍스트를 순서대로 그리므로, 마지막 부분의 path들이 married
        // 전체 SVG의 viewBox나 bounding box를 사용하여 밑줄 위치 계산

        let marriedBBox;
        try {
            // SVG 전체의 bbox를 구하고, married가 있을 위치(아래쪽)에 밑줄 그리기
            const svgBBox = svg.getBBox();
            console.log('SVG BBox:', svgBBox);

            // married는 세 번째 줄이므로, 전체 높이의 2/3 지점 이후
            const lineHeight = fontSize * 1.2;
            const startY = 50;
            const marriedY = startY + (lineHeight * 2);

            // married 텍스트의 예상 위치와 크기
            marriedBBox = {
                x: svgBBox.x,
                y: marriedY,
                width: svgBBox.width,
                height: fontSize
            };
        } catch (e) {
            console.error('BBox 계산 실패:', e);
            return;
        }

        // 밑줄 위치 계산 (텍스트 바로 아래, 살짝 올라가는 느낌)
        const baseY = marriedBBox.y + marriedBBox.height + (isMobile ? 8 : 12);

        // married 텍스트도 대각선 배치되어 있으므로 x 위치 조정
        const diagonalShift = isMobile ? 15 : 30;
        const underlineStartX = marriedBBox.x + diagonalShift - 10;  // 약간 왼쪽에서 시작
        const underlineEndX = marriedBBox.x + marriedBBox.width + diagonalShift + 10;  // 약간 오른쪽까지

        console.log('밑줄 위치:', { baseY, underlineStartX, underlineEndX });

        // 두 줄 밑줄 생성 (각도가 다른)
        const createUnderline = (yOffset, delay, angleOffset) => {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', underlineStartX);
            line.setAttribute('y1', baseY + yOffset);  // 왼쪽 시작점
            line.setAttribute('x2', underlineEndX);
            line.setAttribute('y2', baseY + yOffset - angleOffset);  // 오른쪽은 살짝 올라감
            line.setAttribute('stroke', '#fff');
            line.setAttribute('stroke-width', isMobile ? '1.5' : '2');
            line.setAttribute('stroke-linecap', 'round');

            // stroke-dasharray/dashoffset을 사용한 애니메이션 준비
            const lineLength = Math.sqrt(
                Math.pow(underlineEndX - underlineStartX, 2) +
                Math.pow(angleOffset, 2)
            );
            line.setAttribute('stroke-dasharray', lineLength);
            line.setAttribute('stroke-dashoffset', lineLength);
            line.style.filter = 'drop-shadow(0 2px 6px rgba(0, 0, 0, 0.5))';

            // SVG에 밑줄 추가
            svg.appendChild(line);

            // CSS transition 설정
            line.style.transition = 'stroke-dashoffset 0.3s cubic-bezier(0.4, 0, 0.2, 1)';

            // 딜레이 후 애니메이션 시작
            setTimeout(() => {
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        line.setAttribute('stroke-dashoffset', '0');
                    });
                });
            }, delay);

            return line;
        };

        // 애니메이션 시작
        console.log('married 밑줄 애니메이션 시작 (두 줄 쫙쫙! 서로 다른 각도)');

        // 첫 번째 밑줄 (즉시 시작, 더 완만한 각도)
        const angle1 = isMobile ? 4 : 7;
        createUnderline(0, 0, angle1);

        // 두 번째 밑줄 (약간 아래, 약간의 딜레이, 더 가파른 각도)
        const angle2 = isMobile ? 6 : 10;
        createUnderline(isMobile ? 4 : 5, 100, angle2);
    }

    // 입장 애니메이션 초기화
    initIntroAnimation() {
        const introOverlay = document.getElementById('intro-animation-overlay');

        if (!introOverlay) {
            // 입장 오버레이가 없으면 바로 다른 애니메이션 시작
            console.log('입장 오버레이를 찾을 수 없습니다. 메인 애니메이션 시작');
            this.startMainAnimations();
            return;
        }

        // 오버레이 초기화 (JS 실행 시점에 바로 block 처리하여 깜빡임 최소화)
        // CSS에서 기본적으로 숨겨져 있으나, 여기서 확실히 잡고 감
        introOverlay.style.display = 'block';
        
        // 손글씨 애니메이션 초기화 (폰트 로드 시작)
        this.initHandwritingAnimation();

        // 모바일 감지
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
                        || window.innerWidth <= 768;

        // 저전력 모드 감지
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        console.log('오프닝 애니메이션 시작 (모바일:', isMobile, ', 저전력:', prefersReducedMotion, ')');

        // 페이지 스크롤 방지
        document.body.style.overflow = 'hidden';

        // 이미지 로딩 대기
        const introImages = introOverlay.querySelectorAll('.intro-bg-image');
        let loadedImages = 0;
        const totalImages = introImages.length;
        
        // 애니메이션 시작 여부 플래그 (중복 실행 방지)
        let isAnimationStarted = false;

        const startIntroAnimation = () => {
            if (isAnimationStarted) return;
            isAnimationStarted = true;

            // 모든 준비(이미지 + 폰트)가 완료되었을 때 실행
            console.log('모든 리소스 준비 완료, 애니메이션 시작');
            
            // 오버레이 보이게 처리
            introOverlay.classList.add('ready');

            // Scene 요소 가져오기
            const scene1 = introOverlay.querySelector('.intro-scene-1');

            // 타이밍 설정 (표시 시간)
            let scene1DisplayDuration;

            if (prefersReducedMotion) {
                // 저전력 모드: 씬 표시 시간
                scene1DisplayDuration = 3000;   // 3초
                console.log('⚡ 저전력 모드 타이밍 적용');
            } else {
                // 일반 모드: 씬 표시 시간
                scene1DisplayDuration = 8500;  // 8.5초 (Vara 애니메이션 시간 고려)
                console.log('✨ 일반 속도 타이밍 적용');
            }

            console.log('오프닝 애니메이션 이벤트 기반 시작:', { scene1DisplayDuration });

            // 애니메이션 로직:
            // 1. 배경 및 텍스트 컨테이너 슬라이드 인 (CSS animation)
            // 2. 슬라이드 인 완료 후 Vara.js 재생 시작
            // 3. Vara.js 재생 완료 후 페이드 아웃

            // Vara 설정의 duration 총합 + 밑줄 애니메이션 + 여유 시간 계산
            // duration: 700 (We're) + 700 (getting) + 400 (married) + 400 (밑줄) = 2200ms
            const totalAnimationDuration = 700 + 700 + 400 + 400 + 300; // 여유 시간 300ms

            // 1. Scene 1 슬라이드인 완료 대기
            const onScene1SlideInEnd = (e) => {
                // 중복 이벤트 방지
                if (e.target !== scene1) return;
                scene1.removeEventListener('animationend', onScene1SlideInEnd);
                console.log('✅ Scene 1 슬라이드인 완료, 글씨 쓰기 시작');

                // 2. 글씨 쓰기 시작 (수동 트리거)
                if (this.varaInstance) {
                    this.varaInstance.playAll();
                } else {
                    console.warn('Vara 인스턴스가 없습니다. 자동 진행');
                }

                // 2-1. married 텍스트 완성 후 밑줄 애니메이션 시작
                // We're (700ms) + getting (700ms) + married (400ms) = 1800ms
                setTimeout(() => {
                    console.log('married 텍스트 완성, 밑줄 애니메이션 시작');
                    this.startMarriedUnderline();
                }, 1800);

                // 3. 글자 쓰는 애니메이션이 끝날 때까지 대기 (Duration 기반)
                // Vara.js의 animationEnd 이벤트를 확실히 잡기 어려우므로 duration timer 사용이 가장 안정적
                setTimeout(() => {
                    console.log('글자 쓰기 완료 직후, 페이드아웃 시작');
                    
                    // 이미지(bg-image) 페이드아웃 먼저 시작
                    const bgImage = scene1.querySelector('.intro-bg-image');
                    if(bgImage) {
                        bgImage.style.transition = 'opacity 1.0s ease-out'; // 더 빨리 사라짐
                        bgImage.style.opacity = '0';
                    }
                    
                    // 0.5초 후 글자 페이드아웃 시작
                    setTimeout(() => {
                        const textContainer = scene1.querySelector('.intro-main-text');
                        if(textContainer) {
                            textContainer.style.transition = 'opacity 1.0s ease-out'; // 더 빨리 사라지도록 시간 단축 (1.5s -> 1.0s)
                            textContainer.style.opacity = '0';
                        }
                        
                        // 3. 페이드아웃이 얼추 끝날 때쯤(0.8초 후) 오버레이 제거 및 모달 표시
                        setTimeout(() => {
                            console.log('오버레이 제거 및 모달 표시');
                            if(introOverlay) {
                                introOverlay.style.display = 'none';
                                document.body.style.overflow = '';
                                document.body.classList.remove('intro-active'); // 오프닝 상태 해제
                                this.startMainAnimations();
                                
                                // 페이드아웃 완료 후 모달 표시
                        this.showAttendanceModal();
                            }
                            
                        }, 800); // 대기 시간 단축 (1500 -> 800)
                        
                    }, 500); // 글자는 0.5초 더 있다가 사라짐 (기존 800 -> 500)
                    
                }, totalAnimationDuration);
            };

            // Scene 1 슬라이드인 애니메이션 완료 이벤트 리스너 등록
            scene1.addEventListener('animationend', onScene1SlideInEnd);
            
            // 안전장치: 만약 animationend 이벤트가 발생하지 않는 경우(모바일 등)를 대비하여 강제 실행
            setTimeout(() => {
                // 이미 실행되었는지 확인하는 로직 추가 필요하지만, 단순 타임아웃으로 처리
            }, totalAnimationDuration + 5000);

            // 폴백: 애니메이션이 멈춘 경우를 대비한 안전장치 (15초)
            setTimeout(() => {
                if (introOverlay && introOverlay.style.display !== 'none') {
                    console.log('⚠️ 오프닝 애니메이션 타임아웃, 강제 제거');
                    introOverlay.style.display = 'none';
                    document.body.style.overflow = '';
                    if (!this.scrollElements.length) {
                        this.startMainAnimations();
                    }
                    this.showAttendanceModal();
                }
            }, 15000); // 15초 타임아웃
        };

        // 리소스(이미지+폰트) 준비 체크
        const checkAllResourcesLoaded = () => {
            // 이미지가 없으면 이미지 준비된 것으로 간주
            const isImageReady = (totalImages === 0) || (loadedImages === totalImages);
            const isFontReady = window.isVaraReady === true;
            
            console.log(`리소스 상태 - 이미지: ${loadedImages}/${totalImages}, 폰트: ${isFontReady}`);
            
            if (isImageReady && isFontReady) {
                startIntroAnimation();
            }
        };

        // 이미지 로딩 완료 체크
        const checkImageLoaded = () => {
            loadedImages++;
            checkAllResourcesLoaded();
        };
        
        // 폰트 로딩 완료 이벤트 리스너
        const onVaraReady = () => {
            checkAllResourcesLoaded();
            document.removeEventListener('vara-ready', onVaraReady);
        };
        document.addEventListener('vara-ready', onVaraReady);

        // 이미 Vara가 준비되어 있는 경우 (재방문 등)
        if (window.isVaraReady) {
             checkAllResourcesLoaded();
        }

        // 이미지가 없으면 바로 폰트만 체크
        if (totalImages === 0) {
            console.log('오프닝 이미지 없음');
            checkAllResourcesLoaded();
        } else {
        // 각 이미지 로딩 대기
        introImages.forEach((img) => {
            if (img.complete) {
                // 이미 로딩된 이미지
                checkImageLoaded();
            } else {
                // 로딩 대기
                img.addEventListener('load', checkImageLoaded);
                img.addEventListener('error', () => {
                    console.warn('오프닝 이미지 로딩 실패, 계속 진행');
                    checkImageLoaded();
                });
            }
        });
        }

        // 타임아웃: 이미지/폰트 로딩이 너무 오래 걸리면 강제 시작 (2초 후)
        // 모바일 네트워크 환경 고려하되, 사용자 경험을 위해 대기 시간 단축 (3000 -> 2000)
        setTimeout(() => {
            // 아직 시작 안했으면 강제 시작
            if (!isAnimationStarted) {
                console.warn('⚠️ 리소스 로딩 타임아웃, 강제 시작');
                startIntroAnimation();
            }
        }, 2000);
    }

    // 메인 애니메이션 시작
    startMainAnimations() {
        console.log('메인 애니메이션 초기화 시작');
        this.initScrollAnimations();
        this.initCoverPetals();
        console.log('메인 애니메이션 초기화 완료');
    }

    // 참석 의사 전달 모달 표시
    showAttendanceModal() {
        // 오늘 하루 보지 않기가 설정되어 있는지 확인
        const hideUntil = localStorage.getItem('hideAttendanceNoticeUntil');
        const now = new Date().getTime();

        if (hideUntil && now < parseInt(hideUntil)) {
            console.log('참석 의사 전달 모달: 오늘 하루 보지 않기 설정됨');
            return;
        }

        // 모달 요소 가져오기
        const modal = document.getElementById('attendance-notice-modal');
        if (!modal) {
            console.warn('참석 의사 전달 모달을 찾을 수 없습니다.');
            return;
        }

        // 이미 모달이 표시되어 있으면 중복 실행 방지
        if (modal.style.display === 'flex') {
            console.log('참석 의사 전달 모달: 이미 표시됨 (중복 호출 방지)');
            return;
        }

        // 모달 표시
        modal.style.display = 'flex';
        console.log('참석 의사 전달 모달 표시됨');

        // Lucide 아이콘 재초기화
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    // 스크롤 기반 애니메이션 초기화
    initScrollAnimations() {
        const animationSelectors = [
            // 편지 섹션
            '.letter .header',
            '.letter .letter',
            '.letter .family-description',

            // 기타 섹션들
            '.calendar .d-day-display',
            '.calendar .calendar-buttons',
            '.rsvp-section .header',
            '.rsvp-section .couple-names',
            '.rsvp-section .wedding-info',
            '.rsvp-section .rsvp-button',
            '.gallery .header',
            '.gallery .photo-grid',
            '.guestbook-section .header',
            '.guestbook-section .guestbook-preview',
            '.guestbook-section .messages-section',
            '.qna-section .header',
            '.qna-section .accordion-container',
            '.location .title',
            '.location .venue',
            '.location .address-text',
            '.location .map-image-container',
            '.location .map-buttons-container',
            '.contact-section .title',
            '.contact-section .main-contacts',
            '.contact-section .parents-section',
            '.account-trapezoid h2',
            '.account-trapezoid .account-group',
            '.share-section .share-section-header',
            '.share-section .image-overlay-share',
            '.video-section .header',
            '.video-section .video-container'
        ];

        const animationElements = [];
        animationSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => animationElements.push(el));
        });

        console.log(`스크롤 애니메이션 요소 ${animationElements.length}개 발견`);

        // 각 요소에 애니메이션 클래스 추가
        animationElements.forEach((el, index) => {
            if (!el) return;

            const animationType = this.getAnimationType(el, index);
            const delay = this.getAnimationDelay(index);

            el.classList.add(animationType);
            if (delay) el.classList.add(delay);
        });

        // Intersection Observer 설정
        this.observer = new IntersectionObserver(
            (entries) => this.handleScrollAnimation(entries),
            {
                threshold: 0.15,
                rootMargin: '0px 0px -80px 0px'
            }
        );

        // 모든 애니메이션 요소 관찰 시작
        const allAnimationElements = document.querySelectorAll('.fade-in-up, .fade-in-left, .fade-in-right, .fade-in-scale, .letter-reveal');
        allAnimationElements.forEach(el => this.observer.observe(el));

        console.log(`Intersection Observer 등록 완료: ${allAnimationElements.length}개 요소`);
    }

    // 애니메이션 타입 결정
    getAnimationType(element, index) {
        if (!element || !element.className) return 'fade-in-up';

        const className = element.className;
        const tagName = element.tagName.toLowerCase();

        // 편지 섹션 특별 처리
        if (element.closest('.letter')) {
            return 'letter-reveal';
        }

        // 특정 섹션별로 다른 애니메이션 적용
        if (className.includes('header')) return 'fade-in-up';
        if (className.includes('title') || tagName === 'h2') return 'fade-in-scale';
        if (className.includes('main-contacts')) return 'fade-in-up';
        if (className.includes('couple-names')) return 'fade-in-scale';
        if (className.includes('photo-grid')) return 'fade-in-up';
        if (className.includes('map-image-container')) return 'fade-in-scale';
        if (className.includes('wedding-info')) return 'fade-in-up';
        if (className.includes('rsvp-button')) return 'fade-in-scale';
        if (className.includes('venue')) return 'fade-in-up';
        if (className.includes('address-text')) return 'fade-in-up';
        if (className.includes('video-container')) return 'fade-in-scale';

        // 좌우 번갈아가며 나타나기
        const animations = ['fade-in-up', 'fade-in-left', 'fade-in-right'];
        return animations[index % 3];
    }

    // 애니메이션 딜레이 결정
    getAnimationDelay(index) {
        // 편지 섹션은 순차적으로
        const element = document.querySelectorAll('.fade-in-up, .fade-in-left, .fade-in-right, .fade-in-scale, .letter-reveal')[index];
        if (element && element.closest('.letter')) {
            const letterElements = Array.from(element.closest('.letter').querySelectorAll('.letter-reveal'));
            const letterIndex = letterElements.indexOf(element);
            const delays = ['', 'delay-2', 'delay-4'];
            return delays[letterIndex] || '';
        }

        // 다른 섹션들은 기본 패턴
        if (index < 3) return '';
        const delays = ['delay-1', 'delay-2', 'delay-3'];
        return delays[(index - 3) % 3];
    }

    // 스크롤 애니메이션 처리
    handleScrollAnimation(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
                // 한 번 애니메이션된 요소는 더 이상 관찰하지 않음
                this.observer.unobserve(entry.target);
            }
        });
    }

    // 커버 꽃잎 효과 초기화
    initCoverPetals() {
        const coverSection = document.querySelector('.cover');
        if (!coverSection) {
            console.log('커버 섹션을 찾을 수 없습니다.');
            return;
        }

        // 꽃잎 비 컨테이너 생성
        const petalRainContainer = document.createElement('div');
        petalRainContainer.className = 'petal-rain';
        coverSection.appendChild(petalRainContainer);

        this.petalRain = new NaturalPetalRain(petalRainContainer);

        console.log('꽃잎 애니메이션 초기화 완료');

        // 페이지 로드 후 2초 뒤에 꽃잎 시작
        setTimeout(() => {
            this.petalRain.start();
            console.log('꽃잎 애니메이션 시작');
        }, 2000);
    }
}

// 자연스러운 꽃잎 비 효과 클래스 - 성능 최적화
class NaturalPetalRain {
    constructor(container) {
        this.container = container;
        this.petals = [];
        this.isActive = false;
        this.interval = null;
        this.windInterval = null;
        this.maxPetals = window.innerWidth <= 768 ? 6 : 10;
        this.petalTypes = ['cherry', 'rose', 'peony', 'carnation'];
        this.windForce = 0;
        this.rafId = null; // requestAnimationFrame ID
    }

    start() {
        if (this.isActive) return;
        this.isActive = true;

        // 바람 효과 시작
        this.startWindEffect();

        // 초기 꽃잎들을 천천히 생성
        for (let i = 0; i < 3; i++) {
            setTimeout(() => this.createPetal(), i * 1500);
        }

        // 지속적인 꽃잎 생성
        this.interval = setInterval(() => {
            if (this.petals.length < this.maxPetals) {
                this.createPetal();
            }
        }, window.innerWidth <= 768 ? 3000 : 2000);
    }

    stop() {
        if (!this.isActive) return;
        this.isActive = false;

        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }

        if (this.windInterval) {
            clearInterval(this.windInterval);
            this.windInterval = null;
        }

        if (this.rafId) {
            cancelAnimationFrame(this.rafId);
            this.rafId = null;
        }

        // 기존 꽃잎들 서서히 제거
        setTimeout(() => {
            this.container.innerHTML = '';
            this.petals = [];
        }, 5000);
    }

    createPetal() {
        const petal = document.createElement('div');
        const petalType = this.petalTypes[Math.floor(Math.random() * this.petalTypes.length)];
        petal.className = `petal ${petalType}`;

        // 시작 위치
        const startX = Math.random() * 100;
        petal.style.left = startX + '%';
        petal.style.top = '-30px';

        // 자연스러운 크기와 회전
        const scale = Math.random() * 0.6 + 0.7;
        const initialRotation = Math.random() * 360;

        // 애니메이션 시간
        const duration = Math.random() * 6 + 8; // 8-14초
        const delay = Math.random() * 2;

        petal.style.transform = `scale(${scale}) rotate(${initialRotation}deg)`;
        petal.style.animationDuration = duration + 's';
        petal.style.animationDelay = delay + 's';

        // 투명도로 깊이감 표현
        petal.style.opacity = Math.random() * 0.3 + 0.5;

        // 바람 영향
        petal.dataset.windSensitivity = Math.random() * 0.5 + 0.5;
        petal.dataset.initialX = startX;

        this.container.appendChild(petal);
        this.petals.push(petal);

        // 애니메이션 완료 후 제거
        setTimeout(() => {
            if (petal.parentNode) {
                petal.parentNode.removeChild(petal);
                this.petals = this.petals.filter(p => p !== petal);
            }
        }, (duration + delay + 2) * 1000);
    }

    startWindEffect() {
        this.windInterval = setInterval(() => {
            this.windForce = (Math.random() - 0.5) * 2;

            if (Math.abs(this.windForce) > 0.3) {
                this.applyWindEffect();
            }
        }, 3000 + Math.random() * 4000);
    }

    applyWindEffect() {
        this.petals.forEach(petal => {
            const windSensitivity = parseFloat(petal.dataset.windSensitivity);
            const windEffect = this.windForce * windSensitivity * 15;

            const currentTransform = petal.style.transform;
            const windTransform = `translateX(${windEffect}px)`;

            petal.style.transform = currentTransform + ' ' + windTransform;

            setTimeout(() => {
                petal.style.transform = currentTransform;
            }, 2000 + Math.random() * 2000);
        });
    }

    handleResize() {
        const newMaxPetals = window.innerWidth <= 768 ? 6 : 10;
        if (newMaxPetals !== this.maxPetals) {
            this.maxPetals = newMaxPetals;

            while (this.petals.length > this.maxPetals) {
                const oldestPetal = this.petals.shift();
                if (oldestPetal && oldestPetal.parentNode) {
                    oldestPetal.parentNode.removeChild(oldestPetal);
                }
            }
        }
    }
}

// 전역 애니메이션 매니저 인스턴스
let weddingAnimationManager;

// 애니메이션 초기화 함수
function initializeWeddingAnimations() {
    console.log('=== 애니메이션 매니저 초기화 시작 ===');
    weddingAnimationManager = new WeddingAnimationManager();
}

// 기존 시스템과 통합
if (typeof window !== 'undefined') {
    // 기존 initializePage가 있다면 확장
    if (typeof initializePage === 'function') {
        const originalInitializePage = initializePage;
        window.initializePage = function() {
            originalInitializePage();
            initializeWeddingAnimations();
        };
    } else {
        // 없다면 새로 생성
        window.initializePage = function() {
            initializeWeddingAnimations();
        };
    }

    // DOM 로드 완료 시 실행
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM 로드 완료');
            if (!weddingAnimationManager) {
                initializeWeddingAnimations();
            }
        });
    } else {
        console.log('DOM 이미 로드됨');
        if (!weddingAnimationManager) {
            initializeWeddingAnimations();
        }
    }

    // 페이지 언로드 시 정리
    window.addEventListener('beforeunload', function() {
        if (weddingAnimationManager && weddingAnimationManager.petalRain) {
            weddingAnimationManager.petalRain.stop();
        }
    });

    // 리사이즈 처리 - debounce 적용
    let resizeTimeout;
    window.addEventListener('resize', function() {
        if (resizeTimeout) clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (weddingAnimationManager && weddingAnimationManager.petalRain) {
                weddingAnimationManager.petalRain.handleResize();
            }
        }, 200);
    }, { passive: true });

    // 페이지 가시성 변화 처리
    document.addEventListener('visibilitychange', function() {
        if (weddingAnimationManager && weddingAnimationManager.petalRain) {
            if (document.hidden) {
                weddingAnimationManager.petalRain.stop();
            } else {
                setTimeout(() => {
                    weddingAnimationManager.petalRain.start();
                }, 1000);
            }
        }
    });

    console.log('애니메이션 이벤트 리스너 등록 완료');
}
