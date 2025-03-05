import os
import time
import requests
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

# ✅ 크롤링할 검색어 설정
SEARCH_KEYWORD = "팜하니"
NUM_IMAGES = 400  # ✅ 가져올 이미지 개수 (기존 100 → 500개로 증가)
SAVE_DIR = "images"  # ✅ 이미지 저장 폴더

# ✅ 저장 폴더 생성
os.makedirs(SAVE_DIR, exist_ok=True)

# ✅ Chrome WebDriver 설정
options = Options()
# options.add_argument("--headless")  # 👉 주석 처리하면 브라우저 화면 확인 가능
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ✅ Bing 이미지 검색 URL 설정
search_url = f"https://www.bing.com/images/search?q={SEARCH_KEYWORD}&form=HDRSC2&first=1"
driver.get(search_url)

# ✅ 이미지 URL 수집
image_urls = set()
scroll_count = 0

while len(image_urls) < NUM_IMAGES and scroll_count < 30:  # ✅ 최대 30번 스크롤 (기존 15 → 30 증가)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(2, 4))  # 🔥 차단 방지를 위해 랜덤 딜레이 추가 (2~4초)

    # ✅ 이미지 URL 직접 추출
    image_elements = driver.find_elements(By.CSS_SELECTOR, "img.mimg")  # Bing의 `img` 태그에서 가져오기

    for img in image_elements:
        img_url = img.get_attribute("src")
        if img_url and "http" in img_url:
            image_urls.add(img_url)

    scroll_count += 1
    print(f"🔄 스크롤 {scroll_count}회 완료, 현재 {len(image_urls)}개 이미지 수집됨...")

print(f"🔍 총 {len(image_urls)}개의 이미지 URL을 찾았습니다!")

# ✅ 이미지 다운로드
for i, img_url in enumerate(tqdm(list(image_urls)[:NUM_IMAGES], desc="📥 이미지 다운로드 진행 중")):
    try:
        response = requests.get(img_url, stream=True, timeout=10)
        if response.status_code == 200:
            img_path = os.path.join(SAVE_DIR, f"image_{i+1}.jpg")
            with open(img_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

    except Exception as e:
        print(f"❌ 다운로드 실패: {img_url} -> {str(e)}")

print(f"✅ Bing 이미지 크롤링 완료! 총 {len(image_urls)}개 저장됨")

# ✅ 완료
driver.quit()
