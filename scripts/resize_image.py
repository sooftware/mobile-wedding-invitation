"""
모바일 환경을 고려하여 이미지 크기를 조정하고 WebP 형식으로 변환하는 스크립트
"""

import os
from PIL import Image

# 변환된 이미지 저장 폴더 생성 (재시도)
output_folder = '$OUTPUT_FOLDER$'
os.makedirs(output_folder, exist_ok=True)
file_list = os.listdir('$SOURCE_FOLDER$')

converted_files = []

MAX_SIZE = 1920  # 긴 변 크기(px) (모바일 환경 고려)
QUALITY = 100  # 화질 (0~100)

# JPG/PNG → WebP 변환 (품질 80 정도로 낮춰도 됨, 빠른 변환 위해 method=4 사용)
for file in file_list:
    file = os.path.join('$SOURCE_FOLDER$', file)
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        try:
            img = Image.open(file).convert("RGB")

            # 리사이즈 (긴 변을 MAX_SIZE 이하로 줄임)
            img.thumbnail((MAX_SIZE, MAX_SIZE))

            filename = os.path.splitext(os.path.basename(file))[0] + ".webp"
            output_path = os.path.join(output_folder, filename)
            img.save(output_path, "webp", quality=QUALITY, method=4)  # 속도 우선, 화질 유지
            converted_files.append(output_path)
        except Exception as e:
            print(f"변환 실패: {file}, 에러: {e}")

print("DONE..")
