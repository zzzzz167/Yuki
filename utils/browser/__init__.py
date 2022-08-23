from playwright.async_api import Page, Browser, async_playwright, Playwright
from contextlib import asynccontextmanager
from typing import Optional, AsyncIterator

_browser: Optional[Browser] = None
_playwright: Optional[Playwright] = None


async def init(**kwargs) -> Browser:
    global _browser
    global _playwright
    if _browser:
        return _browser
    _playwright = await async_playwright().start()
    _browser = await launch_browser(**kwargs)
    return _browser


async def get_browser(**kwargs) -> Browser:
    return await init(**kwargs)


async def launch_browser(**kwargs) -> Browser:
    return await _playwright.chromium.launch(**kwargs)


@asynccontextmanager
async def get_new_page(**kwargs) -> AsyncIterator[Page]:
    browser = await get_browser()
    page = await browser.new_page(**kwargs)
    try:
        yield page
    finally:
        await page.close()


async def shutdown_browser():
    await _browser.close()
    await _playwright.stop()
