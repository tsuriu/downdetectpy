from playwright.async_api import async_playwright
import asyncio

async def scrape_downdetector_links(domain: str = "com.br"):
    url = f"https://downdetector.{domain}"
    links = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            slow_mo=100,
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 1024},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        page = await context.new_page()
        
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_selector('div.company-index', timeout=10000)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            cards = await page.query_selector_all('div.company-index a[href]')
            
            for card in cards:
                try:
                    link = await card.get_attribute('href')
                    full_link = f"https://downdetector.{domain}{link}" if link and link.startswith('/') else link
                    company_name = link.split('/')[2] if link and len(link.split('/')) > 2 else 'unknown'

                    # Try to get the logo inside the card
                    img = await card.query_selector('img')
                    logo_url = None
                    if img:
                        logo_url = await img.get_attribute('data-original') or await img.get_attribute('src')

                    links.append({
                        "full_company_link": full_link,
                        "company_name": company_name,
                        "logo_url": logo_url
                    })
                except Exception as e:
                    print(f"Error processing card: {e}")
                    continue
            
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            await context.close()
            await browser.close()
    
    return links

async def main():
    service_links = await scrape_downdetector_links()
    print(f"Found {len(service_links)} links:")
    for link in service_links:
        print(link)

if __name__ == "__main__":
    asyncio.run(main())