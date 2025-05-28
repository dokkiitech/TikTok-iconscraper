import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def get_icon_urls(input_file="urls.txt", output_file="tiktok_icons.csv"):
    results = []

    with open(input_file, "r") as f:
        urls = [line.strip().split("?")[0] for line in f if line.strip()]  # ?lang=ja-JPとか消す

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for url in urls:
            try:
                if "/video/" in url:
                    username = url.split("/@")[1].split("/")[0]
                    profile_url = f"https://www.tiktok.com/@{username}"
                else:
                    username = url.split("/@")[1]
                    profile_url = url

                await page.goto(profile_url, timeout=20000)
                await page.wait_for_selector("img", timeout=10000)

                # アイコン画像のURL取得
                img = await page.query_selector("img[class*=profile]") or await page.query_selector("img")
                img_url = await img.get_attribute("src") if img else ""

                print(f"✅ {username}: {img_url}")
                results.append({"username": username, "img_url": img_url})
            except Exception as e:
                print(f"❌ Error: {url} - {e}")
                results.append({"username": username, "img_url": ""})

        await browser.close()

    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"📦 保存完了！→ {output_file}")

if __name__ == "__main__":
    asyncio.run(get_icon_urls())
