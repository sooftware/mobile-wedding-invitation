import os
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

# 경로 입력 받기
TARGET_DIR = input("HEIC 파일이 있는 폴더 경로를 입력하세요: ").strip()

if not os.path.isdir(TARGET_DIR):
    print("❌ 유효하지 않은 폴더 경로입니다.")
    exit(1)

converted = 0

for filename in os.listdir(TARGET_DIR):
    if filename.lower().endswith(".heic"):
        heic_path = os.path.join(TARGET_DIR, filename)
        jpg_name = os.path.splitext(filename)[0] + ".jpg"
        jpg_path = os.path.join(TARGET_DIR, jpg_name)

        # 이미 JPG가 있으면 스킵
        if os.path.exists(jpg_path):
            print(f"⚠️ 이미 존재: {jpg_name} (스킵)")
            continue

        img = Image.open(heic_path).convert("RGB")
        img.save(jpg_path, "JPEG", quality=95, subsampling=0)

        print(f"✅ 변환 완료: {filename} → {jpg_name}")
        converted += 1

print(f"\n🎉 변환된 파일 수: {converted}")
