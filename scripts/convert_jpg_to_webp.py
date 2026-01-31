#!/usr/bin/env python3
"""
JPEG to WebP 변환 스크립트
카메라 사진(10-20MB)을 모바일 최적화된 WebP로 변환
"""

import os
import sys
from pathlib import Path
from PIL import Image
import argparse


def convert_jpeg_to_webp(input_path, output_path=None, quality=85, max_dimension=2048):
    """
    JPEG 이미지를 WebP로 변환

    Args:
        input_path: 입력 이미지 경로
        output_path: 출력 이미지 경로 (None이면 같은 폴더에 저장)
        quality: WebP 품질 (0-100, 기본값 85 - 모바일에 최적)
        max_dimension: 최대 가로/세로 크기 (기본값 2048px - 모바일에 충분)
    """
    try:
        # 이미지 열기
        img = Image.open(input_path)

        # EXIF 방향 정보 처리 (카메라 회전 정보)
        try:
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # 원본 크기
        original_width, original_height = img.size

        # 리사이징 (긴 쪽이 max_dimension을 초과하면)
        if max(original_width, original_height) > max_dimension:
            if original_width > original_height:
                new_width = max_dimension
                new_height = int(original_height * (max_dimension / original_width))
            else:
                new_height = max_dimension
                new_width = int(original_width * (max_dimension / original_height))

            # 고품질 리샘플링
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"  리사이징: {original_width}x{original_height} → {new_width}x{new_height}")

        # 출력 경로 설정
        if output_path is None:
            input_file = Path(input_path)
            output_path = input_file.with_suffix('.webp')

        # WebP로 저장
        img.save(
            output_path,
            'WebP',
            quality=quality,
            method=6,  # 최고 품질 압축 방법 (느리지만 최적)
        )

        # 파일 크기 비교
        original_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        reduction = (1 - new_size / original_size) * 100

        print(f"  변환 완료: {original_size / 1024 / 1024:.2f}MB → {new_size / 1024 / 1024:.2f}MB "
              f"({reduction:.1f}% 감소)")

        return True

    except Exception as e:
        print(f"  ❌ 오류 발생: {e}")
        return False


def convert_folder(folder_path, quality=85, max_dimension=2048, recursive=False, delete_original=False):
    """
    폴더 내의 모든 JPEG 파일을 WebP로 변환

    Args:
        folder_path: 변환할 폴더 경로
        quality: WebP 품질
        max_dimension: 최대 크기
        recursive: 하위 폴더도 검색할지 여부
        delete_original: 원본 삭제 여부
    """
    folder = Path(folder_path)

    if not folder.exists():
        print(f"❌ 폴더를 찾을 수 없습니다: {folder_path}")
        return

    # JPEG 파일 찾기
    if recursive:
        jpeg_files = list(folder.rglob('*.jpg')) + list(folder.rglob('*.jpeg')) + \
                     list(folder.rglob('*.JPG')) + list(folder.rglob('*.JPEG'))
    else:
        jpeg_files = list(folder.glob('*.jpg')) + list(folder.glob('*.jpeg')) + \
                     list(folder.glob('*.JPG')) + list(folder.glob('*.JPEG'))

    if not jpeg_files:
        print("❌ 변환할 JPEG 파일이 없습니다.")
        return

    print(f"\n📁 폴더: {folder_path}")
    print(f"📊 찾은 파일: {len(jpeg_files)}개")
    print(f"⚙️  설정: 품질={quality}, 최대크기={max_dimension}px")
    print("=" * 70)

    success_count = 0
    fail_count = 0
    total_original_size = 0
    total_new_size = 0

    for i, jpeg_file in enumerate(jpeg_files, 1):
        print(f"\n[{i}/{len(jpeg_files)}] {jpeg_file.name}")

        original_size = os.path.getsize(jpeg_file)
        total_original_size += original_size

        if convert_jpeg_to_webp(jpeg_file, quality=quality, max_dimension=max_dimension):
            success_count += 1

            # 변환된 파일 크기 집계
            webp_file = jpeg_file.with_suffix('.webp')
            if webp_file.exists():
                total_new_size += os.path.getsize(webp_file)

                # 원본 삭제 옵션
                if delete_original:
                    os.remove(jpeg_file)
                    print(f"  🗑️  원본 파일 삭제됨")
        else:
            fail_count += 1

    # 결과 요약
    print("\n" + "=" * 70)
    print("📊 변환 결과:")
    print(f"  ✅ 성공: {success_count}개")
    if fail_count > 0:
        print(f"  ❌ 실패: {fail_count}개")
    print(f"  💾 총 용량: {total_original_size / 1024 / 1024:.2f}MB → "
          f"{total_new_size / 1024 / 1024:.2f}MB")
    if total_original_size > 0:
        reduction = (1 - total_new_size / total_original_size) * 100
        print(f"  📉 감소율: {reduction:.1f}%")


def main():
    parser = argparse.ArgumentParser(
        description='JPEG 이미지를 모바일 최적화된 WebP로 변환',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 기본 변환 (현재 폴더)
  python convert_images.py

  # 특정 폴더 변환
  python convert_images.py /path/to/photos

  # 하위 폴더 포함
  python convert_images.py /path/to/photos -r

  # 고품질 변환 (더 큰 파일)
  python convert_images.py -q 90 -m 3000

  # 원본 파일 삭제
  python convert_images.py --delete-original
        """
    )

    parser.add_argument(
        'folder',
        nargs='?',
        default='.',
        help='변환할 폴더 경로 (기본값: 현재 폴더)'
    )

    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        help='WebP 품질 (0-100, 기본값: 85, 모바일 최적화)'
    )

    parser.add_argument(
        '-m', '--max-dimension',
        type=int,
        default=2048,
        help='최대 가로/세로 크기 (기본값: 2048px, 모바일에 충분)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='하위 폴더도 검색'
    )

    parser.add_argument(
        '--delete-original',
        action='store_true',
        help='변환 후 원본 JPEG 파일 삭제 (주의!)'
    )

    args = parser.parse_args()

    # Pillow 라이브러리 확인
    try:
        import PIL
        print(f"✅ Pillow 버전: {PIL.__version__}")
    except ImportError:
        print("❌ Pillow 라이브러리가 설치되어 있지 않습니다.")
        print("   설치: pip install Pillow")
        sys.exit(1)

    # 원본 삭제 경고
    if args.delete_original:
        print("\n⚠️  경고: 변환 후 원본 파일이 삭제됩니다!")
        response = input("계속하시겠습니까? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("취소되었습니다.")
            sys.exit(0)

    # 변환 실행
    convert_folder(
        args.folder,
        quality=args.quality,
        max_dimension=args.max_dimension,
        recursive=args.recursive,
        delete_original=args.delete_original
    )


if __name__ == '__main__':
    main()