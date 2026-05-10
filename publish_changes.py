import asyncio
import logging
from patchright.async_api import Page, TimeoutError
from linkedin_mcp_server.drivers.browser import get_or_create_browser, ensure_authenticated, close_browser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def click_save(page: Page):
    save_btn = page.locator('div[role="dialog"] button:has-text("Save")').first
    if await save_btn.is_visible():
        await save_btn.click()
        await asyncio.sleep(2)
        return True
    return False

async def run():
    browser = None
    try:
        browser = await get_or_create_browser()
        await ensure_authenticated()
        page = browser.page
        
        # INCREASE TIMEOUT
        page.set_default_timeout(10000)

        # 1. HEADLINE
        try:
            logger.info("Updating Headline...")
            await page.goto("https://www.linkedin.com/in/")
            await asyncio.sleep(3)
            # Find the pencil in the top intro section
            edit_intro_btn = page.locator('main section').first.locator('button[aria-label*="Edit"]').first
            await edit_intro_btn.click()
            await page.wait_for_selector('div[role="dialog"]')
            
            headline = "Technical Artist @ Crossroads Wonderwall | XR Designer | AI Filmmaker | Unreal Engine 5 · Notch · Generative AI"
            headline_input = page.locator('input[id*="headline"], [role="dialog"] input[name*="headline"]').first
            if not await headline_input.is_visible():
                headline_input = page.get_by_label("Headline").first
            
            await headline_input.fill(headline)
            await click_save(page)
            logger.info("Headline updated.")
        except Exception as e:
            logger.error(f"Failed to update Headline: {e}")

        # 2. ABOUT
        try:
            logger.info("Updating About...")
            await page.goto("https://www.linkedin.com/in/")
            await asyncio.sleep(3)
            # Find "About" section pencil
            about_section = page.locator('section:has(div[id="about"])')
            about_pencil = about_section.locator('button[aria-label*="Edit"]').first
            if not await about_pencil.is_visible():
                # fallback
                about_pencil = page.locator('button[aria-label*="Edit about"]').first
            
            await about_pencil.click()
            await page.wait_for_selector('div[role="dialog"]')
            
            about_text = (
                "I'm a technical artist and AI creative technologist building immersive visual systems for live audiences and original cinematic IP for the screen.\n\n"
                "Currently on the Wonderwall Creative Team at Crossroads Church Oakley — an immersive LED canvas driven by Disguise media servers, Unreal Engine RenderStream, and GhostFrame, operating as a virtual production stage in front of a live congregation. I create real-time 3D environments and motion content in Unreal Engine 5, Notch, and Adobe Creative Suite for delivery to a 4K, 12 Gbps broadcast pipeline.\n\n"
                "Before this role I worked across XR design, 3D animation, and multimedia production — including projects for Republic, Atlantic, and Warner Records that have collected millions of views on YouTube, and earlier work as a recording artist with Tanya Morgan.\n\n"
                "Outside my day job I develop AI-assisted short films, AR experiences, and music. My work spans generative video models (Veo, Seedance, Kling, Runway, Sora, LTX, WAN, Hunyuan), AI image generation and LoRA training (Flux, SDXL, ComfyUI, Forge, Kohya), and Unity WebGL augmented reality (Unity 6, 8th Wall, custom MCP tooling). The Reallusion suite — iClone and Character Creator — sits in the middle of that pipeline as my control layer for character posing, animation, and Unreal Engine bridge work that drives downstream AI generation. I also build the systems behind the work: multi-agent coding workflows with Claude Code, custom Model Context Protocol tools, and prompt playbooks that make AI production repeatable instead of one-off.\n\n"
                "What I'm interested in: how studios, churches, brands, and creative teams can use AI not to replace imagination but to expand what small teams can ship — visually ambitious, narratively grounded, technically sound.\n\n"
                "Open to collaborations and consulting on AI production pipelines, virtual production, XR, and generative cinema."
            )
            about_input = page.locator('div[role="dialog"] textarea').first
            await about_input.fill(about_text)
            await click_save(page)
            logger.info("About updated.")
        except Exception as e:
            logger.error(f"Failed to update About: {e}")

        # 3. EXPERIENCE
        try:
            logger.info("Updating Experience...")
            await page.goto("https://www.linkedin.com/in/me/details/experience/")
            await asyncio.sleep(4)
            
            edit_buttons = await page.locator('a[href*="/edit/"], button[aria-label^="Edit experience"]').all()
            target_btn = None
            for btn in edit_buttons:
                text = await btn.text_content()
                aria = await btn.get_attribute("aria-label") or ""
                if "Crossroads" in aria or "Crossroads" in (text or "") or "Realtime Content Designer" in aria:
                    target_btn = btn
                    break
            
            if not target_btn:
                cards = await page.locator('li.pvs-list__paged-list-item').all()
                for card in cards:
                    text = await card.text_content()
                    if text and "Crossroads Church" in text and "Realtime Content Designer" in text:
                        target_btn = card.locator('a[href*="/edit/"], button[aria-label^="Edit"]').first
                        break
                        
            if target_btn:
                await target_btn.click()
                await page.wait_for_selector('div[role="dialog"]')
                await asyncio.sleep(2)
                
                # Update title
                await page.get_by_label("Title").first.fill("Technical Artist")
                
                # Update description
                desc = (
                    "Technical artist on the Wonderwall Creative Team at the Oakley campus — an immersive LED worship environment built on Disguise media servers, Unreal Engine RenderStream, and GhostFrame video processing, treating live worship as a virtual production stage rather than pre-rendered playback.\n\n"
                    "- Create real-time 3D environments and motion content in Unreal Engine 5 for delivery to a 4K, 12 Gbps broadcast pipeline\n"
                    "- Design supporting visuals in Notch and Adobe Creative Suite for service-driven content evolution\n"
                    "- Contribute to a multi-LED canvas system that transforms throughout a service rather than running fixed playback\n"
                    "- Foundational training in Disguise media server operation (not currently in production use at this role)"
                )
                desc_field = page.locator('div[role="dialog"] textarea').first
                await desc_field.fill(desc)
                
                await click_save(page)
                logger.info("Experience updated.")
            else:
                logger.error("Could not find edit button for Crossroads Church experience.")
        except Exception as e:
            logger.error(f"Failed to update Experience: {e}")

        # 4. TURN OFF OPEN TO WORK
        try:
            logger.info("Turning off Open to Work...")
            await page.goto("https://www.linkedin.com/in/")
            await asyncio.sleep(3)
            
            otw_edit = page.locator('a[href*="open-to-work"], button[aria-label*="Edit Open to work"]').first
            if await otw_edit.is_visible():
                await otw_edit.click()
                await page.wait_for_selector('div[role="dialog"]')
                await asyncio.sleep(1)
                del_btn = page.locator('button:has-text("Delete from profile"), button:has-text("Remove")').first
                if await del_btn.is_visible():
                    await del_btn.click()
                    await asyncio.sleep(1)
                    confirm_del = page.locator('div[role="dialog"] button:has-text("Delete"), div[role="dialog"] button:has-text("Remove")').last
                    await confirm_del.click()
                    logger.info("Open to work disabled.")
                else:
                    logger.error("Could not find delete button in Open to work dialog.")
            else:
                logger.error("Could not find Open to work edit button on profile.")
        except Exception as e:
            logger.error(f"Failed to turn off Open to Work: {e}")

        # 5. SKILLS
        try:
            logger.info("Adding Skills...")
            skills_to_add = [
                "Unreal Engine 5", "Notch", "Adobe Creative Suite", "Virtual Production", "Real-Time 3D", 
                "LED Wall Content", "RenderStream", "Disguise", "Broadcast Content Pipelines", "Motion Design",
                "Reallusion iClone", "Reallusion Character Creator", "Character Animation", "Character Rigging", 
                "Unreal Engine Bridge Workflows", "Generative AI", "AI Filmmaking", "AI Video Production", 
                "Generative Video", "Prompt Engineering", "AI Cinematography", "AI Image Generation", 
                "Character Consistency Workflows", "Visual Development", "Concept Art", "LoRA Training", 
                "Dataset Curation", "ComfyUI", "Forge", "Flux", "SDXL", "Kohya", "Hunyuan Video", "WAN", "Veo", 
                "Seedance", "Kling", "Runway", "Sora", "Local LLM Deployment", "LM Studio", "AI Music Production", 
                "Suno", "Generative Audio", "Voice Conversion (RVC)", "AI-Assisted Songwriting", "XR Design", 
                "Augmented Reality (AR)", "WebAR", "Unity 6", "Unity WebGL", "8th Wall", "Immersive Media", 
                "Multi-Agent AI Workflows", "Claude Code", "Model Context Protocol (MCP)", 
                "Custom MCP Tool Development", "AI Workflow Design", "Agentic Prompt Engineering"
            ]
            
            for skill in skills_to_add:
                try:
                    await page.goto("https://www.linkedin.com/in/me/details/skills/")
                    await asyncio.sleep(2)
                    add_btn = page.locator('button[aria-label^="Add skill"], span:has-text("Add skill")').first
                    await add_btn.click()
                    await page.wait_for_selector('div[role="dialog"]')
                    
                    input_box = page.locator('[role="dialog"] input[type="text"]').first
                    await input_box.fill(skill)
                    await asyncio.sleep(1)
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(0.5)
                    await click_save(page)
                    logger.info(f"Skill '{skill}' added.")
                except Exception as e:
                    logger.error(f"Failed to add skill '{skill}': {e}")
                    
        except Exception as e:
            logger.error(f"Failed during skills loop: {e}")

        logger.info("All updates complete!")

    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
    finally:
        if browser:
            await close_browser()

if __name__ == "__main__":
    asyncio.run(run())
