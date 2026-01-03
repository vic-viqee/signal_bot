import time
from datetime import datetime
from data_manager import get_crypto_data
from indicators import add_indicators
from notifier import send_telegram_message, get_new_commands
from keep_alive import keep_alive
from ai_brain import (
    check_news_safety, generate_market_reason, 
    generate_morning_briefing, ask_crypto_mentor, get_sentiment_score
)

COINS_TO_WATCH = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD']
CHECK_INTERVAL = 3600 
RSI_LOWER_LIMIT = 30  
RSI_UPPER_LIMIT = 70  

def run_market_scan(is_manual=False):
    """Checks all coins with safety guards to prevent crashing."""
    timestamp = datetime.now().strftime('%H:%M')
    print(f"\n--- Market Scan at {timestamp} ---")
    
    # Try AI Sentiment, but fallback to Neutral if blocked
    try:
        sentiment_val = get_sentiment_score()
    except Exception as e:
        print(f"AI Blocked: {e}")
        sentiment_val = 0.5 
        
    mood_emoji = "🔥 Bullish" if sentiment_val > 0.6 else "❄️ Bearish" if sentiment_val < 0.4 else "😐 Neutral"
    status_report = f"📊 **Market Report ({timestamp})**\nVibe: {mood_emoji} ({int(sentiment_val*100)}%)\n\n"
    
    for ticker in COINS_TO_WATCH:
        try:
            df = get_crypto_data(ticker)
            
            if df is None or df.empty:
                status_report += f"⚠️ {ticker}: Data Unavailable (Rate Limited)\n"
                continue

            df = add_indicators(df)
            
            if 'RSI_14' not in df.columns:
                status_report += f"⚠️ {ticker}: RSI Failed\n"
                continue
                
            rsi = df.iloc[-1]['RSI_14']
            icon = "🟢" if rsi < 35 else "🔴" if rsi > 65 else "⚪"
            status_report += f"{icon} {ticker}: RSI {rsi:.2f}\n"

            # Automatic Alerts
            if rsi < RSI_LOWER_LIMIT:
                if check_news_safety():
                    reason = generate_market_reason()
                    confidence = ((1 - (rsi/100)) * sentiment_val) * 100
                    send_telegram_message(f"🚨 **BUY {ticker} @ RSI {rsi:.1f}**\n💎 Confidence: {int(confidence)}%\n🤔 {reason}")
            elif rsi > RSI_UPPER_LIMIT:
                reason = generate_market_reason()
                send_telegram_message(f"🚨 **SELL {ticker} @ RSI {rsi:.1f}**\n🤔 {reason}")
        
        except Exception as e:
            print(f"Error scanning {ticker}: {e}")
            status_report += f"⚠️ {ticker}: Error\n"

    if is_manual:
        send_telegram_message(status_report)

def handle_user_command(command):
    cmd = command.strip().lower()
    # Log incoming command to Render logs
    print(f"Telegram Command: {cmd}")
    
    if cmd == "/status":
        send_telegram_message("✅ Bot is online. Use /check for market data.")
    elif cmd == "/check":
        run_market_scan(is_manual=True)
    elif cmd == "/sentiment":
        try:
            score = get_sentiment_score()
            send_telegram_message(f"📈 Market Vibe: {int(score*100)}%\n{generate_market_reason()}")
        except:
            send_telegram_message("😐 AI Vibe is currently unavailable (Rate Limited).")
    elif cmd.startswith("/ask"):
        question = command[5:].strip()
        if question:
            send_telegram_message("🤔 Thinking...")
            send_telegram_message(f"🤖 **Mentor:** {ask_crypto_mentor(question)}")
    elif cmd == "/help":
        send_telegram_message("/status, /check, /sentiment, /ask")

if __name__ == "__main__":
    keep_alive()
    last_check_time = 0
    last_update_id = None 
    sent_morning_briefing = False 

    while True:
        try:
            # Task 1: Check Commands (Updates offset immediately)
            updates = get_new_commands(last_update_id)
            for update in updates:
                last_update_id = update["update_id"] + 1 
                if "message" in update and "text" in update["message"]:
                    handle_user_command(update["message"]["text"])

            # Task 2: Morning Briefing
            now = datetime.now()
            if now.hour == 8 and not sent_morning_briefing:
                send_telegram_message(f"🌅 Morning Briefing:\n{generate_morning_briefing()}")
                sent_morning_briefing = True
            elif now.hour != 8:
                sent_morning_briefing = False

            # Task 3: Scheduled Scan
            if time.time() - last_check_time > CHECK_INTERVAL:
                run_market_scan()
                last_check_time = time.time()

            time.sleep(2)
        except Exception as e:
            print(f"Main Loop Error: {e}")
            time.sleep(5)