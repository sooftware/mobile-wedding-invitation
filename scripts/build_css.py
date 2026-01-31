#!/usr/bin/env python3
"""
CSS Build Script
개발용 분리된 CSS 파일들을 하나의 main.css로 합치고 압축하는 스크립트
"""

import os
import re
import sys
from pathlib import Path

# 우선순위가 있는 CSS 파일들 (먼저 로드되어야 함)
PRIORITY_FILES = [
    'variables.css',  # CSS 변수들 - 가장 먼저
    'base.css',  # 기본 스타일 - 두 번째
]

# 제외할 파일들
EXCLUDE_FILES = [
    'main.css',  # 빌드 결과물
    'main.min.css',  # 빌드 결과물
]


def minify_css(css_content):
    """CSS 압축 함수"""
    # 주석 제거 (/* ... */)
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)

    # 여러 줄 공백을 한 줄로
    css_content = re.sub(r'\n\s*\n', '\n', css_content)

    # 각 줄의 앞뒤 공백 제거
    css_content = '\n'.join(line.strip() for line in css_content.split('\n'))

    # 빈 줄 제거
    css_content = '\n'.join(line for line in css_content.split('\n') if line)

    # CSS 압축: 불필요한 공백 제거
    css_content = re.sub(r'\s*{\s*', '{', css_content)
    css_content = re.sub(r'\s*}\s*', '}', css_content)
    css_content = re.sub(r'\s*;\s*', ';', css_content)
    css_content = re.sub(r'\s*:\s*', ':', css_content)
    css_content = re.sub(r'\s*,\s*', ',', css_content)

    return css_content


def get_css_files(css_dir):
    """CSS 디렉토리에서 모든 CSS 파일을 찾아서 우선순위에 따라 정렬"""
    all_files = []

    # 디렉토리의 모든 .css 파일 찾기
    for file_path in css_dir.glob('*.css'):
        filename = file_path.name

        # 제외 파일 체크
        if filename in EXCLUDE_FILES:
            continue

        all_files.append(filename)

    # 파일 정렬: 우선순위 파일 먼저, 나머지는 알파벳 순
    priority_files = [f for f in PRIORITY_FILES if f in all_files]
    other_files = sorted([f for f in all_files if f not in PRIORITY_FILES])

    final_order = priority_files + other_files

    print(f"📂 발견된 CSS 파일들 ({len(final_order)}개):")
    for i, filename in enumerate(final_order, 1):
        priority_mark = "🔥" if filename in PRIORITY_FILES else "📄"
        print(f"   {i:2d}. {priority_mark} {filename}")

    return final_order


def build_css():
    """CSS 파일들을 합쳐서 main.css 생성"""
    script_dir = Path(__file__).parent
    css_dir = script_dir / '../static' / 'css'

    if not css_dir.exists():
        print(f"❌ CSS 디렉토리를 찾을 수 없습니다: {css_dir}")
        return False

    print("🔨 CSS 빌드 시작...")

    # 동적으로 CSS 파일들 찾기
    css_files = get_css_files(css_dir)

    if not css_files:
        print("❌ 빌드할 CSS 파일이 없습니다!")
        return False

    combined_css = []
    combined_css.append("/* Generated CSS - DO NOT EDIT MANUALLY */")
    combined_css.append("/* Build script combines all CSS files into this single file */")
    combined_css.append(f"/* Generated at: {os.popen('date').read().strip()} */")
    combined_css.append(f"/* Total files combined: {len(css_files)} */")
    combined_css.append("")

    # CSS 파일들을 순서대로 합치기
    processed_files = []
    for css_file in css_files:
        css_path = css_dir / css_file

        if not css_path.exists():
            print(f"⚠️  파일을 찾을 수 없습니다: {css_file}")
            continue

        print(f"📄 추가 중: {css_file}")

        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 파일 헤더 추가
            combined_css.append(f"/* ===== {css_file} ===== */")
            combined_css.append(content)
            combined_css.append("")
            processed_files.append(css_file)

        except Exception as e:
            print(f"❌ {css_file} 읽기 실패: {e}")
            return False

    if not processed_files:
        print("❌ 처리된 CSS 파일이 없습니다!")
        return False

    # 합쳐진 CSS 내용
    final_css = '\n'.join(combined_css)

    # main.css 생성 (개발용 - 압축 안함)
    main_css_path = css_dir / 'main.css'
    try:
        with open(main_css_path, 'w', encoding='utf-8') as f:
            f.write(final_css)
        print(f"✅ 개발용 CSS 생성: {main_css_path}")
    except Exception as e:
        print(f"❌ main.css 쓰기 실패: {e}")
        return False

    # main.min.css 생성 (프로덕션용 - 압축됨)
    minified_css = minify_css(final_css)
    main_min_css_path = css_dir / 'main.min.css'
    try:
        with open(main_min_css_path, 'w', encoding='utf-8') as f:
            f.write(minified_css)
        print(f"✅ 프로덕션용 CSS 생성: {main_min_css_path}")
    except Exception as e:
        print(f"❌ main.min.css 쓰기 실패: {e}")
        return False

    # 크기 정보 출력
    original_size = sum(
        os.path.getsize(css_dir / css_file)
        for css_file in processed_files
        if (css_dir / css_file).exists()
    )
    combined_size = os.path.getsize(main_css_path)
    minified_size = os.path.getsize(main_min_css_path)

    print(f"\n📊 빌드 결과:")
    print(f"   처리된 파일: {len(processed_files)}개")
    print(f"   원본 파일들 총합: {original_size:,} bytes")
    print(f"   합쳐진 CSS: {combined_size:,} bytes")
    print(f"   압축된 CSS: {minified_size:,} bytes")
    print(f"   압축률: {((combined_size - minified_size) / combined_size * 100):.1f}%")
    print(f"   HTTP 요청 감소: {len(processed_files)}개 → 1개")

    return True


def update_html_template():
    """HTML 템플릿에서 CSS import 방식을 main.css로 변경"""
    script_dir = Path(__file__).parent
    template_path = script_dir / '../templates' / 'index.html'

    if not template_path.exists():
        print(f"⚠️  템플릿 파일을 찾을 수 없습니다: {template_path}")
        return False

    print("🔧 HTML 템플릿 업데이트 중...")

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # main.css import로 교체
        old_css_link = r'<link rel="stylesheet" href="/static/css/main\.css">'
        new_css_link = '<link rel="stylesheet" href="/static/css/main.min.css">'

        if 'main.min.css' not in content:
            content = re.sub(old_css_link, new_css_link, content)

            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ HTML 템플릿 업데이트 완료")
        else:
            print("✅ HTML 템플릿이 이미 업데이트됨")

        return True

    except Exception as e:
        print(f"❌ HTML 템플릿 업데이트 실패: {e}")
        return False


if __name__ == "__main__":
    print("🚀 CSS 빌드 프로세스 시작")

    success = build_css()

    if success:
        # HTML 템플릿도 업데이트 (선택사항)
        if len(sys.argv) > 1 and sys.argv[1] == "--update-html":
            update_html_template()

        print("🎉 CSS 빌드 완료!")
        sys.exit(0)
    else:
        print("💥 CSS 빌드 실패!")
        sys.exit(1)