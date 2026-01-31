/**
 * 관리자 페이지 JavaScript
 * Author: Soohwan Kim (2025.10)
 */

// 전역 변수
let allRSVPData = [];
let allGuestbookData = [];
let allPhotosData = [];
let currentTab = 'rsvp';
let deleteTarget = null;

// 페이지 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('관리자 페이지 초기화');
    loadDashboard();

    // Lucide 아이콘 초기화
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

// 대시보드 데이터 로드
async function loadDashboard() {
    await Promise.all([
        loadRSVPData(),
        loadGuestbookData(),
        loadPhotosData()
    ]);

    updateStatistics();
}

// RSVP 데이터 로드
async function loadRSVPData() {
    try {
        const response = await fetch('/admin/api/rsvp');
        if (response.ok) {
            const data = await response.json();
            allRSVPData = data.entries || [];
            renderRSVPTable();
            document.getElementById('tab-rsvp-count').textContent = allRSVPData.length;
        } else if (response.status === 401) {
            window.location.href = '/admin/login';
        } else {
            showToast('RSVP 데이터 로드 실패');
        }
    } catch (error) {
        console.error('RSVP 데이터 로드 에러:', error);
        showToast('RSVP 데이터 로드 중 오류 발생');
    }
}

// 방명록 데이터 로드
async function loadGuestbookData() {
    try {
        const response = await fetch('/api/guestbook');
        if (response.ok) {
            const data = await response.json();
            allGuestbookData = data.entries || [];
            renderGuestbookTable();
            document.getElementById('tab-guestbook-count').textContent = allGuestbookData.length;
        } else {
            showToast('방명록 데이터 로드 실패');
        }
    } catch (error) {
        console.error('방명록 데이터 로드 에러:', error);
        showToast('방명록 데이터 로드 중 오류 발생');
    }
}

// 통계 업데이트
function updateStatistics() {
    // RSVP 통계
    const totalRSVP = allRSVPData.length;
    const attending = allRSVPData.filter(r => r.can_attend === '참석할게요').length;
    const notAttending = allRSVPData.filter(r => r.can_attend === '참석이 어려워요').length;
    const maybe = allRSVPData.filter(r => r.can_attend === '고민중이에요').length;

    document.getElementById('total-rsvp').textContent = totalRSVP;
    document.getElementById('rsvp-detail').textContent =
        `참석 ${attending} · 불참 ${notAttending} · 고민 ${maybe}`;

    // 방명록 통계
    document.getElementById('total-guestbook').textContent = allGuestbookData.length;

    // 참석 통계
    document.getElementById('attending-count').textContent = attending;
    document.getElementById('attendance-detail').textContent =
        `${attending}명 참석 / ${notAttending}명 불참`;
}

// RSVP 테이블 렌더링
function renderRSVPTable(data = allRSVPData) {
    const tbody = document.getElementById('rsvp-table-body');
    const emptyState = document.getElementById('rsvp-empty');

    if (data.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'block';
        lucide.createIcons();
        return;
    }

    emptyState.style.display = 'none';

    tbody.innerHTML = data.map((entry, index) => `
        <tr>
            <td>${data.length - index}</td>
            <td><span class="side-badge">${entry.which_side}</span></td>
            <td><span class="status-badge ${getStatusClass(entry.can_attend)}">${entry.can_attend}</span></td>
            <td><strong>${entry.guest_name}</strong></td>
            <td>${entry.companion_count || 1}명</td>
            <td>${entry.meal_attendance || '-'}</td>
            <td>${entry.phone_number || '-'}</td>
            <td>${formatDateTime(entry.timestamp)}</td>
            <td>
                <button class="btn-delete" onclick="showDeleteConfirm('rsvp', ${entry.id}, '${entry.guest_name}')">
                    <i data-lucide="trash-2"></i>
                </button>
            </td>
        </tr>
    `).join('');

    lucide.createIcons();
}

