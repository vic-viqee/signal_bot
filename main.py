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
    timestamp = datetime.now().strftime('%H:%M')
    sentiment_val = get_sentiment_score()
    
    if is_manual:
        # Simple status report for /check
        mood = "🔥" if sentiment_val > 0.6 else "❄️" if sentiment_val < 0.4 else "😐"
        send_telegram_message(f"📊 {mood} Market Mood: {int(sentiment_val*100)}%")

    for ticker in COINS_TO_WATCH:
        df = get_crypto_data(ticker)
        if df is None: continue
        df = add_indicators(df)
        rsi = df.iloc[-1]['RSI_14']

        # --- THE CLEAN SIGNAL LOGIC ---
        if rsi < RSI_LOWER_LIMIT:
            if check_news_safety():
                reason = generate_market_reason()
                confidence = ((1 - (rsi/100)) * sentiment_val) * 100
                # ONE SIMPLE RESPONSE
                send_telegram_message(f"🚨 BUY {ticker} @ RSI {rsi:.1f}\n💎 Confidence: {int(confidence)}%\n🤔 {reason}")
            else:
                print(f"Skipped {ticker} due to bad news.")

        elif rsi > RSI_UPPER_LIMIT:
            reason = generate_market_reason()
            send_telegram_message(f"🚨 SELL {ticker} @ RSI {rsi:.1f}\n🤔 {reason}")

def handle_user_command(command):
    cmd = command.strip().lower()
    if cmd == "/status":
        send_telegram_message("✅ Bot is active.")
    elif cmd == "/check":
        run_market_scan(is_manual=True)
    elif cmd == "/sentiment":
        score = get_sentiment_score()
        send_telegram_message(f"📈 Market Vibe: {int(score*100)}%\n{generate_market_reason()}")
    elif cmd.startswith("/ask"):
        question = cmd[5:]
        if question:
            send_telegram_message(f"🤖 {ask_crypto_mentor(question)}")
    elif cmd == "/help":
        send_telegram_message("/check, /sentiment, /ask")

if __name__ == "__main__":
    keep_alive()
    last_check_time = 0
    last_update_id = None 
    sent_morning_briefing = False 

    while True:
        try:
            updates = get_new_commands(last_update_id)
            for update in updates:
                last_update_id = update["update_id"] + 1 
                if "message" in update and "text" in update["message"]:
                    handle_user_command(update["message"]["text"])

            now = datetime.now()
            # 8 AM Morning Briefing
            if now.hour == 4 and not sent_morning_briefing:
                send_telegram_message(f"🌅 Morning Briefing:\n{generate_morning_briefing()}")
                sent_morning_briefing = True
            elif now.hour != 4:
                sent_morning_briefing = False

            if time.time() - last_check_time > CHECK_INTERVAL:
                run_market_scan()
                last_check_time = time.time()

            time.sleep(2)
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(5)