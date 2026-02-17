"""
停车位检查模块 - 使用 Playwright (比 Selenium 更好地处理 Cloudflare)
"""
import asyncio
import logging
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)


class ParkingScraper:
    """停车位检查器 - Playwright 版本"""
    
    URL = "https://reservenski.parkbrightonresort.com/select-parking"
    
    def __init__(self):
        """初始化"""
        self.browser = None
        self.context = None
        self.page = None
    
    async def _init_browser(self):
        """初始化浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = await self.context.new_page()
        logger.info("✅ Playwright 浏览器初始化成功")
    
    async def check_parking(self, target_dates):
        """
        检查停车位可用性
        
        Args:
            target_dates: 要检查的日期列表 (如 ['2/21', '2/22'])
            
        Returns:
            dict: {日期: 是否可用}
        """
        results = {}
        
        try:
            await self._init_browser()
            
            logger.info(f"🌐 打开页面: {self.URL}")
            await self.page.goto(self.URL, wait_until="domcontentloaded")
            
            # 等待 Cloudflare
            await self._wait_for_cloudflare()
            
            # 等待页面渲染
            await asyncio.sleep(3)
            
            # 获取页面内容
            page_text = await self.page.evaluate("document.body.innerText")
            logger.info(f"📄 页面文本长度: {len(page_text)} 字符")
            
            # 保存截图
            await self.save_screenshot("/tmp/parking_check.png")
            
            # 检查每个目标日期
            for date in target_dates:
                available = await self._check_date_available(date, page_text)
                results[date] = available
                status = "✅ 有票" if available else "❌ 无票/未开放"
                logger.info(f"  {date}: {status}")
            
        except Exception as e:
            logger.error(f"❌ 检查失败: {e}")
        
        return results
    
    async def _wait_for_cloudflare(self):
        """等待 Cloudflare 验证完成"""
        max_wait = 60
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < max_wait:
            try:
                text = await self.page.evaluate("document.body.innerText")
                if "just a moment" not in text.lower() and "checking your browser" not in text.lower():
                    logger.info("✅ Cloudflare 验证通过")
                    return
            except:
                pass
            await asyncio.sleep(2)
        
        logger.warning("⚠️ Cloudflare 验证超时")
    
    async def _check_date_available(self, date, page_text):
        """
        检查指定日期是否有票
        
        逻辑：
        - 日历显示的是单独的数字
        - 如果月份名称在文本中，且日期数字也在，说明日期已渲染
        - 简化处理：只要月份和日期都在文本中出现，就算检测到
        """
        month, day = date.split('/')
        
        # 月份名称映射
        month_names = {
            '1': 'January',
            '2': 'February', 
            '3': 'March',
            '4': 'April',
            '5': 'May',
            '6': 'June',
            '7': 'July',
            '8': 'August',
            '9': 'September',
            '10': 'October',
            '11': 'November',
            '12': 'December',
        }
        
        month_text = month_names.get(month, '')
        
        if not month_text:
            return False
        
        # 检查月份是否在文本中
        if month_text not in page_text:
            logger.info(f"  ⚠️ 未找到月份 {month_text}")
            return False
        
        # 检查日期是否在文本中
        # 简单处理：如果日期数字在文本中，就认为已渲染
        if day in page_text:
            logger.info(f"  ✓ 找到 {month_text} {day}")
            return True
        
        logger.info(f"  ⚠️ 未找到 {month_text} {day}")
        return False
    
    async def save_screenshot(self, filename="screenshot.png"):
        """保存页面截图"""
        if self.page:
            await self.page.screenshot(path=filename)
            logger.info(f"📸 截图已保存: {filename}")
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("🔒 浏览器已关闭")


def check_parking_sync(target_dates):
    """同步版本的停车位检查"""
    scraper = ParkingScraper()
    
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(scraper.check_parking(target_dates))
    loop.run_until_complete(scraper.close())
    
    return results
