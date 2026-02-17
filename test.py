"""
测试脚本 - 快速测试停车位检查功能
"""
import logging
from parking_scraper import ParkingScraper

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test():
    """测试停车位检查"""
    print("🧪 开始测试...")
    
    scraper = ParkingScraper()
    
    # 测试检查几个日期
    target_dates = ['2/21', '2/22', '2/28', '3/1', '3/20']
    results = scraper.check_parking(target_dates)
    
    print("\n📊 检查结果:")
    for date, available in results.items():
        status = "✅ 有票" if available else "❌ 无票/未开放"
        print(f"  {date}: {status}")
    
    # 保存截图
    scraper.save_screenshot("test_screenshot.png")
    print("📸 截图已保存: test_screenshot.png")
    
    scraper.close()
    
    print("\n✅ 测试完成!")

if __name__ == '__main__':
    test()
