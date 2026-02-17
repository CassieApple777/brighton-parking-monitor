"""
Brighton Parking Monitor - 停车位监控主程序 (Playwright 版本)
"""
import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from parking_scraper import ParkingScraper
from notifier import DiscordNotifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


async def main_async():
    """异步主程序"""
    # 获取配置
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
    target_dates = os.getenv('TARGET_DATES', '2/21,2/22,2/28,3/1').split(',')
    target_dates = [d.strip() for d in target_dates]
    check_interval = int(os.getenv('CHECK_INTERVAL', '1800'))
    
    logger.info(f"🅿️ Brighton Parking Monitor 启动 (Playwright)")
    logger.info(f"📅 监控日期: {target_dates}")
    logger.info(f"⏰ 检查间隔: {check_interval}秒")
    
    # 初始化
    scraper = ParkingScraper()
    notifier = DiscordNotifier(webhook_url) if webhook_url else None
    
    # 记录上次通知的日期
    notified_dates = set()
    
    try:
        while True:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"[{current_time}] 开始检查停车位...")
            
            try:
                # 检查停车位
                results = await scraper.check_parking(target_dates)
                
                # 找出有票的日期
                available_dates = [d for d, available in results.items() if available]
                
                if available_dates:
                    logger.info(f"🎉 发现可用停车位: {available_dates}")
                    
                    # 发送通知
                    new_available = [d for d in available_dates if d not in notified_dates]
                    if new_available and notifier:
                        notifier.send_notification(new_available, results)
                        notified_dates.update(new_available)
                else:
                    logger.info(f"❌ 暂无可用停车位")
                    notified_dates.clear()
                    
            except Exception as e:
                logger.error(f"检查失败: {e}")
            
            # 等待下次检查
            logger.info(f"⏳ 等待 {check_interval} 秒后再次检查...")
            await asyncio.sleep(check_interval)
            
    except KeyboardInterrupt:
        logger.info("🛑 程序被用户停止")
    finally:
        await scraper.close()


def main():
    """主程序入口"""
    asyncio.run(main_async())


if __name__ == '__main__':
    main()
