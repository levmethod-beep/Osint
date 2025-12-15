import asyncio
from playwright.async_api import async_playwright

async def test_with_playwright():
    vehicle_number = "UP72H6726"
    url = f"http://india.42web.io/vehicle/?q={vehicle_number}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to the page and wait for it to load
        await page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Wait a bit for JavaScript to execute
        await asyncio.sleep(2)
        
        # Wait for JSON to appear or wait for redirects to complete
        try:
            # Wait for JSON content to appear
            await page.wait_for_function(
                "document.body.innerText.trim().startsWith('{')",
                timeout=10000
            )
        except:
            # If timeout, continue anyway
            pass
        
        # Get the page content
        content = await page.content()
        print(f"Page content length: {len(content)}")
        
        # Try to get JSON from the page text
        text = await page.inner_text('body')
        print(f"Body text length: {len(text)}")
        print(f"Final URL: {page.url}")
        
        # Check if we got JSON
        if text.strip().startswith('{'):
            print("Found JSON response!")
            print(text)
        else:
            print("First 1000 chars of body:")
            print(text[:1000])
            
            # Try to intercept network response
            print("\nTrying to intercept network response...")
            # Make another request and wait for JSON response
            try:
                response = await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(3)
                text2 = await page.inner_text('body')
                if text2.strip().startswith('{'):
                    print("Found JSON on retry!")
                    print(text2)
            except Exception as e:
                print(f"Retry error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_with_playwright())

