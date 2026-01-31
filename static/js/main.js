// 전역 변수들
let photos = [];
let currentLightboxIndex = 0;
let guestbookEntries = [];
let currentMessagePage = 1;
const messagesPerPage = 10; // 10개씩 로딩
let totalGuestbookPages = 1;
let isLoadingGuestbook = false;
let audio = null;
let isPlaying = false;
let isMuted = false;
let volume = 0.3;
let config = null;
let autoplayPromptShown = false;

// 성능 최적화: Intersection Observer로 이미지 지연 로딩
let imageObserver = null;

// 설정 로드
function loadConfig() {
    const configElement = document.getElementById('config-data');
    if (configElement) {
        config = JSON.parse(configElement.textContent);
    } else {
        console.error('Config data not found');
    }
}

// ==================== 동행인 수 컨트롤 ====================
function increaseCompanionCount() {
    const input = document.getElementById('rsvp-companion-extra');
    if (!input) return;
    const currentValue = parseInt(input.value) || 0;
    if (currentValue < 9) {
        input.value = currentValue + 1;
    }
    setTimeout(reinitializeLucideIcons, 50);
}

function decreaseCompanionCount() {
    const input = document.getElementById('rsvp-companion-extra');
    if (!input) return;
    const currentValue = parseInt(input.value) || 0;
    if (currentValue > 0) {
        input.value = currentValue - 1;
    }
    setTimeout(reinitializeLucideIcons, 50);
}

// 페이지 초기화 - 성능 최적화
function initializePage() {
    loadConfig();
    
    // 오프닝 애니메이션 중인지 확인하고 초기 로딩 클래스 관리
    const introOverlay = document.getElementById('intro-animation-overlay');
    if (introOverlay) {
        document.body.classList.add('intro-active');
        // 오프닝이 있으면 배경음악 초기화는 나중으로 미룸 (리소스 집중)
        setTimeout(initializeBackgroundMusic, 2000);
    } else {
        // 오프닝이 없으면 즉시 초기화
        initializeBackgroundMusic();
    }
    
    document.body.classList.add('loaded');

    // 즉시 필요한 것만 초기화
    calculateDDay();
    initializeQnA();

    // Intersection Observer 설정
    setupIntersectionObserver();

    // 지연 로딩할 항목들 (오프닝 애니메이션에 집중하기 위해 우선순위 낮춤)
    requestIdleCallback(() => {
        initializeGallery();
        initializeGuestbook();
        loadVisitorStats();
        // Kakao SDK는 defer로 로드
        initializeKakaoSDK();
    });

    // 1초마다 D-day 업데이트 (실시간 카운트다운)
    setInterval(calculateDDay, 1000);

    document.addEventListener('keydown', handleKeydown);
    initializeModalForms();

    const openGuestbookBtn = document.getElementById('open-guestbook-btn');
    if (openGuestbookBtn) {
        openGuestbookBtn.addEventListener('click', function() {
            console.log('✅ 방명록 버튼 클릭됨!');
            openGuestbookModal();
        });
        console.log('✅ 방명록 버튼 이벤트 리스너 등록 완료');
    } else {
        console.error('❌ 방명록 버튼을 찾을 수 없습니다!');
    }

    ensureLucideIcons();
}

// Intersection Observer 설정 - 이미지 지연 로딩
function setupIntersectionObserver() {
    if ('IntersectionObserver' in window) {
        imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px' // 50px 전에 미리 로드
        });
    }
}

// requestIdleCallback 폴리필
window.requestIdleCallback = window.requestIdleCallback || function(cb) {
    const start = Date.now();
    return setTimeout(() => {
        cb({
            didTimeout: false,
            timeRemaining: () => Math.max(0, 50 - (Date.now() - start))
        });
    }, 1);
};

// Lucide 아이콘 재초기화 함수 - 성능 개선 (debounce 적용)
let lucideInitTimeout = null;
let lucideInitialized = false;

function reinitializeLucideIcons() {
    if (lucideInitTimeout) {
        clearTimeout(lucideInitTimeout);
    }

    // debounce: 100ms 내 연속 호출 시 마지막 것만 실행
    lucideInitTimeout = setTimeout(() => {
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            try {
                lucide.createIcons();
            } catch (error) {
                console.error('❌ Lucide 아이콘 초기화 실패:', error);
            }
        }
    }, 50);
}

// 페이지 로드 후 아이콘 초기화 - 한 번만 실행
function ensureLucideIcons() {
    if (lucideInitialized) return;

    // requestIdleCallback으로 우선순위 낮춤
    const initIcons = () => {
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            lucide.createIcons();
            lucideInitialized = true;
        }
    };

    if ('requestIdleCallback' in window) {
        requestIdleCallback(initIcons, { timeout: 500 });
    } else {
        setTimeout(initIcons, 100);
    }
}

// 모달 폼 초기화
function initializeModalForms() {
    const rsvpForm = document.getElementById('rsvp-modal-form');
    if (rsvpForm) {
        rsvpForm.removeEventListener('submit', submitRSVP);
        rsvpForm.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            submitRSVP(e);
            return false;
        });
    }

    const guestbookForm = document.getElementById('guestbook-modal-form');
    if (guestbookForm) {
        guestbookForm.removeEventListener('submit', submitGuestbook);
        guestbookForm.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            submitGuestbook(e);
            return false;
        });

        const textarea = document.getElementById('guestbook-modal-message');
        if (textarea) {
            textarea.addEventListener('input', updateGuestbookCharCounter);
        }
    }
}

// RSVP 라디오 버튼 이벤트 초기화
function initializeRSVPRadioButtons() {
    console.log('🔧 RSVP 버튼 이벤트 초기화 시작');

    // 참석 여부 및 신랑/신부측 라디오 버튼
    const rsvpOptionBtns = document.querySelectorAll('#rsvp-modal .option-btn');
    console.log(`📍 찾은 option-btn 개수: ${rsvpOptionBtns.length}`);

    rsvpOptionBtns.forEach((btn, index) => {
        // 기존 이벤트 제거를 위해 clone
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);

        newBtn.addEventListener('click', function(e) {
            console.log(`🖱️ 버튼 클릭됨 (${index})`);
            e.preventDefault();
            e.stopPropagation();

            const radio = this.querySelector('input[type="radio"]');
            if (!radio) {
                console.error('❌ 라디오 버튼을 찾을 수 없습니다');
                return;
            }

            const groupName = radio.name;

            // 같은 그룹의 모든 버튼 선택 해제
            document.querySelectorAll(`#rsvp-modal input[name="${groupName}"]`).forEach(r => {
                const parentBtn = r.closest('.option-btn');
                if (parentBtn) {
                    parentBtn.classList.remove('selected');
                }
            });

            // 현재 버튼 선택
            this.classList.add('selected');
            radio.checked = true;

            console.log(`✅ 선택됨: ${groupName} = ${radio.value}`);
        });
    });

    // 식사여부 체크 옵션 이벤트
    const mealCheckOptions = document.querySelectorAll('#rsvp-modal .meal-check-option');
    console.log(`📍 찾은 meal-check-option 개수: ${mealCheckOptions.length}`);

    mealCheckOptions.forEach((option, index) => {
        const newOption = option.cloneNode(true);
        option.parentNode.replaceChild(newOption, option);

        newOption.addEventListener('click', function(e) {
            console.log(`🖱️ 식사 옵션 클릭됨 (${index})`);
            e.preventDefault();
            e.stopPropagation();

            const radio = this.querySelector('input[type="radio"]');
            if (!radio) {
                console.error('❌ 식사 라디오 버튼을 찾을 수 없습니다');
                return;
            }

            // 모든 식사 옵션 선택 해제
            document.querySelectorAll('#rsvp-modal .meal-check-option').forEach(opt => {
                opt.classList.remove('selected');
            });

            // 현재 옵션 선택
            this.classList.add('selected');
            radio.checked = true;

            setTimeout(() => reinitializeLucideIcons(), 50);
            console.log(`✅ 식사여부 선택됨: ${radio.value}`);
        });
    });

    // 개인정보 동의 체크박스 이벤트
    const privacyCheckOption = document.querySelector('#rsvp-modal .privacy-check-option');
    if (privacyCheckOption) {
        console.log('📍 개인정보 동의 체크박스 찾음');
        const newPrivacy = privacyCheckOption.cloneNode(true);
        privacyCheckOption.parentNode.replaceChild(newPrivacy, privacyCheckOption);

        newPrivacy.addEventListener('click', function(e) {
            console.log('🖱️ 개인정보 동의 클릭됨');
            e.preventDefault();
            e.stopPropagation();

            const checkbox = this.querySelector('input[type="checkbox"]');
            if (!checkbox) {
                console.error('❌ 체크박스를 찾을 수 없습니다');
                return;
            }

            checkbox.checked = !checkbox.checked;

            if (checkbox.checked) {
                this.classList.add('checked');
            } else {
                this.classList.remove('checked');
            }

            setTimeout(() => reinitializeLucideIcons(), 50);
            console.log(`✅ 개인정보 동의: ${checkbox.checked}`);
        });
    } else {
        console.error('❌ 개인정보 동의 체크박스를 찾을 수 없습니다');
    }

    setTimeout(() => reinitializeLucideIcons(), 100);
    console.log('✅ RSVP 버튼 이벤트 초기화 완료');
}