// 방명록 테이블 렌더링
function renderGuestbookTable(data = allGuestbookData) {
    const tbody = document.getElementById('guestbook-table-body');
    const emptyState = document.getElementById('guestbook-empty');

    if (data.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'block';
        lucide.createIcons();
        return;
    }

    emptyState.style.display = 'none';

    tbody.innerHTML = data.map((entry, index) => `
        <tr>
            <td>${data.length - index}</td>
            <td><strong>${entry.name}</strong></td>
            <td class="message-cell">${escapeHtml(entry.message)}</td>
            <td>${formatDateTime(entry.timestamp)}</td>
            <td>
                <button class="btn-delete" onclick="showDeleteConfirm('guestbook', ${entry.id}, '${entry.name}')">
                    <i data-lucide="trash-2"></i>
                </button>
            </td>
        </tr>
    `).join('');

    lucide.createIcons();
}

// 상태 클래스 가져오기
function getStatusClass(status) {
    switch(status) {
        case '참석할게요': return 'status-attending';
        case '참석이 어려워요': return 'status-not-attending';
        case '고민중이에요': return 'status-maybe';
        default: return '';
    }
}

// 날짜 포맷팅
function formatDateTime(timestamp) {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

// 날짜만 포맷팅
function formatDate(timestamp) {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
}

// HTML 이스케이프
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 탭 전환
function switchTab(tab) {
    currentTab = tab;

    // 탭 버튼 활성화
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.closest('.tab-btn').classList.add('active');

    // 탭 콘텐츠 표시
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tab}-tab`).classList.add('active');
}

// RSVP 필터링
function filterRSVP() {
    const statusFilter = document.getElementById('rsvp-filter').value;
    const sideFilter = document.getElementById('side-filter').value;
    const searchText = document.getElementById('rsvp-search').value.toLowerCase();

    let filtered = allRSVPData;

    // 상태 필터
    if (statusFilter !== 'all') {
        filtered = filtered.filter(entry => entry.can_attend === statusFilter);
    }

    // 측 필터
    if (sideFilter !== 'all') {
        filtered = filtered.filter(entry => entry.which_side === sideFilter);
    }

    // 검색
    if (searchText) {
        filtered = filtered.filter(entry =>
            entry.guest_name.toLowerCase().includes(searchText) ||
            (entry.phone_number && entry.phone_number.includes(searchText))
        );
    }

    renderRSVPTable(filtered);
}

// 방명록 필터링
function filterGuestbook() {
    const searchText = document.getElementById('guestbook-search').value.toLowerCase();

    if (!searchText) {
        renderGuestbookTable(allGuestbookData);
        return;
    }

    const filtered = allGuestbookData.filter(entry =>
        entry.name.toLowerCase().includes(searchText) ||
        entry.message.toLowerCase().includes(searchText)
    );

    renderGuestbookTable(filtered);
}

// 새로고침
async function refreshRSVP() {
    showToast('RSVP 데이터를 새로고침하는 중...');
    await loadRSVPData();
    updateStatistics();
    showToast('RSVP 데이터가 새로고침되었습니다.');
}

async function refreshGuestbook() {
    showToast('방명록 데이터를 새로고침하는 중...');
    await loadGuestbookData();
    updateStatistics();
    showToast('방명록 데이터가 새로고침되었습니다.');
}

// CSV 내보내기
function exportRSVP() {
    if (allRSVPData.length === 0) {
        showToast('내보낼 데이터가 없습니다.');
        return;
    }

    const csv = convertToCSV(allRSVPData, ['id', 'which_side', 'can_attend', 'guest_name', 'companion_count', 'meal_attendance', 'phone_number', 'timestamp']);
    downloadCSV(csv, 'rsvp_data.csv');
    showToast('RSVP 데이터를 다운로드했습니다.');
}

function exportGuestbook() {
    if (allGuestbookData.length === 0) {
        showToast('내보낼 데이터가 없습니다.');
        return;
    }

    const csv = convertToCSV(allGuestbookData, ['id', 'name', 'message', 'timestamp']);
    downloadCSV(csv, 'guestbook_data.csv');
    showToast('방명록 데이터를 다운로드했습니다.');
}

// CSV 변환
function convertToCSV(data, headers) {
    const headerRow = headers.join(',');
    const rows = data.map(item =>
        headers.map(header => {
            let value = item[header] || '';
            // CSV 이스케이프
            if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
                value = '"' + value.replace(/"/g, '""') + '"';
            }
            return value;
        }).join(',')
    );

    return '\uFEFF' + headerRow + '\n' + rows.join('\n'); // UTF-8 BOM 추가
}

// CSV 다운로드
function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 삭제 확인 모달
function showDeleteConfirm(type, id, name) {
    deleteTarget = { type, id, name };

    const modal = document.getElementById('delete-modal');
    const message = document.getElementById('delete-message');

    if (type === 'rsvp') {
        message.textContent = `"${name}"님의 RSVP 응답을 삭제하시겠습니까?`;
    } else {
        message.textContent = `"${name}"님의 방명록 메시지를 삭제하시겠습니까?`;
    }

    modal.style.display = 'flex';
    lucide.createIcons();
}

// 모달 닫기
function closeDeleteModal() {
    document.getElementById('delete-modal').style.display = 'none';
    deleteTarget = null;
}

// 삭제 확인
async function confirmDelete() {
    if (!deleteTarget) return;

    const { type, id, name } = deleteTarget;

    try {
        let response;
        if (type === 'rsvp') {
            response = await fetch(`/admin/api/rsvp/${id}`, {
                method: 'DELETE'
            });
        } else {
            response = await fetch(`/admin/api/guestbook/${id}`, {
                method: 'DELETE'
            });
        }

        if (response.ok) {
            showToast(`"${name}"님의 ${type === 'rsvp' ? 'RSVP 응답' : '방명록'}이 삭제되었습니다.`);
            closeDeleteModal();

            // 데이터 새로고침
            if (type === 'rsvp') {
                await loadRSVPData();
            } else {
                await loadGuestbookData();
            }
            updateStatistics();
        } else if (response.status === 401) {
            window.location.href = '/admin/login';
        } else {
            const data = await response.json();
            showToast(data.detail || '삭제에 실패했습니다.');
        }
    } catch (error) {
        console.error('삭제 에러:', error);
        showToast('삭제 중 오류가 발생했습니다.');
    }
}

// 로그아웃
async function logout() {
    try {
        const response = await fetch('/admin/logout', {
            method: 'POST'
        });

        if (response.ok) {
            window.location.href = '/admin/login';
        } else {
            showToast('로그아웃 실패');
        }
    } catch (error) {
        console.error('로그아웃 에러:', error);
        showToast('로그아웃 중 오류 발생');
    }
}

// 토스트 메시지
function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    toastMessage.textContent = message;
    toast.style.display = 'block';

    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

// 모달 외부 클릭 시 닫기
document.addEventListener('click', function(event) {
    const modal = document.getElementById('delete-modal');
    if (event.target === modal) {
        closeDeleteModal();
    }
});

// ESC 키로 모달 닫기
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeDeleteModal();
    }
});

// =============================================================================
// 사진 관리 기능
// =============================================================================

// 사진 데이터 로드
async function loadPhotosData() {
    try {
        // S3 버킷에서 직접 사진 목록 가져오기
        const response = await fetch('/photos/api/list-s3');
        if (response.ok) {
            const data = await response.json();
            allPhotosData = data.photos || [];
            renderPhotosGrid();
            document.getElementById('tab-photos-count').textContent = allPhotosData.length;

            // 통계 업데이트
            await updatePhotosStats();
        } else if (response.status === 401) {
            window.location.href = '/admin/login';
        } else {
            showToast('사진 데이터 로드 실패');
        }
    } catch (error) {
        console.error('사진 데이터 로드 에러:', error);
        showToast('사진 데이터 로드 중 오류 발생');
    }
}

// 사진 통계 업데이트
async function updatePhotosStats() {
    try {
        const response = await fetch('/photos/api/stats');
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('photos-total').textContent = stats.total_photos;
            document.getElementById('photos-size').textContent = stats.total_size_mb;
        }
    } catch (error) {
        console.error('사진 통계 로드 에러:', error);
    }
}

// 사진 그리드 렌더링
function renderPhotosGrid() {
    const grid = document.getElementById('photos-grid');
    const emptyState = document.getElementById('photos-empty');

    if (allPhotosData.length === 0) {
        grid.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';

    grid.innerHTML = allPhotosData.map(photo => `
        <div class="photo-card">
            <div class="photo-image-container">
                <img src="${photo.url}" alt="${photo.filename}" loading="lazy" onerror="this.src='/static/assets/images/image-placeholder.png'">
            </div>
            <div class="photo-info">
                <div class="photo-filename" title="${photo.filename}">${truncateFilename(photo.filename, 20)}</div>
                <div class="photo-meta">
                    <span class="photo-uploader">${photo.uploader_name || 'S3'}</span>
                    <span class="photo-size">${formatFileSize(photo.file_size)}</span>
                </div>
                <div class="photo-date">${formatDate(photo.timestamp)}</div>
            </div>
            <div class="photo-actions">
                <button onclick="downloadPhotoFromS3('${encodeURIComponent(photo.file_path)}', '${photo.filename}')" class="btn-icon" title="다운로드">
                    <i data-lucide="download"></i>
                </button>
                <button onclick="deletePhotoFromS3('${encodeURIComponent(photo.file_path)}', '${photo.filename}')" class="btn-icon btn-danger" title="삭제">
                    <i data-lucide="trash-2"></i>
                </button>
            </div>
        </div>
    `).join('');

    // Lucide 아이콘 재초기화
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// 파일명 잘라내기
function truncateFilename(filename, maxLength) {
    if (filename.length <= maxLength) return filename;
    const extension = filename.split('.').pop();
    const nameWithoutExt = filename.substring(0, filename.lastIndexOf('.'));
    const truncated = nameWithoutExt.substring(0, maxLength - extension.length - 4) + '...';
    return truncated + '.' + extension;
}

// 파일 크기 포맷
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// 사진 다운로드
function downloadPhoto(photoId, filename) {
    window.open(`/photos/api/download/${photoId}`, '_blank');
    showToast('다운로드를 시작합니다...');
}

// 사진 삭제
async function deletePhoto(photoId, filename) {
    if (!confirm(`"${filename}" 파일을 삭제하시겠습니까?\n\n⚠️ 이 작업은 되돌릴 수 없습니다.`)) {
        return;
    }

    try {
        const response = await fetch(`/photos/api/${photoId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('사진이 삭제되었습니다.');
            await loadPhotosData();
        } else {
            const error = await response.json();
            showToast(error.detail || '사진 삭제 실패');
        }
    } catch (error) {
        console.error('사진 삭제 에러:', error);
        showToast('사진 삭제 중 오류 발생');
    }
}

