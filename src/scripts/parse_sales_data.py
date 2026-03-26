import asyncio
import json
from pathlib import Path

import numpy as np
import pandas as pd
from i18n import t
from loguru import logger
from playwright.async_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError, async_playwright
from tqdm.asyncio import tqdm_asyncio

import src.core.global_config as config
from src.interface.file_dialog import select_csv
from .core_script import InfographicsScripts

CACHE_DIR = Path("cached")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / "sales_data_cached.json"
MEDIA_MAP = {
    "photos": "images",
    "videos": "video",
    "illustrations": "images",
    "vectors": "images",
}


class ParseSalesData(InfographicsScripts):
    CONFIG_PARAMETERS = ["timeout"]

    cache_error_locale = "info.scripts.parse_sales_data.cache_error"
    fetch_error_locale = "info.scripts.parse_sales_data.fetch_error"
    cache_hit_locale = "info.scripts.parse_sales_data.cache_hit"
    fetched_locale = "info.scripts.parse_sales_data.fetched"
    timeout_locale = "info.scripts.parse_sales_data.timeout"
    progress_locale = "info.scripts.parse_sales_data.progress"
    merged_locale = "info.scripts.parse_sales_data.merged"
    resume_locale = "info.scripts.parse_sales_data.resume"

    @classmethod
    def _load_cache(cls):
        if CACHE_FILE.exists():
            try:
                with CACHE_FILE.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                logger.warning(t(cls.cache_error_locale))
        return {}

    @classmethod
    def _save_cache(cls, cache):
        with CACHE_FILE.open("w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    @classmethod
    async def _fetch_record(cls, browser, row: dict, cache: dict, lock: asyncio.Lock):
        media_id = row["media_id"]

        if media_id in cache:
            if "error" in cache[media_id]:
                e = cache[media_id]['error']
                logger.error(t(cls.fetch_error_locale).format(media_id=media_id, error=e))
                return "skip"
            logger.info(t(cls.cache_hit_locale).format(media_id=media_id))
            return cache[media_id]

        media_type = MEDIA_MAP.get(row["media_type"])
        if not media_type:
            e = f"Wrong media type: \"{row['media_type']}\""
            cache[media_id] = {"error": e}
            cls._save_cache(cache)
            logger.error(t(cls.fetch_error_locale).format(media_id=media_id, error=e))
            return "skip"

        url = f"https://stock.adobe.com/{media_type}/{row['author']}/{media_id}?locale=en_US"

        try:
            async with lock:
                page = await browser.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=cls.get_config()["timeout"] * 1000)
                if page.url == "https://stock.adobe.com/404":
                    e = f"Wrong url: \"{url}\""
                    cache[media_id] = {"error": e}
                    cls._save_cache(cache)
                    logger.error(t(cls.fetch_error_locale).format(media_id=media_id, error=e))
                    return "skip"

                preview_selector = (
                    'div[data-t="details-thumbnail-wrapper"] picture img'
                    if media_type == "images" else ".player-content video"
                )
                await page.wait_for_selector(preview_selector, timeout=cls.get_config()["timeout"] * 1000)

                preview_attr = "src" if media_type == "images" else "poster"
                preview = await page.get_attribute(preview_selector, preview_attr)

                ai_flag_selector = ".gen-ai__label"
                ai_flag = bool(await page.query_selector(ai_flag_selector))

                result = {
                    "media_link": url,
                    "media_ai_flag": ai_flag,
                    "media_preview": preview,
                }

                cache[media_id] = result
                cls._save_cache(cache)

                logger.info(t(cls.fetched_locale).format(media_id=media_id))
                return result

        except (PlaywrightTimeoutError, PlaywrightError) as e:
            cache[media_id] = {"error": str(e)}
            cls._save_cache(cache)
            logger.warning(t(cls.timeout_locale).format(media_id=media_id, url=url))
            return "timeout"

        except Exception as e:
            cache[media_id] = {"error": str(e)}
            cls._save_cache(cache)
            logger.error(t(cls.fetch_error_locale).format(media_id=media_id, error=e))
            return "skip"

        finally:
            await page.close()

    @classmethod
    async def _run(cls):
        lock = asyncio.Lock()

        try:
            sales_file: Path = select_csv()
        except RuntimeError as e:
            logger.error(e)
            return

        required_columns = [
            "sell_time", "media_id", "media_name", "sell_type", "sell_income",
            "media_type", "media_filename", "author", "media_resolution",
            "media_ai_flag", "media_link", "media_preview"
        ]

        df = pd.read_csv(sales_file, dtype=str, header=None)
        while len(df.columns) < len(required_columns):
            df[len(df.columns)] = ""
        df.columns = required_columns

        parsed_file = sales_file.with_name(sales_file.stem + "_parsed.csv")

        if parsed_file.exists():
            df_prev = pd.read_csv(parsed_file, dtype=str)
            for col in ["media_ai_flag", "media_link", "media_preview"]:
                if col in df_prev.columns:
                    df_prev[col] = df_prev[col].replace("", np.nan)
            for idx, row in df.iterrows():
                media_id = row["media_id"]
                matches = df_prev[df_prev["media_id"] == media_id]
                if not matches.empty:
                    for col in ["media_ai_flag", "media_link", "media_preview"]:
                        if not row[col] or row[col] == "nan":
                            val = matches[col].dropna().iloc[0] if not matches[col].dropna().empty else row[col]
                            df.at[idx, col] = val
            logger.info(t(cls.merged_locale))
            logger.info(t(cls.resume_locale))

        cache = cls._load_cache()

        to_process = [
            (idx, row) for idx, row in df.iterrows()
            if (not row["media_link"] or row["media_link"] == "nan") and
               (row["media_id"] not in cache or "error" not in cache[row["media_id"]])
        ]

        if to_process:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=not config.DEBUG)

                async def bounded_fetch(idx, row):
                    if row["media_id"] in cache and "error" in cache[row["media_id"]]:
                        return idx, "skip"
                    result = await cls._fetch_record(browser, row, cache, lock)
                    return idx, result

                queue = to_process

                with tqdm_asyncio(total=len(queue), desc=t(cls.progress_locale)) as pbar:
                    while queue:
                        tasks = [bounded_fetch(idx, row) for idx, row in queue]
                        queue = []

                        for fut in asyncio.as_completed(tasks):
                            idx, res = await fut

                            if res == "timeout":
                                queue.append((idx, df.iloc[idx]))
                            elif res == "skip":
                                pass
                            elif res:
                                for k, v in res.items():
                                    df.at[idx, k] = v
                                df.to_csv(parsed_file, index=False)

                            if not res == "skip":
                                pbar.update(1)

                await browser.close()
