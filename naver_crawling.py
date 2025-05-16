import os
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
import requests
import base64

# === 환경 설정 ===
load_dotenv()

# === Google Sheets 인증 ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("초이스마켓_마진계산차트").worksheet("Shopee")

# === 이미 처리된 URL 불러오기 ===
processed_urls = set()
if os.path.exists("processed.txt"):
    with open("processed.txt", "r") as f:
        processed_urls = set(line.strip() for line in f.readlines())

# === 이미지 저장 폴더 준비 ===
os.makedirs("downloads", exist_ok=True)

# === Playwright 실행 ===
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        storage_state="naver_state.json",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        locale="ko-KR",
        timezone_id="Asia/Seoul",
        viewport={"width": 1280, "height": 800}
    )
    page = context.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    data = sheet.get_all_values()
    for idx, row in enumerate(data[1:], start=2):
        try:
            url = row[0]
            if not url.startswith("https://smartstore.naver.com/") or url in processed_urls:
                continue

            print(f"[INFO] 처리 중: {url}")
            page.goto(url)
            page.wait_for_selector("body", timeout=10000)
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            imgs = soup.select("div.se-main-container img")

            # 상세 설명 이미지 없을 경우 대표 이미지로 대체
            if not imgs:
                og_image = soup.select_one('meta[property="og:image"]')
                if og_image and og_image.get("content"):
                    imgs = [{"src": og_image["content"]}]
                    print(f"[INFO] 대표 이미지로 대체: {og_image['content']}")
                else:
                    print(f"[SKIP] 이미지 없음: {url}")
                    with open("failures.txt", "a") as f:
                        f.write(f"{url}\n")
                    continue

            for i, img_tag in enumerate(imgs):
                src = img_tag.get("src") if isinstance(img_tag, dict) else img_tag.get("src")
                if not src:
                    continue
                try:
                    if src.startswith("data:image"):
                        header, encoded = src.split(",", 1)
                        img_data = base64.b64decode(encoded)
                        ext = header.split(";")[0].split("/")[1]
                        filename = f"{idx}_{i}_base64.{ext}"
                    else:
                        img_data = requests.get(src).content
                        path = urlparse(src).path
                        ext = os.path.splitext(path)[1] or ".jpg"
                        filename = f"{idx}_{i}{ext}"

                    with open(os.path.join("downloads", filename), "wb") as f:
                        f.write(img_data)
                    print(f"[저장 완료] {filename}")
                except Exception as img_error:
                    print(f"[오류] 이미지 저장 실패: {src} - {img_error}")
                    continue

            sheet.update_cell(idx, 3, "TRUE")
            with open("processed.txt", "a") as f:
                f.write(f"{url}")
            processed_urls.add(url)

        except Exception as e:
            print(f"[ERROR] {url}: {e}")
            with open("failures.txt", "a") as f:
                f.write(f"{url} - {e}\n")
