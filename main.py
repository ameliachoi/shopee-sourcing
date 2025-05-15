from crawler import crawl_shopee
from gsheet_uploader import save_to_gsheet
import pandas as pd

if __name__ == "__main__":
    country_configs = [
        {"name": "Singapore", "url": "https://shopee.sg", "keyword": "korean skincare"},
        {"name": "Mexico", "url": "https://shopee.com.mx", "keyword": "kpop lightstick"},
        {"name": "Malaysia", "url": "https://shopee.com.my", "keyword": "korean ramen"},
        {"name": "Thailand", "url": "https://shopee.co.th", "keyword": "สกินแคร์เกาหลี"},
        {"name": "Vietnam", "url": "https://shopee.vn", "keyword": "mì hàn quốc"},
        {"name": "Philippines", "url": "https://shopee.ph", "keyword": "korean face mask"},
        {"name": "Brazil", "url": "https://shopee.com.br", "keyword": "korean beauty"}
    ]

    all_data = pd.DataFrame()

    for country in country_configs:
        try:
            print(f"🔍 Crawling: {country['name']} | Keyword: {country['keyword']}")
            df = crawl_shopee(keyword=country["keyword"], base_url=country["url"])
            all_data = pd.concat([all_data, df], ignore_index=True)
        except Exception as e:
            print(f"⚠️ Failed to crawl {country['name']}: {e}")

    save_to_gsheet(all_data)
