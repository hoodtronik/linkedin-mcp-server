import asyncio
import json
from linkedin_mcp_server.drivers.browser import get_or_create_browser, ensure_authenticated, close_browser
from linkedin_mcp_server.scraping import LinkedInExtractor

async def run():
    try:
        username = "ilyasnashid"
        browser = await get_or_create_browser()
        await ensure_authenticated()
        extractor = LinkedInExtractor(browser.page)
        
        sections = {
            "about", "experience", "education", "skills", 
            "projects", "honors", "languages", "contact_info"
        }
        res = await extractor.scrape_person(username, sections)
        
        with open("profile_data_v2.json", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print("Profile data saved to profile_data_v2.json")
    finally:
        await close_browser()

asyncio.run(run())