// RSVP 모달 열기
function openRSVPModal() {
    const modal = document.getElementById('rsvp-modal');
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    const form = document.getElementById('rsvp-modal-form');
    if (form) {
        form.reset();
        const extraInput = document.getElementById('rsvp-companion-extra');
        if (extraInput) {
            extraInput.value = 0; // 추가인원은 기본 0
        }
        document.querySelectorAll('#rsvp-modal .option-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        document.querySelectorAll('#rsvp-modal .meal-check-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        const privacyCheck = document.querySelector('#rsvp-modal .privacy-check-option');
        if (privacyCheck) {
            privacyCheck.classList.remove('checked');
        }
    }

    initializeRSVPRadioButtons();

    setTimeout(reinitializeLucideIcons, 50);
    setTimeout(reinitializeLucideIcons, 200);
}

// RSVP 모달 닫기
function closeRSVPModal() {
    const modal = document.getElementById('rsvp-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';

    // 모달 닫을 때 BGM 자동 재생
    if (!isPlaying && audio && audio.readyState >= 2) {
        tryAutoplay();
    }
}

async function submitRSVP(event) {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    const submitBtn = document.getElementById('rsvp-submit-btn');
    const submitText = document.getElementById('rsvp-submit-text');

    if (submitBtn.disabled) return;

    const formData = new FormData(event.target);
    const extraCount = parseInt(formData.get('companion-extra')) || 0;
    const data = {
        which_side: formData.get('which-side'),
        can_attend: formData.get('can-attend'),
        guest_name: formData.get('guest-name'),
        phone_number: formData.get('phone-number') || '',
        companion_count: extraCount + 1, // 본인 + 추가인원
        meal_attendance: formData.get('meal-attendance') || ''
    };

    console.log('📤 RSVP 제출 데이터:', data);

    if (!data.which_side) {
        alert('어느 분의 하객인지 선택해주세요.');
        return;
    }
    if (!data.can_attend) {
        alert('참석 여부를 선택해주세요.');
        return;
    }
    if (!data.guest_name.trim()) {
        alert('성함을 입력해주세요.');
        return;
    }
    if (!data.meal_attendance) {
        alert('식사 여부를 선택해주세요.');
        return;
    }

    submitBtn.disabled = true;
    submitText.innerHTML = '<span class="loading-spinner"></span>전송 중...';

    try {
        const response = await fetch('/api/rsvp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        console.log('📥 서버 응답:', result);

        if (response.ok) {
            console.log('✅ RSVP 제출 성공!');
            closeRSVPModal();
            showToast('참석 여부가 성공적으로 전달되었습니다! 💕');

            // RSVP 제출 성공 시 BGM 자동 재생
            if (!isPlaying && audio && audio.readyState >= 2) {
                setTimeout(() => {
                    tryAutoplay();
                }, 500);
            }
        } else {
            throw new Error(result.detail || '제출 실패');
        }
    } catch (error) {
        console.error('❌ RSVP 제출 실패:', error);
        alert('제출 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
        submitBtn.disabled = false;
        submitText.textContent = '제출하기';
    }
}

// ==================== 방문자 통계 ====================
async function loadVisitorStats() {
    try {
        const response = await fetch('/api/visitor-stats');
        if (response.ok) {
            const data = await response.json();
            document.getElementById('today-count').textContent = data.today;
            document.getElementById('total-count').textContent = data.total;
        }
    } catch (error) {
        console.error('방문자 통계 로드 실패:', error);
        document.getElementById('today-count').textContent = '-';
        document.getElementById('total-count').textContent = '-';
    }
}

function openGuestbookModal() {
    const modal = document.getElementById('guestbook-modal');
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    const form = document.getElementById('guestbook-modal-form');
    if (form) {
        form.reset();
        updateGuestbookCharCounter();
    }
}

function closeGuestbookModal() {
    const modal = document.getElementById('guestbook-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
}

function updateGuestbookCharCounter() {
    const textarea = document.getElementById('guestbook-modal-message');
    const counter = document.getElementById('guestbook-char-counter');

    if (!textarea || !counter) return;

    const currentLength = textarea.value.length;
    const maxLength = 500;
    counter.textContent = `${currentLength} / ${maxLength}`;

    if (currentLength > maxLength * 0.9) {
        counter.className = 'char-counter error';
    } else if (currentLength > maxLength * 0.8) {
        counter.className = 'char-counter warning';
    } else {
        counter.className = 'char-counter';
    }
}

async function submitGuestbook(event) {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    const submitBtn = document.getElementById('guestbook-submit-btn');
    const submitText = document.getElementById('guestbook-submit-text');

    if (submitBtn.disabled) return;

    const formData = new FormData(event.target);
    const data = {
        name: formData.get('name').trim(),
        message: formData.get('message').trim(),
        password: formData.get('password').trim()
    };

    console.log('📤 방명록 제출 데이터:', { name: data.name, message: data.message.substring(0, 50) + '...' });

    if (!data.name) {
        alert('성함을 입력해주세요.');
        return;
    }
    if (data.name.length > 20) {
        alert('성함은 20자 이내로 입력해주세요.');
        return;
    }
    if (!data.message) {
        alert('축하 메시지를 입력해주세요.');
        return;
    }
    if (data.message.length > 500) {
        alert('메시지는 500자 이내로 입력해주세요.');
        return;
    }
    if (!data.password) {
        alert('비밀번호를 입력해주세요.');
        return;
    }
    if (data.password.length < 4) {
        alert('비밀번호는 4자리 이상 입력해주세요.');
        return;
    }

    submitBtn.disabled = true;
    submitText.innerHTML = '<span class="loading-spinner"></span>전송 중...';

    try {
        const response = await fetch('/api/guestbook', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        console.log('📥 서버 응답:', result);

        if (response.ok) {
            console.log('✅ 방명록 제출 성공!');
            closeGuestbookModal();
            showToast('축하 메시지가 전달되었습니다! 💝');
            await initializeGuestbook();
        } else {
            throw new Error(result.detail || '제출 실패');
        }
    } catch (error) {
        console.error('❌ 방명록 제출 실패:', error);
        alert('제출 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
        submitBtn.disabled = false;
        submitText.textContent = '작성 완료';
    }
}

// D-day 계산 - 성능 최적화 (DOM 캐싱 및 변경 시에만 업데이트)
let dDayCache = { days: null, hours: null, minutes: null, seconds: null };
let dDayElements = null;

function calculateDDay() {
    if (!config) return;

    // DOM 요소 캐싱 (첫 호출 시에만)
    if (!dDayElements) {
        dDayElements = {
            dDay: document.getElementById('d-day-text'),
            days: document.getElementById('countdown-days'),
            hours: document.getElementById('countdown-hours'),
            minutes: document.getElementById('countdown-minutes'),
            seconds: document.getElementById('countdown-seconds')
        };
    }

    const targetDate = new Date(config.wedding.date.iso_format);
    const now = new Date();
    const diff = targetDate.getTime() - now.getTime();

    let days, hours, minutes, seconds;

    if (diff <= 0) {
        days = hours = minutes = seconds = 0;
    } else {
        days = Math.floor(diff / (1000 * 60 * 60 * 24));
        hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        seconds = Math.floor((diff % (1000 * 60)) / 1000);
    }

    // 값이 변경된 경우에만 DOM 업데이트 (리플로우 최소화)
    if (dDayCache.days !== days) {
        dDayCache.days = days;
        if (dDayElements.dDay) dDayElements.dDay.textContent = days + '일';
        if (dDayElements.days) dDayElements.days.textContent = days;
    }
    if (dDayCache.hours !== hours) {
        dDayCache.hours = hours;
        if (dDayElements.hours) dDayElements.hours.textContent = hours;
    }
    if (dDayCache.minutes !== minutes) {
        dDayCache.minutes = minutes;
        if (dDayElements.minutes) dDayElements.minutes.textContent = minutes;
    }
    if (dDayCache.seconds !== seconds) {
        dDayCache.seconds = seconds;
        if (dDayElements.seconds) dDayElements.seconds.textContent = seconds;
    }
}

// Google Calendar 추가
function addToGoogleCalendar() {
    if (!config) return;

    const weddingDate = config.wedding.date;
    const venue = config.wedding.venue;
    const groom = config.wedding.groom.name_kr;
    const bride = config.wedding.bride.name_kr;

    const startDate = new Date(weddingDate.iso_format).toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    const endDate = new Date(new Date(weddingDate.iso_format).getTime() + 2 * 60 * 60 * 1000).toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';

    const title = encodeURIComponent(`${groom} ♥ ${bride} 결혼식`);
    const details = encodeURIComponent(
        `${groom}과 ${bride}의 결혼식에 초대합니다!\n\n📍 장소: ${venue.name}\n📍 주소: ${venue.address}\n⏰ 시간: ${weddingDate.display_time}\n\n따뜻한 축복과 응원 부탁드립니다.`
    );
    const location = encodeURIComponent(`${venue.name}, ${venue.address}`);
    const dates = `${startDate}/${endDate}`;

    const googleCalendarUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${dates}&details=${details}&location=${location}&sf=true&output=xml`;
    window.open(googleCalendarUrl, '_blank');
}

// 갤러리 초기화 - 3열 그리드
function initializeGallery() {
    if (!config) return;

    const totalPhotos = config.content.gallery.total_photos;
    const imageNumbers = Array.from({length: totalPhotos}, (_, i) => i + 1);

    photos = imageNumbers.map(num => ({
        src: `${config.assets.gallery_path}${num}.webp`,
        key: num
    }));

    // 모든 사진을 그리드로 렌더링
    renderPhotoGrid();

    // 라이트박스 스와이프 제스처 초기화
    initializeLightboxSwipe();
}

// 사진 그리드 렌더링 - 모든 사진을 3열 그리드로 표시
function renderPhotoGrid() {
    const photoGrid = document.getElementById('photo-grid');

    photoGrid.innerHTML = photos.map((photo, index) => {
        return `
            <div class="photo-item" data-index="${index}" onclick="openGalleryLightbox(${index})">
                <img data-src="${photo.src}" alt="Gallery photo ${index + 1}" loading="lazy" decoding="async" style="background: #f5f5f5;" />
            </div>
        `;
    }).join('');

    // Intersection Observer로 이미지 지연 로딩
    if (imageObserver) {
        photoGrid.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // 폴백: data-src를 src로 즉시 변환
        photoGrid.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

// 갤러리 라이트박스 열기
function openGalleryLightbox(index) {
    currentLightboxIndex = index;
    const lightbox = document.getElementById('gallery-lightbox');
    const lightboxImage = document.getElementById('lightbox-image');

    if (lightbox && lightboxImage && photos[index]) {
        lightboxImage.src = photos[index].src;
        lightbox.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        // Lucide 아이콘 다시 초기화
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

// 갤러리 라이트박스 닫기
function closeGalleryLightbox() {
    const lightbox = document.getElementById('gallery-lightbox');
    if (lightbox) {
        lightbox.style.display = 'none';
        document.body.style.overflow = '';
    }
}

// 라이트박스 네비게이션
function navigateLightbox(direction) {
    const newIndex = currentLightboxIndex + direction;

    // 순환 네비게이션
    if (newIndex < 0) {
        currentLightboxIndex = photos.length - 1;
    } else if (newIndex >= photos.length) {
        currentLightboxIndex = 0;
    } else {
        currentLightboxIndex = newIndex;
    }

    const lightboxImage = document.getElementById('lightbox-image');
    if (lightboxImage && photos[currentLightboxIndex]) {
        lightboxImage.src = photos[currentLightboxIndex].src;
    }
}

// 라이트박스 스와이프 제스처
let lightboxTouchStartX = 0;
let lightboxTouchEndX = 0;

function initializeLightboxSwipe() {
    const lightbox = document.getElementById('gallery-lightbox');
    if (!lightbox) return;

    lightbox.addEventListener('touchstart', (e) => {
        lightboxTouchStartX = e.touches[0].clientX;
    }, { passive: true });

    lightbox.addEventListener('touchmove', (e) => {
        lightboxTouchEndX = e.touches[0].clientX;
    }, { passive: true });

    lightbox.addEventListener('touchend', () => {
        const swipeThreshold = 50;
        const swipeDistance = lightboxTouchEndX - lightboxTouchStartX;

        if (Math.abs(swipeDistance) > swipeThreshold) {
            if (swipeDistance > 0) {
                navigateLightbox(-1); // 이전
            } else {
                navigateLightbox(1); // 다음
            }
        }

        lightboxTouchStartX = 0;
        lightboxTouchEndX = 0;
    }, { passive: true });

    // 배경 클릭시 닫기
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox || e.target.classList.contains('gallery-lightbox-container')) {
            closeGalleryLightbox();
        }
    });

    // ESC 키로 닫기
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && lightbox.style.display === 'flex') {
            closeGalleryLightbox();
        }
        if (e.key === 'ArrowLeft' && lightbox.style.display === 'flex') {
            navigateLightbox(-1);
        }
        if (e.key === 'ArrowRight' && lightbox.style.display === 'flex') {
            navigateLightbox(1);
        }
    });
}

// Q&A 아코디언 초기화
function initializeQnA() {
    if (!config) return;

    const accordion = document.getElementById('qna-accordion');
    const qnaData = config.qna;

    accordion.innerHTML = qnaData.map(item => `
        <div class="accordion-item" data-id="${item.id}">
            <button class="accordion-header" onclick="toggleQnAItem(${item.id})">
                <span class="question">${item.question}</span>
                <span class="chevron">
                    <i data-lucide="chevron-down"></i>
                </span>
            </button>
            <div class="accordion-content collapsed">
                <div class="answer">${item.answer}</div>
            </div>
        </div>
    `).join('');

    reinitializeLucideIcons();
}

function toggleQnAItem(id) {
    const item = document.querySelector(`[data-id="${id}"]`);
    const content = item.querySelector('.accordion-content');
    const chevron = item.querySelector('.chevron');

    if (content.classList.contains('collapsed')) {
        content.classList.remove('collapsed');
        content.classList.add('expanded');
        chevron.classList.add('rotated');
        item.classList.add('open');
    } else {
        content.classList.remove('expanded');
        content.classList.add('collapsed');
        chevron.classList.remove('rotated');
        item.classList.remove('open');
    }
}

// 방명록 초기화
async function initializeGuestbook(page = 1) {
    const loadingElement = document.getElementById('loading-messages');
    const messageCountElement = document.getElementById('message-count');

    if (!loadingElement || !messageCountElement) {
        console.log('방명록 요소들을 찾을 수 없습니다. 메인 페이지가 아닐 수 있습니다.');
        return;
    }

    if (isLoadingGuestbook) {
        console.log('이미 방명록을 로딩 중입니다.');
        return;
    }

    isLoadingGuestbook = true;

    try {
        const response = await fetch(`/api/guestbook?page=${page}&limit=${messagesPerPage}`);
        if (response.ok) {
            const data = await response.json();

            if (page === 1) {
                guestbookEntries = data.entries || [];
            } else {
                guestbookEntries = [...guestbookEntries, ...(data.entries || [])];
            }

            totalGuestbookPages = data.total_pages || 1;
            currentMessagePage = data.page || 1;

            messageCountElement.textContent = data.total || 0;
            renderGuestbookMessages();
        } else {
            showEmptyGuestbook();
        }
    } catch (error) {
        console.error('방명록 로딩 실패:', error);
        showEmptyGuestbook();
    } finally {
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        isLoadingGuestbook = false;
    }
}

function showEmptyGuestbook() {
    if (!config) return;

    const container = document.getElementById('messages-container');
    if (!container) return;

    container.innerHTML = `
        <div class="empty-state">
            <i data-lucide="message-circle"></i>
            <p>${config.content.guestbook.empty_message}</p>
            <span>${config.content.guestbook.empty_subtitle}</span>
        </div>
    `;
    reinitializeLucideIcons();
}

function renderGuestbookMessages() {
    const container = document.getElementById('messages-container');
    if (!container) return;

    if (guestbookEntries.length === 0) {
        showEmptyGuestbook();
        return;
    }

    const MAX_LENGTH = 100; // 최대 글자 수

    const messagesList = container.querySelector('.messages-list') || document.createElement('div');
    if (!messagesList.parentElement) {
        messagesList.className = 'messages-list';
        container.innerHTML = '';
        container.appendChild(messagesList);
    }

    messagesList.innerHTML = guestbookEntries.map(entry => {
        const isLong = entry.message.length > MAX_LENGTH;
        const truncatedMessage = isLong ? entry.message.substring(0, MAX_LENGTH) + '...' : entry.message;

        return `
        <div class="message-card" data-id="${entry.id}">
            <div class="message-header">
                <div class="message-actions">
                    <button class="edit-button" onclick="showEditModal(${entry.id})" title="메시지 수정">
                        ✏️
                    </button>
                    <button class="delete-button" onclick="showDeleteModal(${entry.id})" title="메시지 삭제">
                        ×
                    </button>
                </div>
            </div>
            <div class="message-content">
                <p class="message-text" data-full="${isLong ? 'false' : 'true'}">${truncatedMessage}</p>
                ${isLong ? `
                    <button class="read-more-btn" onclick="toggleMessageExpand(${entry.id})" data-expanded="false">
                        더보기
                    </button>
                ` : ''}
            </div>
            <div class="author-display">- ${entry.name} -</div>
            <div class="timestamp">${formatTimestamp(entry.timestamp)}</div>
        </div>
        `;
    }).join('');

    // 스크롤 이벤트 리스너 추가
    setupScrollListener(messagesList);
}

// 슬라이드 스크롤 이벤트 리스너 설정 - 성능 최적화
let scrollHandlerRef = null;

function setupScrollListener(messagesList) {
    // 기존 리스너 제거
    if (scrollHandlerRef) {
        messagesList.removeEventListener('scroll', scrollHandlerRef);
    }

    // debounce된 핸들러 생성
    scrollHandlerRef = debounce(handleGuestbookScroll, 100);

    // passive: true로 스크롤 성능 최적화
    messagesList.addEventListener('scroll', scrollHandlerRef, { passive: true });
}

// 슬라이드 스크롤 핸들러
function handleGuestbookScroll(event) {
    const messagesList = event.target;
    const scrollLeft = messagesList.scrollLeft;
    const scrollWidth = messagesList.scrollWidth;
    const clientWidth = messagesList.clientWidth;

    // 스크롤이 끝에서 100px 이내로 근접하면 다음 페이지 로드
    if (scrollLeft + clientWidth >= scrollWidth - 100) {
        if (currentMessagePage < totalGuestbookPages && !isLoadingGuestbook) {
            initializeGuestbook(currentMessagePage + 1);
        }
    }
}

// 범용 debounce 함수
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function toggleMessageExpand(messageId) {
    const card = document.querySelector(`.message-card[data-id="${messageId}"]`);
    if (!card) return;

    const messageText = card.querySelector('.message-text');
    const button = card.querySelector('.read-more-btn');
    const entry = guestbookEntries.find(e => e.id === messageId);

    if (!entry || !messageText || !button) return;

    const isExpanded = button.getAttribute('data-expanded') === 'true';
    const MAX_LENGTH = 60;

    if (isExpanded) {
        // 접기
        messageText.textContent = entry.message.substring(0, MAX_LENGTH) + '...';
        button.textContent = '더보기';
        button.setAttribute('data-expanded', 'false');
    } else {
        // 펼치기
        messageText.textContent = entry.message;
        button.textContent = '접기';
        button.setAttribute('data-expanded', 'true');
    }
}


function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffTime / (1000 * 60));

    if (diffDays > 0) {
        return `${diffDays}일 전`;
    } else if (diffHours > 0) {
        return `${diffHours}시간 전`;
    } else if (diffMinutes > 0) {
        return `${diffMinutes}분 전`;
    } else {
        return '방금 전';
    }
}

// 수정 모달 표시
function showEditModal(messageId) {
    const modal = document.getElementById('edit-modal');
    const passwordInput = document.getElementById('edit-password-input');

    modal.style.display = 'flex';
    passwordInput.value = '';
    passwordInput.focus();

    const confirmBtn = document.getElementById('confirm-edit');
    confirmBtn.onclick = () => verifyPasswordForEdit(messageId);
}

async function verifyPasswordForEdit(messageId) {
    const password = document.getElementById('edit-password-input').value;

    if (!password) {
        alert('비밀번호를 입력해주세요.');
        return;
    }

    try {
        const response = await fetch(`/api/guestbook/${messageId}/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: messageId,
                password: password
            })
        });

        const result = await response.json();

        if (response.ok) {
            closeEditModal();
            showEditForm(messageId, result.data, password);
        } else {
            alert(result.detail || '비밀번호가 일치하지 않습니다.');
        }
    } catch (error) {
        console.error('비밀번호 확인 실패:', error);
        alert('비밀번호 확인 중 오류가 발생했습니다.');
    }
}

function showEditForm(messageId, data, password) {
    const modal = document.getElementById('edit-form-modal');
    const nameInput = document.getElementById('edit-name-input');
    const messageInput = document.getElementById('edit-message-input');

    nameInput.value = data.name;
    messageInput.value = data.message;
    modal.style.display = 'flex';
    nameInput.focus();

    const saveBtn = document.getElementById('save-edit');
    saveBtn.onclick = () => saveEditedMessage(messageId, password);
}

async function saveEditedMessage(messageId, password) {
    const name = document.getElementById('edit-name-input').value.trim();
    const message = document.getElementById('edit-message-input').value.trim();

    if (!name || !message) {
        alert('이름과 메시지를 모두 입력해주세요.');
        return;
    }

    try {
        const response = await fetch(`/api/guestbook/${messageId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: messageId,
                name: name,
                message: message,
                password: password
            })
        });

        const result = await response.json();

        if (response.ok) {
            showToast('메시지가 수정되었습니다.');
            closeEditFormModal();

            const messageCard = document.querySelector(`.message-card[data-id="${messageId}"]`);
            if (messageCard) {
                const entryIndex = guestbookEntries.findIndex(entry => entry.id === messageId);
                if (entryIndex !== -1) {
                    guestbookEntries[entryIndex].name = name;
                    guestbookEntries[entryIndex].message = message;
                }

                const authorName = messageCard.querySelector('.author-name');
                const messageContent = messageCard.querySelector('.message-content p');

                if (authorName) authorName.textContent = name;
                if (messageContent) messageContent.textContent = message;

                messageCard.style.animation = 'pulse 0.5s ease-out';
                setTimeout(() => {
                    messageCard.style.animation = '';
                }, 500);
            } else {
                await initializeGuestbook();
            }
        } else {
            alert(result.detail || '수정에 실패했습니다.');
        }
    } catch (error) {
        console.error('수정 실패:', error);
        alert('수정 중 오류가 발생했습니다.');
    }
}

function closeEditModal() {
    document.getElementById('edit-modal').style.display = 'none';
}

function closeEditFormModal() {
    document.getElementById('edit-form-modal').style.display = 'none';
}

function showDeleteModal(messageId) {
    const modal = document.getElementById('password-modal');
    const passwordInput = document.getElementById('password-input');

    modal.style.display = 'flex';
    passwordInput.value = '';
    passwordInput.focus();

    const confirmBtn = document.getElementById('confirm-delete');
    confirmBtn.onclick = () => deleteMessage(messageId);
}

function closeDeleteModal() {
    document.getElementById('password-modal').style.display = 'none';
}

async function deleteMessage(messageId) {
    const password = document.getElementById('password-input').value;

    if (!password) {
        alert('비밀번호를 입력해주세요.');
        return;
    }

    try {
        const response = await fetch(`/api/guestbook/${messageId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: messageId,
                password: password
            })
        });

        const result = await response.json();

        if (response.ok) {
            showToast('메시지가 삭제되었습니다.');
            closeDeleteModal();

            const messageCard = document.querySelector(`.message-card[data-id="${messageId}"]`);
            if (messageCard) {
                messageCard.style.animation = 'fadeOut 0.3s ease-out';
                setTimeout(() => {
                    guestbookEntries = guestbookEntries.filter(entry => entry.id !== messageId);

                    const messageCountElement = document.getElementById('message-count');
                    if (messageCountElement) {
                        messageCountElement.textContent = guestbookEntries.length;
                    }

                    const startIndex = (currentMessagePage - 1) * messagesPerPage;
                    const endIndex = startIndex + messagesPerPage;
                    const currentMessages = guestbookEntries.slice(startIndex, endIndex);

                    if (currentMessages.length === 0 && currentMessagePage > 1) {
                        currentMessagePage--;
                    }

                    renderGuestbookMessages();
                }, 300);
            } else {
                await initializeGuestbook();
            }
        } else {
            alert(result.detail || '삭제에 실패했습니다.');
        }
    } catch (error) {
        console.error('삭제 실패:', error);
        alert('삭제 중 오류가 발생했습니다.');
    }
}

