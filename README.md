# 微信金融新闻小助手

每日自动采集金融新闻，调用 DeepSeek 生成简报，并通过企业微信群机器人推送。

## 工作流程

```
采集新闻（新浪财经 / 华尔街见闻 / 财联社）
    ↓
DeepSeek 总结为 200-300 字每日简报
    ↓
企业微信群机器人推送
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

复制 `.env.example` 为 `.env`，填入以下信息：

| 配置项 | 说明 | 获取方式 |
|-------|------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | https://platform.deepseek.com |
| `WEWORK_WEBHOOK_URL` | 企业微信群机器人 Webhook | 群设置 → 群机器人 → 添加 |

### 3. 运行

```bash
python src/main.py
```

### 4. 设置定时任务（可选）

每天早上 8:00 自动执行，即使未登录桌面也能运行：

```bash
schtasks /create /tn "FinanceNewsDigest" /tr "python D:\Finance\src\main.py" /sc daily /st 08:00 /ru SYSTEM /f
```

## 项目结构

```
├── config/
│   └── config.py          # 配置读取
├── src/
│   ├── main.py            # 主入口
│   ├── collector/
│   │   ├── engine.py      # 采集引擎（去重合并）
│   │   └── sources.py     # 各新闻源适配器
│   ├── summarizer/
│   │   └── summarizer.py  # DeepSeek 总结
│   └── pusher/
│       └── pusher.py      # 企业微信推送
├── .env.example           # 配置模板
├── requirements.txt
└── README.md
```

## 新闻来源

- **新浪财经** — 滚动新闻 API（综合 / 国内 / 国际）
- **华尔街见闻** — 全球快讯 API
- **财联社** — 电报页面
- **东方财富** — 指数行情（备用，当前接口不稳定）
