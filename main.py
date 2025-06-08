import asyncio
import pandas as pd
from pathlib import Path
from playwright.async_api import async_playwright
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn

console = Console()

async def scrape_decathlon(target=100):
    url = "https://www.decathlon.sg/c/all-sports.html?itm_source=hp&itm_medium=circlebanner&itm_campaign=desktop"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        console.print("[cyan]Navigating to Decathlon page...")
        await page.goto(url)
        await page.wait_for_timeout(5000)
        console.print("[green]Page loaded, starting scraping process...")

        products = []
        seen = set()
        last_seen_count = 0

        with Progress(SpinnerColumn(), "Scraping Progress", BarColumn(), TimeElapsedColumn(), console=console) as progress:
            task = progress.add_task("scraping", total=target)

            while len(products) < target:
                # Click “View More” button if present
                view_more = await page.query_selector('button[data-cy="Show-More"]')
                if view_more:
                    await view_more.click()
                    await asyncio.sleep(0.8)
                    console.print("[yellow]Clicked 'View More' to load more products.")
                else:
                    console.print("[red]No more 'View More' button found. Stopping.")
                    break

                cards = await page.query_selector_all('a[href^="/p/"]')
                console.print(f"[yellow]Found {len(cards)} product links in current DOM...")

                for card in cards:
                    status_el = await card.query_selector('span:has-text("PRICE DROP"), span:has-text("SALE"), span:has-text("NEW"), span:has-text("BEST"), span:has-text("LIMITED"), span:has-text("BUY"), span:has-text("ONLINE"), span:has-text("EXCLUSIVE")')
                    status = await status_el.text_content() if status_el else ''

                    name_el = await card.query_selector('div[title]')
                    name = await name_el.get_attribute('title') if name_el else 'N/A'

                    brand_el = await card.query_selector('div[data-testid="product-title-brand"], div.css-cxe9q1, div.clampLineOne')
                    brand = await brand_el.text_content() if brand_el else 'N/A'

                    price_el = await card.query_selector('span:has-text("$")')
                    price = await price_el.text_content() if price_el else 'N/A'

                    discount_el = await card.query_selector('span[data-part="sticker"]')
                    discount = await discount_el.text_content() if discount_el else ''

                    link = await card.get_attribute('href') or 'N/A'
                    product_url = f'https://www.decathlon.sg{link}' if link.startswith('/') else link

                    product = {
                        'Name': name.strip(),
                        'Price': price.strip(),
                        'Status': status.strip(),
                        'Brand': brand.strip(),
                        'Discount': discount.strip(),
                        'URL': product_url
                    }

                    unique_key = f'{name}-{price}-{brand}'
                    if unique_key not in seen:
                        products.append(product)
                        seen.add(unique_key)
                        progress.update(task, advance=1)

                    if len(products) >= target:
                        break

                if len(products) == last_seen_count:
                    console.print("[red]No new products detected. Stopping scraper.")
                    break
                last_seen_count = len(products)

        console.print(f"[bold green]Scraping completed. {len(products)} unique products extracted.")

        # Saving to csv/json
        df = pd.DataFrame(products[:target])
        csv_file = Path.cwd() / 'decathlon_products.csv'
        json_file = Path.cwd() / 'decathlon_products.json'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        df.to_json(json_file, orient='records', indent=2)

        console.print(f"[cyan]Saved to [bold]{csv_file}[/bold] and [bold]{json_file}[/bold].")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_decathlon(target=120))