// 배경음악 초기화 - 성능 최적화 (메타데이터만 먼저 로드)
function initializeBackgroundMusic() {
    if (!config) return;

    audio = new Audio(config.assets.background_music);
    audio.loop = true;
    audio.volume = 0.3;
    audio.muted = isMuted;
    audio.preload = 'metadata'; // 메타데이터만 먼저 로드하여 초기 로딩 속도 개선

    audio.addEventListener('play', () => {
        isPlaying = true;
        updatePlayButton();
        saveUserMusicPreferences(); // 재생 상태 저장
        console.log('✅ 배경음악 재생 중');
    });

    audio.addEventListener('pause', () => {
        isPlaying = false;
        updatePlayButton();
        saveUserMusicPreferences(); // 일시정지 상태 저장
        console.log('⏸️ 배경음악 일시정지');
    });

    audio.addEventListener('error', (e) => {
        console.error('❌ 배경음악 로딩 실패:', e);
    });

    loadUserMusicPreferences();

    // 즉시 로딩 시작 (재생은 하지 않음)
    audio.load();
    console.log('🎵 배경음악 로드 명령 실행 (자동 재생 비활성화 - 모달 닫을 때만 재생)');

    // Fallback 3: 페이지 가시성 변경 시 자동 재생 (탭 전환, 페이지 재진입 등)
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && audio && audio.readyState >= 2) {
            // 페이지가 다시 보이고, 음악이 재생 중이 아니며, 이전에 재생했었다면
            const savedPlaying = localStorage.getItem('wedding-music-playing');
            if (!isPlaying && savedPlaying === 'true') {
                console.log('👁️ 페이지 다시 보임 - 음악 자동 재생 시도');
                tryAutoplay();
            }
        }
    });

    // Fallback 4: 페이지 포커스 시 자동 재생
    window.addEventListener('focus', () => {
        if (audio && audio.readyState >= 2 && !isPlaying) {
            const savedPlaying = localStorage.getItem('wedding-music-playing');
            if (savedPlaying === 'true') {
                console.log('🔍 페이지 포커스 - 음악 자동 재생 시도');
                tryAutoplay();
            }
        }
    });
}

