import os
import sys
import django
import requests
import json
from datetime import datetime
from django.utils.timezone import make_aware
from googleapiclient.discovery import build

# ✅ Django 환경 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # `/fin/django`
PROJECT_DIR = os.path.dirname(BASE_DIR)  # `/fin`
BACKEND_DIR = os.path.join(BASE_DIR, "backend")  # `/fin/django/backend`

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

# ✅ Django 모델 import (Django 환경이 로드된 후에 해야 함)
from ai_model.models import YouTubeVideo

# ✅ API 키 설정 (config.json에서 로드)
with open("config.json", "r") as config_file:
    config = json.load(config_file)
    YOUTUBE_API_KEY = config["YOUTUBE_API_KEY"]

def search_youtube_videos(query, max_results=30):
    """YouTube API를 사용하여 검색어(query)와 관련된 영상을 가져옴"""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    response = request.execute()

    video_list = []
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        channel_name = item["snippet"]["channelTitle"]
        published_at = item["snippet"]["publishedAt"]
        description = item["snippet"].get("description", "")
        thumbnail_url = item["snippet"]["thumbnails"]["high"]["url"]

        # 날짜 변환 (ISO 8601 -> Django DateTimeField 형식)
        published_at_dt = make_aware(datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ"))

        video_list.append({
            "video_id": video_id,
            "title": title,
            "channel_name": channel_name,
            "published_at": published_at_dt,
            "description": description,
            "thumbnail_url": thumbnail_url
        })

    return video_list

def save_videos_to_db(video_list):
    """검색된 영상 정보를 데이터베이스에 저장"""
    for video in video_list:
        YouTubeVideo.objects.update_or_create(
            video_id=video["video_id"],
            defaults={
                "title": video["title"],
                "channel_name": video["channel_name"],
                "published_at": video["published_at"],
                "description": video["description"],
                "thumbnail_url": video["thumbnail_url"],
            }
        )
    print(f"✅ {len(video_list)}개의 영상이 데이터베이스에 저장되었습니다!")

def get_videos_data(video_ids):
    """YouTube API를 이용해 여러 영상의 조회수, 좋아요, 댓글 수 가져옴"""
    ids_string = ",".join(video_ids)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={ids_string}&key={YOUTUBE_API_KEY}"

    print(f"🔍 YouTube API 요청 URL: {url}")  # ✅ 요청 URL 출력
    response = requests.get(url)
    
    if response.status_code == 200:
        print("✅ YouTube API 응답 성공!")
        return response.json()
    
    print(f"❌ API 요청 실패! 상태 코드: {response.status_code}, 응답: {response.text}")
    return None  # API 응답 실패 시 None 반환

def update_videos_metadata():
    """DB에 저장된 모든 영상의 조회수, 좋아요, 댓글 수 업데이트"""
    print("🔍 DB에서 기존 영상 조회 중...")
    videos = YouTubeVideo.objects.all()
    video_ids = [video.video_id for video in videos]

    print(f"📌 DB에 저장된 영상 개수: {len(video_ids)}")

    if not video_ids:
        print("⚠️ DB에 저장된 영상이 없습니다. 먼저 영상을 추가합니다...")
        video_list = search_youtube_videos("팜하니")  # ✅ "팜하니" 영상 검색
        save_videos_to_db(video_list)  # ✅ 검색한 영상 저장
        video_ids = [video["video_id"] for video in video_list]  # 새롭게 저장된 영상 ID 리스트 업데이트

    for i in range(0, len(video_ids), 50):  # YouTube API는 50개씩 요청 가능
        batch_ids = video_ids[i:i+50]
        print(f"🔹 {len(batch_ids)}개의 영상 데이터 요청 중...")
        data = get_videos_data(batch_ids)

        if data and "items" in data:
            for item in data["items"]:
                video_id = item["id"]
                statistics = item.get("statistics", {})
                
                views = int(statistics.get("viewCount", 0))
                likes = int(statistics.get("likeCount", 0))
                comments = int(statistics.get("commentCount", 0))

                # ✅ DB 업데이트 (조회수, 좋아요, 댓글 포함)
                YouTubeVideo.objects.filter(video_id=video_id).update(
                    views=views,
                    likes=likes,
                    comments=comments
                )
                print(f"✅ {video_id} 업데이트 완료 (조회수: {views}, 좋아요: {likes}, 댓글: {comments})")

if __name__ == "__main__":
    print("🚀 YouTube 데이터 업데이트 시작...")
    update_videos_metadata()
    print("🎉 YouTube 데이터 업데이트 완료!")
