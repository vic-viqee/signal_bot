Crypto Signal Bot 📈

A Python-based crypto trading signal bot that monitors markets 24/7 using technical analysis (RSI) and sends instant alerts to Telegram when assets are overbought or oversold.

Features 🚀

Multi-Asset Monitoring
Tracks BTC, ETH, SOL, and XRP (easy to extend).

RSI-Based Signals
Uses the Relative Strength Index to detect market extremes.

Telegram Control
Receive alerts and control the bot via Telegram commands.

Always-On Design
Runs continuously with configurable intervals.

Privacy-Friendly
No wallet access or trading API keys required.

How It Works 🧠

The bot runs in a simple loop:

Fetch Data
Pulls the last 7 days of hourly price data from Yahoo Finance.

Analyze
Computes the 14-period RSI indicator.

Generate Signals

BUY → RSI < 30 (oversold)

SELL → RSI > 70 (overbought)

Notify
Sends a Telegram alert immediately when a signal appears.

Tech Stack 🛠️

Python 3.10+

yfinance — Market data

pandas_ta — Technical indicators

python-telegram-bot — Messaging & commands

Project Structure 📂
signal_bot/
├── data_manager.py   # Fetches market data
├── indicators.py     # RSI calculations
├── notifier.py       # Telegram notifications
├── main.py           # Core application loop
├── .env              # Environment variables (ignored by Git)
└── requirements.txt  # Dependencies

Installation ⚙️
1. Clone the Repository
git clone https://github.com/YOUR_USERNAME/signal_bot.git
cd signal_bot

2. Create a Virtual Environment (Recommended)

Windows

python -m venv venv
source venv/Scripts/activate


macOS / Linux

python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Environment Variables

Create a .env file in the root directory:

TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

5. Run the Bot
python main.py

Telegram Commands 🤖
Command	Description
/status	Check bot status
/check	Force a market scan
/help	Show available commands
Configuration 🔧

Modify the configuration section in main.py:

COINS_TO_WATCH = ['BTC-USD', 'ETH-USD', 'DOGE-USD']
CHECK_INTERVAL = 3600  # seconds
RSI_LOWER_LIMIT = 30
RSI_UPPER_LIMIT = 70

Disclaimer ⚠️

This project is for educational purposes only.
It does not provide financial advice. Use at your own risk.