function tryAutoplay() {
    if (!audio || isPlaying) return Promise.resolve(true);

    console.log('🎵 자동재생 시도...');
    return audio.play()
        .then(() => {
            console.log('✅ BGM 자동재생 성공!');
            isPlaying = true;
            updatePlayButton();
            showBGMNotification(); // 배너 표시
            return true;
        })
        .catch(error => {
            console.log('⚠️ 자동재생 실패 (브라우저 정책):', error.message);
            isPlaying = false;
            updatePlayButton();
            return false;
        });
}

// BGM 알림 배너 표시 함수
function showBGMNotification() {
    const banner = document.getElementById('bgm-notification-banner');
    const speakerControl = document.getElementById('bgm-speaker-control');

    if (!banner || !speakerControl) return;

    // 배너 표시 (스피커는 배너 안에 포함되어 함께 내려옴)
    banner.classList.add('show');
    console.log('🎵 BGM 알림 배너 및 스피커 아이콘 표시');

    // Lucide 아이콘 재초기화
    setTimeout(() => reinitializeLucideIcons(), 100);

    // 3초 후 스피커를 배너에서 분리하고 배너를 숨김
    setTimeout(() => {
        // 1. 스피커의 현재 위치 계산
        const rect = speakerControl.getBoundingClientRect();

        // 2. 스피커를 정확한 위치에 fixed로 고정
        speakerControl.style.position = 'fixed';
        speakerControl.style.top = rect.top + 'px';
        speakerControl.style.right = (window.innerWidth - rect.right) + 'px';
        speakerControl.style.left = 'auto';
        speakerControl.classList.add('detached');

        // 3. 스피커를 배너에서 분리해서 body의 직접 자식으로 옮김
        document.body.appendChild(speakerControl);

        // 4. 배너를 숨김 (스피커는 이미 DOM에서 분리되어 영향받지 않음)
        banner.classList.remove('show');
        console.log('🎵 BGM 알림 배너 숨김, 스피커는 body로 이동하여 우측 상단에 고정');
    }, 3000);
}

