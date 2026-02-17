# Brighton Parking Monitor

自动监控 Brighton 滑雪场停车位，有票时发送 Discord 通知。

## 功能

- 🤖 使用 Selenium 自动化浏览器检查停车位
- ⏰ 每30分钟自动检查一次
- 📅 支持监控多个日期
- 🔔 有票时通过 Discord Webhook 发送通知

## 安装

```bash
# 克隆项目
git clone https://github.com/cassiesu777/brighton-parking-monitor.git
cd brighton-parking-monitor

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 配置

1. 复制 `.env.example` 为 `.env`：
```bash
cp .env.example .env
```

2. 编辑 `.env` 配置：
```env
# Discord Webhook URL (可选)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# 要监控的日期 (月/日 格式，多个用逗号分隔)
TARGET_DATES=2/21,2/22,2/28,3/1

# 检查间隔 (秒)
CHECK_INTERVAL=1800
```

## 运行

```bash
python main.py
```

## Docker 运行

```bash
docker build -t parking-monitor .
docker run -d --env-file .env parking-monitor
```

## 项目结构

```
brighton-parking-monitor/
├── .env.example          # 环境变量示例
├── .gitignore
├── Dockerfile
├── requirements.txt
├── main.py               # 主程序
├── parking_scraper.py    # 停车位检查逻辑
├── notifier.py           # 通知模块
└── README.md
```
