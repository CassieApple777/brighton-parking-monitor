"""
Playwright 版本的停车位检查 - 可能更好地处理 Cloudflare
"""
import asyncio
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_parking():
    """使用 Playwright 检查停车位"""
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        logger.info("🌐 打开页面...")
        await page.goto("https://reservenski.parkbrightonresort.com/select-parking")
        
        # 等待页面加载
        await page.wait_for_load_state("networkidle", timeout=60000)
        
        # 等待 Cloudflare
        logger.info("⏳ 等待 Cloudflare...")
        for i in range(30):
            await asyncio.sleep(2)
            text = await page.evaluate("document.body.innerText")
            if "just a moment" not in text.lower() and "checking your browser" not in text.lower():
                break
            logger.info(f"Cloudflare 检查中... {i*2}s")
        
        # 等待 React 渲染
        await asyncio.sleep(5)
        
        # 获取页面内容
        content = await page.content()
        text = await page.evaluate("document.body.innerText")
        
        logger.info(f"📄 内容长度: {len(content)} 字符")
        logger.info(f"📄 可见文本: {len(text)} 字符")
        logger.info(f"📝 文本内容: {text[:500]}...")
        
        # 保存截图
        await page.screenshot(path="/tmp/playwright_test.png")
        logger.info("📸 截图已保存")
        
        # 检查日期
        dates = ['2/21', '2/22', '2/28', '3/1', '3/20']
        for date in dates:
            if date in content:
                logger.info(f"✓ 找到日期: {date}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(check_parking())
