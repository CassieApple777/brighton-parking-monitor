"""
测试脚本 - 使用 Playwright 测试停车位检查
"""
import asyncio
from parking_scraper import ParkingScraper

async def test():
    print("🧪 开始测试 (Playwright)...")
    
    scraper = ParkingScraper()
    results = await scraper.check_parking(['2/21', '2/22', '2/28', '3/1', '3/20'])
    
    print("\n📊 检查结果:")
    for date, available in results.items():
        status = "✅ 有票" if available else "❌ 无票/未开放"
        print(f"  {date}: {status}")
    
    await scraper.save_screenshot("/tmp/test_result.png")
    await scraper.close()
    
    print("\n✅ 测试完成!")

if __name__ == '__main__':
    asyncio.run(test())