function toggleMusic() {
    if (!audio) return;

    if (isPlaying) {
        audio.pause();
    } else {
        audio.play().then(() => {
            console.log('✅ 사용자가 음악 재생');
            // 사용자가 직접 재생한 경우에도 배너/아이콘 표시
            const speakerControl = document.getElementById('bgm-speaker-control');
            if (speakerControl && !speakerControl.classList.contains('detached')) {
                showBGMNotification();
            }
        }).catch(error => {
            console.log('❌ 재생 실패:', error);
            alert('음악 재생에 실패했습니다. 다시 시도해주세요.');
        });
    }
}

function updatePlayButton() {
    // 기존 play-icon 업데이트 (하위 호환성)
    const playIcon = document.getElementById('play-icon');
    if (playIcon) {
        if (isPlaying) {
            playIcon.setAttribute('data-lucide', 'pause');
        } else {
            playIcon.setAttribute('data-lucide', 'play');
        }
    }

    // 스피커 아이콘 업데이트
    const speakerIcon = document.getElementById('bgm-speaker-icon');
    if (speakerIcon) {
        if (isPlaying) {
            speakerIcon.setAttribute('data-lucide', 'volume-2');
        } else {
            speakerIcon.setAttribute('data-lucide', 'volume-x');
        }
    }

    reinitializeLucideIcons();
}

