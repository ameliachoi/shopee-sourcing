from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://smartstore.naver.com/")
    input("👉 네이버 로그인 완료 후 엔터를 눌러주세요...")
    context.storage_state(path="naver_state.json")
