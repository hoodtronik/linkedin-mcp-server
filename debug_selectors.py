import asyncio
import logging
from patchright.async_api import Page, TimeoutError
from linkedin_mcp_server.drivers.browser import get_or_create_browser, ensure_authenticated, close_browser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run():
    browser = None
    try:
        browser = await get_or_create_browser()
        await ensure_authenticated()
        page = browser.page
        
        await page.goto("https://www.linkedin.com/in/")
        await asyncio.sleep(4)
        
        logger.info("Extracting all button aria-labels from main section...")
        buttons = await page.locator('main button').all()
        for i, btn in enumerate(buttons):
            aria = await btn.get_attribute('aria-label')
            text = await btn.text_content()
            if aria:
                logger.info(f"Btn {i}: aria='{aria}', text='{text.strip() if text else ''}'")

    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
    finally:
        if browser:
            await close_browser()

if __name__ == "__main__":
    asyncio.run(run())
