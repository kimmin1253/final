from django.db import models

class YouTubeVideo(models.Model):
    video_id = models.CharField(max_length=50, unique=True)  # 유튜브 영상 ID
    title = models.CharField(max_length=255)  # 영상 제목
    channel_name = models.CharField(max_length=255)  # 채널 이름
    published_at = models.DateTimeField()  # 영상 업로드 날짜
    description = models.TextField(null=True, blank=True)  # 영상 설명 (nullable)
    views = models.BigIntegerField(default=0)  # 조회수
    likes = models.BigIntegerField(default=0)  # 좋아요 수
    comments = models.BigIntegerField(default=0)  # 댓글 수
    thumbnail_url = models.URLField(max_length=500, null=True, blank=True)  # 썸네일 이미지 URL

    class Meta:
        db_table = "youtube_video" #테이블명 변경

    def __str__(self):
        return f"{self.title} - {self.channel_name}"
