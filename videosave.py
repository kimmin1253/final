import os
import sys
import django
import yt_dlp  # ✅ yt-dlp 라이브러리 사용

# ✅ Django 환경 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # `/fin/django`
PROJECT_DIR = os.path.dirname(BASE_DIR)  # `/fin`
BACKEND_DIR = os.path.join(BASE_DIR, "backend")  # `/fin/django/backend`

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # settings.py 경로 설정
django.setup()  # ✅ Django 환경 적용

# ✅ Django 설정 적용 후 모델 import (순서 중요!)
from ai_model.models import YouTubeVideo  

# ✅ 영상 다운로드 경로 설정
DOWNLOAD_PATH = os.path.join(BASE_DIR, "videos")  # `/fin/django/videos/`

# ✅ 폴더가 없으면 생성
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

def download_video(video_id):
    """유튜브 영상 다운로드 (yt-dlp 사용)"""
    url = f"https://www.youtube.com/watch?v={video_id}"
    file_path = os.path.join(DOWNLOAD_PATH, f"{video_id}.mp4")

    ydl_opts = {
        "format": "best",  # ✅ 비디오 + 오디오 합쳐진 단일 포맷 다운로드
        "outtmpl": file_path,  # ✅ 저장 경로 지정
        "merge_output_format": "mp4",  # ✅ 비디오 & 오디오 통합 저장
        "quiet": False,  # ✅ 다운로드 진행 상태 출력
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])  # ✅ 유튜브 영상 다운로드 실행
        print(f"✅ 다운로드 완료: {file_path}")
        return file_path
    except Exception as e:
        print(f"❌ 다운로드 실패 ({video_id}): {str(e)}")

def download_all_videos():
    """DB에서 저장된 영상 가져와서 다운로드"""
    videos = YouTubeVideo.objects.all()  # ✅ 유튜브 DB에서 영상 목록 가져오기
    for video in videos:
        file_path = os.path.join(DOWNLOAD_PATH, f"{video.video_id}.mp4")
        if not os.path.exists(file_path):  # ✅ 이미 다운로드된 영상은 건너뜀
            download_video(video.video_id)
        else:
            print(f"⏭️ 이미 다운로드됨: {file_path}")

if __name__ == "__main__":
    print("🚀 유튜브 영상 다운로드 시작...")
    download_all_videos()
    print("🎉 모든 다운로드 완료!")
