"""
停车位检查模块 - 使用 Selenium
"""
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)


class ParkingScraper:
    """停车位检查器"""
    
    URL = "https://reservenski.parkbrightonresort.com/select-parking"
    
    def __init__(self):
        """初始化浏览器"""
        self.driver = None
        self._init_driver()
    
    def _init_driver(self):
        """初始化 Chrome 驱动"""
        chrome_options = Options()
        
        # 反检测选项
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        
        # 更真实的浏览器指纹
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User Agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 禁用图片加载以提高速度
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(60)
            
            # 移除 webdriver 标志
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            logger.info("✅ Chrome 驱动初始化成功")
        except Exception as e:
            logger.error(f"❌ 驱动初始化失败: {e}")
            raise
    
    def check_parking(self, target_dates):
        """
        检查停车位可用性
        
        Args:
            target_dates: 要检查的日期列表 (如 ['2/21', '2/22'])
            
        Returns:
            dict: {日期: 是否可用}
        """
        results = {}
        
        try:
            logger.info(f"🌐 打开页面: {self.URL}")
            self.driver.get(self.URL)
            
            # 等待页面加载
            wait = WebDriverWait(self.driver, 60)
            
            # 等待 Cloudflare 挑战完成
            try:
                # 等待页面主要元素出现
                wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                logger.info("✅ 页面加载完成")
                
                # 等待 Cloudflare 挑战完成 - 反复检查直到通过
                max_wait = 60
                start_time = time.time()
                cf_passed = False
                
                while time.time() - start_time < max_wait:
                    try:
                        body = self.driver.find_element(By.TAG_NAME, "body")
                        page_text = body.text
                        
                        # 保存中间截图用于调试
                        if int(time.time() - start_time) % 15 == 0:
                            self.save_screenshot(f"debug_{int(time.time())}.png")
                        
                        # 检查 Cloudflare 是否通过
                        if "just a moment" not in page_text.lower() and "checking your browser" not in page_text.lower():
                            cf_passed = True
                            logger.info(f"✅ Cloudflare 验证通过 ({int(time.time() - start_time)}s)")
                            break
                    except Exception as e:
                        pass
                    
                    time.sleep(2)
                    elapsed = int(time.time() - start_time)
                    if elapsed % 10 == 0:
                        logger.info(f"⏳ 等待 Cloudflare 验证... ({elapsed}s)")
                        
                if not cf_passed:
                    logger.warning("⚠️ Cloudflare 验证超时，尝试继续...")
                    
            except TimeoutException:
                logger.warning("⚠️ 页面加载超时")
            
            # 等待日期选择器加载
            logger.info("⏳ 等待 React 应用渲染...")
            time.sleep(8)
            
            # 获取页面文本内容
            page_text = self.driver.page_source
            page_visible_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            logger.info(f"📄 页面内容长度: {len(page_text)} 字符")
            logger.info(f"📄 可见文本长度: {len(page_visible_text)} 字符")
            
            # 保存截图用于调试
            self.save_screenshot("debug_screenshot.png")
            
            # 检查每个目标日期
            for date in target_dates:
                available = self._check_date_available(date, page_text, page_visible_text)
                results[date] = available
                status = "✅ 有票" if available else "❌ 无票/未开放"
                logger.info(f"  {date}: {status}")
            
        except WebDriverException as e:
            logger.error(f"❌ WebDriver 错误: {e}")
            try:
                self._init_driver()
            except:
                pass
        
        except Exception as e:
            logger.error(f"❌ 检查失败: {e}")
        
        return results
    
    def _check_date_available(self, date, page_source, visible_text):
        """
        检查指定日期是否有票
        
        Args:
            date: 日期 (如 '2/21')
            page_source: 页面源代码
            visible_text: 可见文本
            
        Returns:
            bool: 是否有票
        """
        month, day = date.split('/')
        
        # 1. 精确匹配日期格式
        date_formats = [
            f"Feb {day}",
            f"February {day}",
            f"{month}/{day}",
            f"2025-{month}-{day.zfill(2)}",
            f"2026-{month}-{day.zfill(2)}",
            f"'{day}",
        ]
        
        for fmt in date_formats:
            if fmt in visible_text:
                logger.info(f"  ✓ 找到日期 {date} 的信息")
                return True
        
        for fmt in date_formats:
            if fmt in page_source:
                logger.info(f"  ✓ 在页面源码找到日期 {date}")
                return True
        
        # 2. 检查是否已售罄
        sold_out_keywords = ['sold out', 'unavailable', 'full', 'closed', 'sold-out', 'no parking']
        for keyword in sold_out_keywords:
            if keyword.lower() in visible_text.lower():
                logger.info(f"  ✗ 发现 '{keyword}'，该日期可能无票")
                return False
        
        # 3. 如果还在显示日期选择器/日历
        calendar_keywords = ['calendar', 'select date', 'choose date', 'month']
        for keyword in calendar_keywords:
            if keyword.lower() in visible_text.lower():
                logger.info(f"  ⏳ 页面显示日期选择器，可能还未开放购买")
                return False
        
        # 4. 检查是否还在 Cloudflare 页面
        if "just a moment" in visible_text.lower() or "checking your browser" in visible_text.lower():
            logger.info(f"  ⏳ Cloudflare 验证中...")
            return False
        
        logger.info(f"  ⚠️ 无法确定 {date} 的状态")
        return False
    
    def save_screenshot(self, filename="screenshot.png"):
        """保存页面截图"""
        if self.driver:
            self.driver.save_screenshot(filename)
            logger.info(f"📸 截图已保存: {filename}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            logger.info("🔒 浏览器已关闭")