function loadUserMusicPreferences() {
    try {
        const savedMuted = localStorage.getItem('wedding-music-muted');
        const savedPlaying = localStorage.getItem('wedding-music-playing');

        if (savedMuted) {
            isMuted = savedMuted === 'true';
            if (audio) audio.muted = isMuted;
        }

        // 이전에 음악을 재생했었다면 자동재생을 더 적극적으로 시도
        if (savedPlaying === 'true') {
            console.log('🎵 이전 세션에서 음악 재생 이력 있음 - 자동재생 시도');
            autoplayPromptShown = true; // 사용자가 이미 음악을 들었음을 표시
        }
    } catch (error) {
        console.log('localStorage 접근 실패:', error);
    }
}

function saveUserMusicPreferences() {
    try {
        localStorage.setItem('wedding-music-muted', isMuted.toString());
        localStorage.setItem('wedding-music-playing', isPlaying.toString());
    } catch (error) {
        console.log('localStorage 저장 실패:', error);
    }
}

// 지도 라이트박스
function openMapLightbox() {
    const lightbox = document.getElementById('map-lightbox');
    lightbox.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeMapLightbox() {
    const lightbox = document.getElementById('map-lightbox');
    lightbox.style.display = 'none';
    document.body.style.overflow = '';
}

// 주소 복사
function copyAddress() {
    if (!config) return;

    const address = config.wedding.venue.full_address;
    navigator.clipboard.writeText(address)
        .then(() => showToast('주소가 복사되었습니다!'))
        .catch(err => console.error('주소 복사 실패:', err));
}

// 카카오 SDK 초기화 - defer 로딩
function initializeKakaoSDK() {
    const script = document.createElement('script');
    script.src = 'https://t1.kakaocdn.net/kakao_js_sdk/2.7.2/kakao.min.js';
    script.integrity = 'sha384-TiCUE00h649CAMonG018J2ujOgDKW/kVWlChEuu4jK2vxfAAD0eZxzCKakxg55G4';
    script.crossOrigin = 'anonymous';
    script.defer = true;

    script.onload = () => {
        if (window.Kakao && !window.Kakao.isInitialized()) {
            const kakaoAppKey = window.KAKAO_APP_KEY;
            if (kakaoAppKey && kakaoAppKey !== '') {
                window.Kakao.init(kakaoAppKey);
                console.log('카카오 SDK 초기화 완료');
            } else {
                console.warn('카카오 앱 키가 설정되지 않았습니다.');
            }
        }
    };

    script.onerror = () => {
        console.error('카카오 SDK 로드 실패');
    };

    document.head.appendChild(script);
}

// 공유 기능들
function shareToKakao() {
    if (!config) return;

    if (typeof window.Kakao === 'undefined') {
        showToast('카카오톡 공유 기능을 불러오는 중입니다. 잠시 후 다시 시도해주세요.');
        return;
    }

    const shareConfig = config.content.share.kakao_share;

    try {
        window.Kakao.Share.sendDefault({
            objectType: 'feed',
            content: {
                title: shareConfig.title,
                description: shareConfig.description,
                imageUrl: config.content.meta.image,
                link: {
                    mobileWebUrl: window.location.href,
                    webUrl: window.location.href
                }
            },
            buttons: [
                {
                    title: shareConfig.button_title,
                    link: {
                        mobileWebUrl: window.location.href,
                        webUrl: window.location.href
                    }
                }
            ],
            installTalk: true
        });
    } catch (error) {
        console.error('카카오톡 공유 실패:', error);
        showToast('카카오톡 공유에 실패했습니다. 다시 시도해주세요.');
    }
}

async function copyLink() {
    try {
        const currentUrl = window.location.href;

        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(currentUrl);
            showToast('링크가 복사되었습니다! 💕');
        } else {
            const textArea = document.createElement('textarea');
            textArea.value = currentUrl;
            textArea.style.position = 'fixed';
            textArea.style.opacity = '0';
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showToast('링크가 복사되었습니다! 💕');
        }
    } catch (error) {
        console.error('링크 복사 실패:', error);
        showToast('링크 복사에 실패했습니다.');
    }
}

async function shareNative() {
    if (!config) return;

    const shareConfig = config.content.share.kakao_share;

    if (navigator.share) {
        try {
            await navigator.share({
                title: shareConfig.title,
                text: shareConfig.description.replace(/\\n/g, '\n'),
                url: window.location.href
            });
        } catch (error) {
            if (error.name !== 'AbortError') {
                copyLink();
            }
        }
    } else {
        copyLink();
    }
}

// 토스트 메시지
function showToast(message) {
    const toast = document.getElementById('share-toast');
    const toastMessage = document.getElementById('toast-message');

    toastMessage.textContent = message;
    toast.style.display = 'block';

    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

// 키보드 이벤트 핸들러
function handleKeydown(event) {
    const mapLightbox = document.getElementById('map-lightbox');
    const passwordModal = document.getElementById('password-modal');
    const editModal = document.getElementById('edit-modal');
    const editFormModal = document.getElementById('edit-form-modal');
    const rsvpModal = document.getElementById('rsvp-modal');
    const guestbookModal = document.getElementById('guestbook-modal');

    const activeElement = document.activeElement;
    const isInputFocused = activeElement && (
        activeElement.tagName === 'INPUT' ||
        activeElement.tagName === 'TEXTAREA' ||
        activeElement.contentEditable === 'true'
    );

    if (event.key === 'Escape') {
        if (mapLightbox.style.display === 'flex') {
            closeMapLightbox();
        } else if (guestbookModal.style.display === 'flex') {
            closeGuestbookModal();
        } else if (rsvpModal.style.display === 'flex') {
            closeRSVPModal();
        } else if (editFormModal.style.display === 'flex') {
            closeEditFormModal();
        } else if (editModal.style.display === 'flex') {
            closeEditModal();
        } else if (passwordModal.style.display === 'flex') {
            closeDeleteModal();
        }
    } else if (event.key === ' ' && !isInputFocused) {
        event.preventDefault();
        toggleMusic();
    }
}

// 모달 오버레이 클릭 시 닫기
document.addEventListener('click', function(event) {
    const passwordModal = document.getElementById('password-modal');
    const editModal = document.getElementById('edit-modal');
    const editFormModal = document.getElementById('edit-form-modal');
    const mapLightbox = document.getElementById('map-lightbox');
    const rsvpModal = document.getElementById('rsvp-modal');
    const guestbookModal = document.getElementById('guestbook-modal');

    if (event.target === passwordModal) {
        closeDeleteModal();
    } else if (event.target === editModal) {
        closeEditModal();
    } else if (event.target === editFormModal) {
        closeEditFormModal();
    } else if (event.target === mapLightbox) {
        closeMapLightbox();
    } else if (event.target === rsvpModal) {
        closeRSVPModal();
    } else if (event.target === guestbookModal) {
        closeGuestbookModal();
    }
});

// 연락처 아코디언 토글 함수
function toggleParentsAccordion() {
    const content = document.getElementById('parents-content');
    const icon = document.getElementById('parents-accordion-icon');

    if (content.classList.contains('expanded')) {
        content.classList.remove('expanded');
        icon.classList.remove('rotated');
    } else {
        content.classList.add('expanded');
        icon.classList.add('rotated');
    }
}

// 페이드아웃 애니메이션 CSS 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: scale(1); }
        to { opacity: 0; transform: scale(0.8); }
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); box-shadow: 0 8px 25px rgba(185, 148, 147, 0.3); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);

