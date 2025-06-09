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
            
            # Updated selector based on the HTML sample
            cards = await page.query_selector_all('div.company-index a[href]')
            
            for card in cards:
                try:
                    link = await card.get_attribute('href')
                    full_link = f"https://downdetector.{domain}{link}" if link and link.startswith('/') else link

                    # Extract company name from href or title
                    company_name = link.split('/')[2] if link and len(link.split('/')) > 2 else 'unknown'
                    title = await card.get_attribute('title')
                    if title:
                        company_name = title

                    # Get the logo - looking at data-original first, then src
                    img = await card.query_selector('img')
                    logo_url = None
                    if img:
                        logo_url = await img.get_attribute('data-original')
                        if not logo_url:
                            logo_url = await img.get_attribute('src')
                        # Clean up logo URL if needed
                        if logo_url and logo_url.startswith('//'):
                            logo_url = f'https:{logo_url}'
                        elif logo_url and not logo_url.startswith('http'):
                            logo_url = f'https://downdetector.{domain}{logo_url}'


                    # Get SVG data attributes
                    svg_data = {}
                    svg_element = await card.query_selector('svg')
                    if svg_element:
                        # Extract all SVG data attributes
                        svg_data['data_values'] = await svg_element.get_attribute('data-values')
                        svg_data['data_min'] = await svg_element.get_attribute('data-min')
                        svg_data['data_max'] = await svg_element.get_attribute('data-max')
                        svg_data['data_mean'] = await svg_element.get_attribute('data-mean')
                        svg_data['data_stddev'] = await svg_element.get_attribute('data-stddev')

                        # If min/max/mean/stddev are null, try to calculate from data-values
                        if svg_data['data_values'] and (not svg_data['data_min'] or not svg_data['data_max'] or not svg_data['data_mean']):
                            try:
                                # Clean and parse the data-values string into numbers
                                # Remove brackets, quotes, and other non-numeric characters except commas and numbers
                                cleaned_data = svg_data['data_values'].replace('[', '').replace(']', '').replace('"', '').replace("'", '')
                                values = []
                                for x in cleaned_data.split(','):
                                    x = x.strip()
                                    if x and x.replace('.', '').replace('-', '').isdigit():
                                        values.append(float(x))
                                if values:
                                    if not svg_data['data_min']:
                                        svg_data['data_min'] = str(min(values))
                                    if not svg_data['data_max']:
                                        svg_data['data_max'] = str(max(values))
                                    if not svg_data['data_mean']:
                                        svg_data['data_mean'] = str(sum(values) / len(values))
                                    if not svg_data['data_stddev']:
                                        # Calculate standard deviation
                                        mean_val = sum(values) / len(values)
                                        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
                                        svg_data['data_stddev'] = str(variance ** 0.5)
                            except (ValueError, AttributeError) as e:
                                print(f"Error calculating SVG stats: {e}")

                        # Extract last status from SVG class (first string split by space)
                        svg_class = await svg_element.get_attribute('class')
                        if svg_class:
                            svg_data['last_status'] = svg_class.split()[0] if svg_class.split() else None
                        else:
                            svg_data['last_status'] = None

                    links.append({
                        "full_company_link": full_link,
                        "company_name": company_name,
                        "logo_url": logo_url,
                        "svg_data": svg_data
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