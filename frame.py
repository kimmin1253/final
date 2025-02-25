import cv2
import os

# ✅ 영상이 저장된 폴더
VIDEO_DIR = "videos"
FRAME_DIR = "frames"

# ✅ 프레임 저장 폴더 생성
os.makedirs(FRAME_DIR, exist_ok=True)

def extract_frames(video_path, video_id):
    """동영상에서 프레임을 1초당 1개만 추출하여 저장"""
    cap = cv2.VideoCapture(video_path)  # 영상 열기
    fps = cap.get(cv2.CAP_PROP_FPS)  # ✅ FPS 가져오기
    frame_interval = int(fps)  # ✅ 1초에 1개씩 저장하도록 설정

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # 더 이상 프레임이 없으면 종료

        if frame_count % frame_interval == 0:  # ✅ 1초당 1개씩 저장
            frame_filename = os.path.join(FRAME_DIR, f"{video_id}_frame_{frame_count:04d}.jpg")
            cv2.imwrite(frame_filename, frame)

        frame_count += 1

    cap.release()  # 리소스 해제
    print(f"✅ {video_id} - {frame_count // frame_interval}개의 프레임 저장 완료!")

def process_all_videos():
    """videos 폴더 내 모든 동영상 파일을 프레임 단위로 변환"""
    for filename in os.listdir(VIDEO_DIR):
        if filename.endswith(".mp4"):
            video_path = os.path.join(VIDEO_DIR, filename)
            video_id = filename.split(".mp4")[0]  # 파일명에서 video_id 추출
            extract_frames(video_path, video_id)

if __name__ == "__main__":
    print("🚀 프레임 추출 시작...")
    process_all_videos()
    print("🎉 모든 프레임 저장 완료!")