// ==================== 참석 의사 전달 모달 ====================

// 참석 의사 전달 모달 표시
function showAttendanceNoticeModal() {
    // "오늘 하루 보지 않기" 확인
    const hideUntil = localStorage.getItem('attendance-notice-hide-until');
    if (hideUntil) {
        const hideDate = new Date(hideUntil);
        const now = new Date();
        if (now < hideDate) {
            console.log('✅ 오늘 하루 보지 않기 설정됨 - 모달 표시 안 함');
            return;
        }
    }

    const modal = document.getElementById('attendance-notice-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        console.log('✅ 참석 의사 전달 모달 표시');

        // Lucide 아이콘 초기화
        setTimeout(reinitializeLucideIcons, 50);
    }
}

// 참석 의사 전달 모달 닫기
function closeAttendanceNoticeModal(skipBGM = false) {
    const modal = document.getElementById('attendance-notice-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        console.log('✅ 참석 의사 전달 모달 닫기');

        // RSVP 모달로 전환하는 경우가 아닐 때만 BGM 재생
        if (!skipBGM && !isPlaying && audio && audio.readyState >= 2) {
            setTimeout(() => {
                tryAutoplay();
            }, 300);
        }
    }
}

// 참석 의사 전달 모달에서 RSVP 모달 열기
function openRSVPFromNotice() {
    closeAttendanceNoticeModal(true); // BGM 재생 건너뛰기
    setTimeout(() => {
        openRSVPModal();
    }, 300); // 부드러운 전환을 위한 딜레이
}

// 오늘 하루 보지 않기
function hideAttendanceNoticeForToday() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0); // 다음날 자정

    localStorage.setItem('attendance-notice-hide-until', tomorrow.toISOString());
    console.log('✅ 오늘 하루 보지 않기 설정:', tomorrow);

    closeAttendanceNoticeModal();
    showToast('내일부터 다시 표시됩니다');
}

// 오프닝 애니메이션 완료 후 모달 표시 (이벤트 리스너)
// 주석 처리: animations.js의 WeddingAnimationManager에서 이미 처리하고 있음
// document.addEventListener('DOMContentLoaded', function() {
//     // 오프닝 애니메이션이 완료되는 시점에 모달 표시
//     // animations.js의 타이밍과 일치시키기 위해 여유를 두고 설정
//     const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

//     // 새로운 오프닝 애니메이션 타이밍:
//     // - 일반 모드: 완료 시간 10.2초 → 모달 표시 11초
//     // - 저전력 모드: 완료 시간 6.3초 → 모달 표시 7초
//     const showModalDelay = prefersReducedMotion ? 7000 : 11000;

//     console.log(`참석 의사 전달 모달 타이밍: ${showModalDelay}ms`);

//     setTimeout(() => {
//         showAttendanceNoticeModal();
//     }, showModalDelay);
// });

// =============================================================================
// 전역 함수 노출
// =============================================================================

window.openGuestbookModal = openGuestbookModal;
window.closeGuestbookModal = closeGuestbookModal;
window.openRSVPModal = openRSVPModal;
window.closeRSVPModal = closeRSVPModal;
window.showEditModal = showEditModal;
window.closeEditModal = closeEditModal;
window.closeEditFormModal = closeEditFormModal;
window.showDeleteModal = showDeleteModal;
window.closeDeleteModal = closeDeleteModal;
window.openGalleryLightbox = openGalleryLightbox;
window.closeGalleryLightbox = closeGalleryLightbox;
window.navigateLightbox = navigateLightbox;
window.openMapLightbox = openMapLightbox;
window.closeMapLightbox = closeMapLightbox;
window.toggleQnAItem = toggleQnAItem;
window.toggleMusic = toggleMusic;
window.copyAddress = copyAddress;
window.shareToKakao = shareToKakao;
window.copyLink = copyLink;
window.shareNative = shareNative;
window.addToGoogleCalendar = addToGoogleCalendar;
window.toggleParentsAccordion = toggleParentsAccordion;
window.increaseCompanionCount = increaseCompanionCount;
window.decreaseCompanionCount = decreaseCompanionCount;
window.toggleMessageExpand = toggleMessageExpand;
window.showAttendanceNoticeModal = showAttendanceNoticeModal;
window.closeAttendanceNoticeModal = closeAttendanceNoticeModal;
window.openRSVPFromNotice = openRSVPFromNotice;
window.hideAttendanceNoticeForToday = hideAttendanceNoticeForToday;

// ==================== 사진 업로드 ====================

let selectedFiles = [];

// 파일 선택 핸들러
function handleFileSelect(event) {
    const files = Array.from(event.target.files);

    if (files.length > 50) {
        showToast('한 번에 최대 50장까지 업로드할 수 있습니다.');
        event.target.value = '';
        return;
    }

    selectedFiles = files;
    displayFilePreview(files);
}

// 파일 미리보기 표시
function displayFilePreview(files) {
    const previewContainer = document.getElementById('file-preview');
    previewContainer.innerHTML = '';

    if (files.length === 0) {
        return;
    }

    const fileCount = document.createElement('div');
    fileCount.className = 'file-count';
    fileCount.textContent = `선택된 파일: ${files.length}개`;
    previewContainer.appendChild(fileCount);

    const previewGrid = document.createElement('div');
    previewGrid.className = 'preview-grid';

    files.forEach((file, index) => {
        const previewItem = document.createElement('div');
        previewItem.className = 'preview-item';

        const reader = new FileReader();
        reader.onload = (e) => {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'preview-image';
            previewItem.appendChild(img);

            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-preview-btn';
            removeBtn.innerHTML = '×';
            removeBtn.onclick = (event) => {
                event.preventDefault();
                removeFile(index);
            };
            previewItem.appendChild(removeBtn);
        };
        reader.readAsDataURL(file);

        previewGrid.appendChild(previewItem);
    });

    previewContainer.appendChild(previewGrid);
}

// 파일 제거
function removeFile(index) {
    selectedFiles.splice(index, 1);
    displayFilePreview(selectedFiles);

    // 파일 input 업데이트
    const fileInput = document.getElementById('photo-files');
    const dataTransfer = new DataTransfer();
    selectedFiles.forEach(file => dataTransfer.items.add(file));
    fileInput.files = dataTransfer.files;

    if (selectedFiles.length === 0) {
        fileInput.value = '';
    }
}

// 드래그 앤 드롭 처리
const fileUploadArea = document.getElementById('file-upload-area');