// S3에서 사진 다운로드
function downloadPhotoFromS3(filePath, filename) {
    const url = `/photos/api/download-s3/${encodeURIComponent(filePath)}`;
    window.open(url, '_blank');
    showToast('다운로드를 시작합니다...');
}

// S3에서 사진 삭제
async function deletePhotoFromS3(filePath, filename) {
    if (!confirm(`"${filename}" 파일을 삭제하시겠습니까?\n\n⚠️ 이 작업은 되돌릴 수 없습니다.`)) {
        return;
    }

    try {
        const response = await fetch(`/photos/api/delete-s3/${encodeURIComponent(filePath)}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('사진이 삭제되었습니다.');
            await loadPhotosData();
        } else {
            const error = await response.json();
            showToast(error.detail || '사진 삭제 실패');
        }
    } catch (error) {
        console.error('사진 삭제 에러:', error);
        showToast('사진 삭제 중 오류 발생');
    }
}

// 전체 사진 다운로드
async function downloadAllPhotos() {
    if (allPhotosData.length === 0) {
        showToast('다운로드할 사진이 없습니다.');
        return;
    }

    showToast(`${allPhotosData.length}장의 사진 다운로드를 시작합니다...`);

    // 각 사진을 순차적으로 다운로드
    for (const photo of allPhotosData) {
        setTimeout(() => {
            if (photo.id) {
                downloadPhoto(photo.id, photo.filename);
            } else {
                downloadPhotoFromS3(photo.file_path, photo.filename);
            }
        }, 500);
    }
}

// 사진 새로고침
async function refreshPhotos() {
    const grid = document.getElementById('photos-grid');
    grid.innerHTML = '<div class="loading-state"><div class="loading-spinner"></div><p>사진을 불러오는 중...</p></div>';
    await loadPhotosData();
    showToast('사진 목록이 새로고침되었습니다.');
}
