#!/usr/bin/env python3
"""
WebP 이미지 최적화 스크립트
- 해상도 조정: 너비 800px (비율 유지)
- 압축률 강화: Quality 80
"""

import os
import sys
from PIL import Image
from pathlib import Path


def optimize_webp(input_path, output_path, target_width=800, quality=80):
    """
    WebP 이미지 최적화

    Args:
        input_path: 입력 파일 경로
        output_path: 출력 파일 경로
        target_width: 목표 너비 (기본 800px)
        quality: WebP 품질 (기본 80)
    """
    try:
        # 이미지 열기
        img = Image.open(input_path)

        # 원본 크기
        original_width, original_height = img.size

        # 리사이징 (너비 기준, 비율 유지)
        if original_width > target_width:
            ratio = target_width / original_width
            new_height = int(original_height * ratio)
            img = img.resize((target_width, new_height), Image.LANCZOS)
            print(f"  ↳ 리사이징: {original_width}x{original_height} → {target_width}x{new_height}")
        else:
            print(f"  ↳ 리사이징 불필요 (이미 {original_width}px)")

        # WebP로 저장 (최적화 적용)
        print(f"  ↳ 저장 중: {output_path}")
        img.save(
            output_path,
            'WEBP',
            quality=quality,
            method=6,  # 최고 압축 (느리지만 용량 최소화)
            optimize=True
        )

        # 저장 확인
        if not os.path.exists(output_path):
            print(f"  ✗ 파일 저장 실패: {output_path}")
            return False

        # 파일 크기 비교
        original_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        optimized_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        reduction = ((original_size - optimized_size) / original_size) * 100

        print(f"  ↳ 용량: {original_size:.2f}MB → {optimized_size:.2f}MB (↓{reduction:.1f}%)")

        return True

    except Exception as e:
        print(f"  ✗ 오류 발생: {e}")
        return False


def process_folder(input_folder, output_folder, target_width=800, quality=80):
    """
    폴더 내 모든 WebP 파일 최적화
    """
    input_path = Path(input_folder).resolve()  # 절대 경로로 변환
    output_path = Path(output_folder).resolve()  # 절대 경로로 변환

    # 입력 폴더 확인
    if not input_path.exists():
        print(f"❌ 입력 폴더를 찾을 수 없습니다: {input_path}")
        return

    if not input_path.is_dir():
        print(f"❌ 입력 경로가 폴더가 아닙니다: {input_path}")
        return

    # 출력 폴더 생성
    try:
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 출력 폴더 생성: {output_path}")
        print(f"📁 절대 경로: {output_path.absolute()}\n")
    except Exception as e:
        print(f"❌ 출력 폴더 생성 실패: {e}")
        return

    # WebP 파일 찾기
    webp_files = list(input_path.glob("*.webp")) + list(input_path.glob("*.WEBP"))

    if not webp_files:
        print("❌ WebP 파일을 찾을 수 없습니다.")
        return

    print(f"🔍 발견된 파일: {len(webp_files)}개\n")
    print("=" * 60)

    # 통계
    success_count = 0
    fail_count = 0
    total_original = 0
    total_optimized = 0

    # 각 파일 처리
    for idx, file_path in enumerate(webp_files, 1):
        print(f"\n[{idx}/{len(webp_files)}] {file_path.name}")

        output_file = output_path / file_path.name
        print(f"  → 저장 위치: {output_file}")

        # 원본 크기 기록
        original_size = os.path.getsize(file_path) / (1024 * 1024)
        total_original += original_size

        # 최적화 실행
        if optimize_webp(file_path, output_file, target_width, quality):
            optimized_size = os.path.getsize(output_file) / (1024 * 1024)
            total_optimized += optimized_size
            success_count += 1
        else:
            fail_count += 1

    # 결과 요약
    print("\n" + "=" * 60)
    print("\n📊 최적화 완료!\n")
    print(f"✅ 성공: {success_count}개")
    if fail_count > 0:
        print(f"❌ 실패: {fail_count}개")
    print(f"\n📦 전체 용량:")
    print(f"  • 최적화 전: {total_original:.2f}MB")
    print(f"  • 최적화 후: {total_optimized:.2f}MB")

    if total_original > 0:
        total_reduction = ((total_original - total_optimized) / total_original) * 100
        print(f"  • 절감률: ↓{total_reduction:.1f}%")
        print(f"  • 절감량: {total_original - total_optimized:.2f}MB")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python optimize_webp.py <입력폴더> <출력폴더> [너비] [품질]")
        print("\n예시:")
        print("  python optimize_webp.py ./원본 ./최적화")
        print("  python optimize_webp.py ./images ./optimized 800 80")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    target_width = int(sys.argv[3]) if len(sys.argv) > 3 else 800
    quality = int(sys.argv[4]) if len(sys.argv) > 4 else 80

    print("🚀 WebP 이미지 최적화 시작\n")
    print(f"⚙️  설정:")
    print(f"  • 목표 너비: {target_width}px")
    print(f"  • 품질: {quality}")
    print(f"  • 입력: {input_folder}")
    print(f"  • 출력: {output_folder}\n")

    process_folder(input_folder, output_folder, target_width, quality)