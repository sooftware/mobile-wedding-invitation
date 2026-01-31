#!/usr/bin/env python3
"""
인트로 애니메이션 이미지를 모바일 최적화된 크기로 재생성
현재 1920px → 1080px로 리사이징하여 용량 절반 이상 절감
"""

import os
from PIL import Image
from pathlib import Path


def optimize_intro_image(input_path, output_path, target_width=1080, quality=85):
    """
    인트로 애니메이션 이미지 최적화

    Args:
        input_path: 입력 파일 경로
        output_path: 출력 파일 경로
        target_width: 목표 너비 (기본 1080px - 모바일 최적화)
        quality: WebP 품질 (기본 85)
    """
    try:
        # 이미지 열기
        img = Image.open(input_path)

        # EXIF 방향 정보 처리
        try:
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
        except:
            pass

        # RGB로 변환
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

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

        # WebP로 저장
        print(f"  ↳ 저장 중: {output_path}")
        img.save(
            output_path,
            'WEBP',
            quality=quality,
            method=6,
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
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    images_dir = Path("/home/user/wedding-card/static/assets/images")

    files_to_optimize = [
        "animation1.webp",
        "animation2.webp",
    ]

    print("🚀 인트로 애니메이션 이미지 최적화 시작\n")
    print(f"⚙️  설정:")
    print(f"  • 목표 너비: 1080px (모바일 최적화)")
    print(f"  • 품질: 85\n")
    print("=" * 60)

    success_count = 0
    total_original = 0
    total_optimized = 0

    for idx, filename in enumerate(files_to_optimize, 1):
        input_path = images_dir / filename
        # 백업 생성
        backup_path = images_dir / f"{filename}.backup"
        output_path = input_path

        if not input_path.exists():
            print(f"\n[{idx}/{len(files_to_optimize)}] {filename}")
            print(f"  ✗ 파일을 찾을 수 없습니다: {input_path}")
            continue

        print(f"\n[{idx}/{len(files_to_optimize)}] {filename}")

        # 백업 생성
        os.rename(input_path, backup_path)
        print(f"  ↳ 백업 생성: {backup_path.name}")

        original_size = os.path.getsize(backup_path) / (1024 * 1024)
        total_original += original_size

        if optimize_intro_image(backup_path, output_path, target_width=1080, quality=85):
            optimized_size = os.path.getsize(output_path) / (1024 * 1024)
            total_optimized += optimized_size
            success_count += 1
            # 백업 삭제
            os.remove(backup_path)
            print(f"  ✓ 백업 파일 삭제")
        else:
            # 실패 시 백업 복원
            os.rename(backup_path, output_path)
            print(f"  ✗ 최적화 실패 - 백업 복원")

    # 결과 요약
    print("\n" + "=" * 60)
    print("\n📊 최적화 완료!\n")
    print(f"✅ 성공: {success_count}개")
    print(f"\n📦 전체 용량:")
    print(f"  • 최적화 전: {total_original:.2f}MB")
    print(f"  • 최적화 후: {total_optimized:.2f}MB")

    if total_original > 0:
        total_reduction = ((total_original - total_optimized) / total_original) * 100
        print(f"  • 절감률: ↓{total_reduction:.1f}%")
        print(f"  • 절감량: {total_original - total_optimized:.2f}MB")