if (fileUploadArea) {
    fileUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUploadArea.classList.add('dragover');
    });

    fileUploadArea.addEventListener('dragleave', () => {
        fileUploadArea.classList.remove('dragover');
    });

    fileUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        fileUploadArea.classList.remove('dragover');

        const files = Array.from(e.dataTransfer.files).filter(file =>
            file.type.startsWith('image/')
        );

        if (files.length > 50) {
            showToast('한 번에 최대 50장까지 업로드할 수 있습니다.');
            return;
        }

        const fileInput = document.getElementById('photo-files');
        const dataTransfer = new DataTransfer();
        files.forEach(file => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;

        selectedFiles = files;
        displayFilePreview(files);
    });
}

// 사진 업로드 폼 제출
const photoUploadForm = document.getElementById('photo-upload-form');

if (photoUploadForm) {
    photoUploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (selectedFiles.length === 0) {
            showToast('사진을 선택해주세요.');
            return;
        }

        const uploaderName = document.getElementById('uploader-name').value || '';
        const uploadButton = document.getElementById('photo-upload-button');
        const uploadProgress = document.getElementById('upload-progress');
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');

        // 버튼 비활성화 및 진행 상태 표시
        uploadButton.disabled = true;
        uploadButton.querySelector('#upload-button-text').textContent = '업로드 중...';
        uploadProgress.style.display = 'block';

        try {
            const formData = new FormData();
            selectedFiles.forEach(file => {
                formData.append('files', file);
            });
            formData.append('uploader_name', uploaderName);

            const response = await fetch('/photos/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                progressFill.style.width = '100%';
                progressText.textContent = '업로드 완료!';

                showToast(`${result.uploaded}장의 사진이 업로드되었습니다! ✨`);

                // 폼 리셋
                setTimeout(() => {
                    photoUploadForm.reset();
                    selectedFiles = [];
                    displayFilePreview([]);
                    uploadProgress.style.display = 'none';
                    progressFill.style.width = '0%';
                }, 2000);
            } else {
                throw new Error(result.detail || '업로드에 실패했습니다.');
            }
        } catch (error) {
            console.error('업로드 실패:', error);
            showToast('업로드 중 오류가 발생했습니다. 다시 시도해주세요.');
            uploadProgress.style.display = 'none';
        } finally {
            uploadButton.disabled = false;
            uploadButton.querySelector('#upload-button-text').textContent = '업로드';
        }
    });
}

window.handleFileSelect = handleFileSelect;

// ==================== Snaps 섹션 업로드 기능 ====================

// 업로드 허용 시작 시간 (한국시간 기준: 2026-05-17 12:00:00)
const UPLOAD_START_TIME_KST = new Date('2026-05-17T12:00:00+09:00');

/**
 * 현재 한국시간이 업로드 허용 시간인지 확인
 */
function isUploadAllowed() {
    const now = new Date();
    return now >= UPLOAD_START_TIME_KST;
}

/**
 * Snaps 업로드 버튼 및 안내 문구 상태 업데이트
 */
function updateSnapUploadStatus() {
    const uploadButton = document.querySelector('.snap-upload-button');
    const uploadNotice = document.getElementById('snap-upload-notice');

    if (!uploadButton || !uploadNotice) return;

    if (isUploadAllowed()) {
        // 업로드 가능 시간
        uploadButton.disabled = false;
        uploadButton.style.opacity = '1';
        uploadButton.style.cursor = 'pointer';
        uploadNotice.style.display = 'none';
    } else {
        // 업로드 불가 시간
        uploadButton.disabled = true;
        uploadButton.style.opacity = '0.5';
        uploadButton.style.cursor = 'not-allowed';
        uploadNotice.style.display = 'block';
    }
}

/**
 * Snaps 업로드 창 열기
 */
function openSnapUpload() {
    // 한국시간 기준으로 업로드 허용 시간 체크
    if (!isUploadAllowed()) {
        showToast('2026년 5월 17일 12:00(한국시간)부터 업로드 가능합니다.');
        return;
    }

    const input = document.getElementById('snap-upload-input');
    if (input) {
        input.click();
    }
}

/**
 * Snaps 업로드 모달 닫기
 */
function closeSnapUploadModal() {
    const modal = document.getElementById('snap-upload-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Snaps 파일 선택 이벤트 핸들러 초기화
 */
function initializeSnapUpload() {
    const input = document.getElementById('snap-upload-input');
    if (!input) return;

    // 업로드 상태 초기화 (버튼 비활성화/활성화 및 안내 문구 표시)
    updateSnapUploadStatus();

    input.addEventListener('change', async function(e) {
        const files = Array.from(e.target.files);

        if (files.length === 0) return;

        // 최대 50장 제한
        if (files.length > 50) {
            showToast('한 번에 최대 50장까지만 업로드할 수 있습니다.');
            return;
        }

        // 파일 크기 검증 (10MB)
        const maxSize = 10 * 1024 * 1024; // 10MB
        const oversizedFiles = files.filter(file => file.size > maxSize);
        if (oversizedFiles.length > 0) {
            showToast(`파일 크기가 너무 큽니다. 최대 10MB까지 업로드 가능합니다.`);
            return;
        }

        // 모달 표시
        const modal = document.getElementById('snap-upload-modal');
        const progressBar = document.getElementById('snap-upload-progress');
        const statusText = document.getElementById('snap-upload-status');
        const closeBtn = document.getElementById('snap-upload-close');

        modal.style.display = 'flex';
        progressBar.style.width = '0%';
        statusText.textContent = `${files.length}장의 사진을 업로드하는 중...`;
        closeBtn.style.display = 'none';

        try {
            // FormData 생성
            const formData = new FormData();
            files.forEach(file => {
                formData.append('files', file);
            });
            formData.append('uploader_name', 'Guest'); // 익명 업로더

            // 업로드 요청
            const xhr = new XMLHttpRequest();

            // 진행률 업데이트
            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    progressBar.style.width = percentComplete + '%';
                    statusText.textContent = `업로드 중... ${Math.round(percentComplete)}%`;
                }
            });

            // 업로드 완료
            xhr.addEventListener('load', function() {
                if (xhr.status === 200) {
                    const result = JSON.parse(xhr.responseText);
                    progressBar.style.width = '100%';

                    if (result.uploaded > 0) {
                        statusText.textContent = `✅ ${result.uploaded}장의 사진이 업로드되었습니다!`;
                        if (result.failed > 0) {
                            statusText.textContent += `\n⚠️ ${result.failed}장은 업로드에 실패했습니다.`;
                        }
                    } else {
                        statusText.textContent = '❌ 업로드에 실패했습니다.';
                    }

                    closeBtn.style.display = 'block';
                    // 입력 필드 초기화
                    input.value = '';
                } else {
                    progressBar.style.width = '0%';
                    statusText.textContent = '❌ 업로드에 실패했습니다. 다시 시도해주세요.';
                    closeBtn.style.display = 'block';
                    input.value = '';
                }
            });

            // 에러 처리
            xhr.addEventListener('error', function() {
                progressBar.style.width = '0%';
                statusText.textContent = '❌ 업로드 중 오류가 발생했습니다.';
                closeBtn.style.display = 'block';
                input.value = '';
            });

            // 요청 전송
            xhr.open('POST', '/photos/upload', true);
            xhr.send(formData);

        } catch (error) {
            console.error('업로드 에러:', error);
            progressBar.style.width = '0%';
            statusText.textContent = '❌ 업로드 중 오류가 발생했습니다.';
            closeBtn.style.display = 'block';
            input.value = '';
        }
    });
}

// Snaps 업로드 초기화를 페이지 로드 시 실행
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSnapUpload);
} else {
    initializeSnapUpload();
}

// 전역 함수로 노출
window.openSnapUpload = openSnapUpload;
window.closeSnapUploadModal = closeSnapUploadModal;

console.log('✅ 모든 전역 함수 노출 완료');