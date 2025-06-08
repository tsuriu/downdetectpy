from playwright.async_api import async_playwright
import asyncio

async def scrape_downdetector_links(domain: str = "com.br"):
    url = f"https://downdetector.{domain}"
    links = []
    
    async with async_playwright() as p:
        # Launch browser with more natural settings
        browser = await p.chromium.launch(
            headless=True,
            slow_mo=100,  # Slow down interactions
        )
        
        # Create a new context with realistic viewport
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 1024},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        page = await context.new_page()
        
        try:
            # Navigate to the page with longer timeout
            await page.goto(url, timeout=60000)
            
            # Wait specifically for the content we need
            await page.wait_for_selector('div.company-index', timeout=10000)
            
            # Scroll to trigger lazy loading if needed
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # Get all company cards
            cards = await page.query_selector_all('div.company-index a[href]')
            
            for card in cards:
                try:
                    link = await card.get_attribute('href')
                    if link:
                        full_link = f"https://downdetector.{domain}{link}" if link.startswith('/') else link
                        company_name = link.split('/')[2] if len(link.split('/')) > 2 else 'unknown'
                        links.append({
                            "full_company_link": full_link,
                            "company_name": company_name
                        })
                except Exception as e:
                    print(f"Error processing card: {e}")
                    continue
            
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            # Close browser
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