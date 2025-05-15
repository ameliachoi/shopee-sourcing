from playwright.sync_api import sync_playwright
import pandas as pd

def crawl_shopee(keyword="korean", base_url="https://shopee.sg", max_items=20):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        search_url = f"{base_url}/search?keyword={keyword}"
        page.goto(search_url)
        page.wait_for_timeout(5000)

        items = page.locator("div.shopee-search-item-result__item")
        data = []

        for i in range(min(items.count(), max_items)):
            try:
                item = items.nth(i)
                name = item.locator("._10Wbs-._5SSWfi.UjjMrh").inner_text()
                price = item.locator("._3bRNwX").first.inner_text()
                link = item.locator("a").get_attribute("href")
                full_link = f"{base_url}{link}"
                data.append([name, price, full_link, base_url])
            except:
                continue

        browser.close()

    return pd.DataFrame(data, columns=["상품명", "가격", "링크", "국가"])
