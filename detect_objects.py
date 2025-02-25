import cv2
import os
from ultralytics import YOLO

# ✅ YOLO 모델 불러오기 (미리 학습된 모델 사용)
model = YOLO("yolov8n.pt")  # YOLOv8 기본 모델 (사전 학습됨)

# ✅ 프레임이 저장된 폴더
FRAME_DIR = "frames"
RESULTS_DIR = "detections"

# ✅ 결과 저장 폴더 생성
os.makedirs(RESULTS_DIR, exist_ok=True)

def detect_objects(image_path):
    """이미지에서 객체 탐지"""
    img = cv2.imread(image_path)  # 이미지 불러오기
    results = model(img)  # YOLO 모델 적용

    # ✅ 탐지 결과 시각화 및 저장
    for result in results:
        img_with_boxes = result.plot()  # 탐지된 객체를 시각적으로 표시
        filename = os.path.basename(image_path)
        save_path = os.path.join(RESULTS_DIR, filename)
        cv2.imwrite(save_path, img_with_boxes)
        print(f"✅ 객체 탐지 완료: {save_path}")

def process_all_images():
    """frames 폴더 내 모든 이미지에서 객체 탐지"""
    for filename in os.listdir(FRAME_DIR):
        if filename.endswith(".jpg"):
            image_path = os.path.join(FRAME_DIR, filename)
            detect_objects(image_path)

if __name__ == "__main__":
    print("🚀 YOLO 객체 탐지 시작...")
    process_all_images()
    print("🎉 모든 프레임에 대한 객체 탐지 완료!")
