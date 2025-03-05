import cv2
import os
import urllib.request
from ultralytics import YOLO

# ✅ YOLOv8 얼굴 전용 모델 다운로드 경로
MODEL_PATH = "yolov8n-face.pt"
MODEL_URL = "https://github.com/akanametov/yolo-face/releases/download/v0.0.0/yolov10l-face.pt"

# ✅ 모델이 없으면 자동 다운로드
if not os.path.exists(MODEL_PATH):
    print("🔽 YOLO 얼굴 탐지 모델 다운로드 중...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("✅ 다운로드 완료!")

# ✅ YOLO 얼굴 탐지 모델 불러오기
model = YOLO(MODEL_PATH)

# ✅ 입력 이미지 폴더 & 결과 저장 폴더
INPUT_DIR = "train_img_pam"  # 원본 이미지 폴더
OUTPUT_DIR = "cropped_faces"  # 얼굴 크롭 저장 폴더
os.makedirs(OUTPUT_DIR, exist_ok=True)

def detect_and_crop_faces(image_path):
    """YOLOv8 얼굴 탐지 후 얼굴 부분 크롭"""
    img = cv2.imread(image_path)  # 이미지 불러오기
    results = model(img)  # YOLO 모델 적용

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # 바운딩 박스 좌표 가져오기
            face = img[y1:y2, x1:x2]  # 얼굴 크롭

            if face.size > 0:  # 빈 이미지 방지
                filename = os.path.basename(image_path)
                save_path = os.path.join(OUTPUT_DIR, f"face_{filename}")
                cv2.imwrite(save_path, face)
                print(f"✅ 얼굴 저장 완료: {save_path}")

def process_all_images():
    """모든 이미지에서 얼굴 탐지 및 크롭"""
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(INPUT_DIR, filename)
            detect_and_crop_faces(image_path)

if __name__ == "__main__":
    print("🚀 YOLOv8 얼굴 탐지 + 크롭 시작...")
    process_all_images()
    print("🎉 모든 얼굴 크롭 완료!")
