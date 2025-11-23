from loguru import logger
from i18n import t
import pandas as pd
from playwright.sync_api import sync_playwright

import time
import json

import src.core.global_config as config
from src.core.image_file import ImageFile
from src.interface.file_dialog import select_scv


def get_keywords(page):
    keywords_elements = page.query_selector_all(
        '#details-keywords span, #details-keywords a, [data-t="keywords-section"] span, [data-t="keywords-section"] a')
    keywords = []
    for keyword in keywords_elements:
        keyword = keyword.text_content().strip()
        if keyword and not keyword in ["Similar Keywords", "Show less"]:
            keywords.append(keyword)
        if any("Show all" in keyword for keyword in keywords):
            page.click("text=Show all")
            time.sleep(0.5)
            return get_keywords(page)
    return list(dict.fromkeys(keywords))

def parse_sales_data():
    message = t("info.scripts.parse_sales_data.message")

    # Чтение CSV без заголовка
    sales_file = select_scv(title=message)

    columns = [
        "sell_time",
        "media_id",
        "media_name",
        "sell_type",
        "sell_income",
        "media_type",
        "media_filename",
        "author",
        "media_resolution",
        "media_ai_flag",
        "media_link",
        "media_preview",
    ]
    media_type_map = {
        "photos": "images",
        "videos": "video"
    }

    # Чтение CSV без заголовка
    df = pd.read_csv(sales_file, header=0, dtype=str)
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    df.fillna("", inplace=True)

    cache = {}

    # Построчная обработка
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not config.DEBUG)

        for index, row in df.iterrows():
            media_id = row["media_id"]
            media_type_key = row["media_type"]

            if media_id in cache:
                cached_data = cache[media_id]
                for key, value in cached_data.items():
                    df.at[index, key] = value
                logger.info(f"[{index}] [{cached_data['media_type']}] [cached] {media_id} ✔️")
                continue

            media_type = "???"
            for _ in range(5):
                try:
                    media_type = media_type_map[media_type_key]
                    author = row["author"]
                    url = f"https://stock.adobe.com/{media_type}/{author}/{media_id}?locale=en_US"
                    page = browser.new_page()
                    page.goto(url)

                    ai_flag = bool(page.query_selector(".gen-ai__label"))
                    preview = page.get_attribute(
                        'div[data-t="details-thumbnail-wrapper"] picture img' if media_type == "images" else ".player-content video",
                        "src" if media_type == "images" else "poster"
                    )

                    # Сохраняем в датафрейм
                    df.at[index, 'media_link'] = url
                    df.at[index, 'media_ai_flag'] = ai_flag
                    df.at[index, 'media_preview'] = preview

                    # Сохраняем в кэш
                    cache[media_id] = {
                        "media_type": media_type,
                        "media_link": url,
                        "media_ai_flag": ai_flag,
                        "media_preview": preview
                    }

                    logger.info(f"[{index}] [{media_type}] [{"AI" if ai_flag else "not AI"}] {media_id} ✔️")
                    df.to_csv(sales_file, index=False)
                    break
                except Exception:
                    logger.info(f"[{index}] [{media_type}] [???] {media_id} trying again…")
            else:
                logger.info(f"[{index}] [{media_type}] [???] {media_id} ❌")
        browser.close()