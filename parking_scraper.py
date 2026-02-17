"""
停车位检查模块 - 使用 Selenium
"""
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
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
            wait = WebDriverWait(self.driver, 20)
            
            # 等待日期选择器出现
            try:
                # 尝试找到日期选择元素
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div, button, input"))
                )
                logger.info("✅ 页面加载完成")
            except TimeoutException:
                logger.warning("⚠️ 页面加载超时")
            
            # 获取页面文本内容
            page_text = self.driver.page_source
            page_visible_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            logger.info(f"📄 页面内容长度: {len(page_text)} 字符")
            
            # 检查每个目标日期
            for date in target_dates:
                # 尝试多种方式查找日期
                available = self._check_date_available(date, page_text, page_visible_text)
                results[date] = available
                status = "✅ 有票" if available else "❌ 无票"
                logger.info(f"  {date}: {status}")
            
        except WebDriverException as e:
            logger.error(f"❌ WebDriver 错误: {e}")
            # 重置驱动
            self._init_driver()
        
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
        # 多种检测方式
        
        # 1. 在可见文本中查找日期
        if date in visible_text:
            # 检查是否有"available", "spots", "$"等表示有票的关键词
            # 找到日期所在区域，检查附近是否有可用标识
            return True
        
        # 2. 在页面源代码中查找
        # 注意：这个网站可能是动态加载的，所以需要检查JavaScript数据
        if date in page_source:
            return True
        
        # 3. 查找常见的"可用"关键词
        available_keywords = ['available', 'open', 'select', 'parking', 'spots']
        for keyword in available_keywords:
            if keyword.lower() in visible_text.lower():
                # 如果页面显示日期选择器，可能还没开放购买
                logger.info(f"  发现关键词 '{keyword}'，日期可能还未开放")
                break
        
        # 默认返回 False（需要人工确认）
        return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 浏览器已关闭")
