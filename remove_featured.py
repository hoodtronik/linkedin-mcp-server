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
        page.set_default_timeout(10000)
        
        logger.info("Navigating to Featured section details...")
        await page.goto("https://www.linkedin.com/in/me/details/featured/")
        await asyncio.sleep(4)
        
        edit_buttons = await page.locator('button[aria-label*="Edit"], a[href*="/edit/"]').all()
        
        clicked = False
        for btn in edit_buttons:
            aria = await btn.get_attribute("aria-label") or ""
            text = await btn.text_content() or ""
            # Looking for standard edit buttons on the featured list
            if "Ilyas" in aria or "Highlight Reel" in aria or "feature" in aria.lower() or "Edit" in aria:
                await btn.click()
                clicked = True
                break
                
        if not clicked and edit_buttons:
            await edit_buttons[0].click()
            clicked = True
            
        if clicked:
            await page.wait_for_selector('div.artdeco-modal', timeout=5000)
            await asyncio.sleep(2)
            
            # Find the "Delete" button inside the dialog
            delete_btn = page.locator('div.artdeco-modal button:has-text("Delete")').first
            if await delete_btn.is_visible():
                await delete_btn.click()
                await asyncio.sleep(1)
                
                # Check for a second confirmation modal
                confirm_btn = page.locator('div.artdeco-modal button:has-text("Delete")').last
                if await confirm_btn.is_visible() and confirm_btn != delete_btn:
                    await confirm_btn.click()
                logger.info("Featured item successfully removed.")
            else:
                logger.error("Could not find 'Delete' button in modal.")
        else:
            logger.error("Could not find any edit buttons for Featured items.")

    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
    finally:
        if browser:
            await close_browser()

if __name__ == "__main__":
    asyncio.run(run())
