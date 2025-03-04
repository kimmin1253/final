## GPU문제로 구글 colab에서 실행함

import cv2
import os
import torch
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from ultralytics import YOLO

# ✅ YOLO & BLIP 모델 불러오기
yolo_model = YOLO("yolov8n.pt")  # YOLOv8 모델
device = "cuda" if torch.cuda.is_available() else "cpu"

# ✅ BLIP-2 모델 변경
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
blip_model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b",
    torch_dtype=torch.float16,  # 메모리 최적화
    low_cpu_mem_usage=True
).to(device)

# ✅ 폴더 설정
FRAME_DIR = "frames"
RESULTS_DIR = "detections"
CAPTION_DIR = "captions"
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(CAPTION_DIR, exist_ok=True)

def detect_objects_and_generate_caption(image_path):
    """YOLO로 객체 탐지 + BLIP-2로 설명 생성"""
    img = cv2.imread(image_path)
    
    # ✅ YOLO 탐지
    results = yolo_model(img)
    detected_objects = []
    
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            label = yolo_model.names[class_id]  # 객체 이름
            detected_objects.append(label)
    
    # ✅ BLIP-2 설명 생성
    raw_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    inputs = processor(images=raw_image, return_tensors="pt").to(device)

    with torch.no_grad():
        generated_ids = blip_model.generate(**inputs, max_length=50)
        blip_caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # ✅ 최종 설명 생성
    combined_caption = f"탐지된 객체: {', '.join(detected_objects)}. 설명: {blip_caption}"

    # ✅ 탐지 결과 시각화 및 저장
    img_with_boxes = results[0].plot()
    save_path = os.path.join(RESULTS_DIR, os.path.basename(image_path))
    cv2.imwrite(save_path, img_with_boxes)

    # ✅ 설명 저장
    caption_path = os.path.join(CAPTION_DIR, f"{os.path.basename(image_path)}.txt")
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(combined_caption)

    print(f"✅ 분석 완료: {os.path.basename(image_path)} -> {combined_caption}")

def process_all_images():
    """모든 프레임을 분석하여 객체 탐지 + 설명 생성"""
    for filename in os.listdir(FRAME_DIR):
        if filename.endswith(".jpg"):
            image_path = os.path.join(FRAME_DIR, filename)
            detect_objects_and_generate_caption(image_path)

if __name__ == "__main__":
    print("🚀 YOLO 객체 탐지 + BLIP-2 설명 생성 시작...")
    process_all_images()
    print("🎉 모든 프레임 분석 완료!")
