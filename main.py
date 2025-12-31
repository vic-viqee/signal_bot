import time
from datetime import datetime
from data_manager import get_crypto_data
from indicators import add_indicators
from notifier import send_telegram_message, get_new_commands

# --- SETTINGS ---
COINS_TO_WATCH = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD']
CHECK_INTERVAL = 3600  # Check market every 1 hour (3600 seconds)

def run_market_scan(is_manual=False):
    """Checks all coins for trading signals"""
    print(f"\n--- Market Scan at {datetime.now().strftime('%H:%M')} ---")
    
    # We will build a status report string just in case this is a manual check
    status_report = "📊 **Manual Market Report**\n"
    
    for ticker in COINS_TO_WATCH:
        # 1. Get Data
        df = get_crypto_data(ticker)
        if df is None: continue

        # 2. Analyze
        df = add_indicators(df)
        rsi = df.iloc[-1]['RSI_14']
        
        print(f"   {ticker}: RSI {rsi:.2f}")

        # 3. Add to Manual Report (regardless of signal)
        # We add an icon based on how 'hot' the market is
        icon = "🟢" if rsi < 35 else "🔴" if rsi > 65 else "⚪"
        status_report += f"{icon} {ticker}: RSI {rsi:.2f}\n"

        # 4. Notify (The original logic for ALERTS)
        if rsi < 30:
            send_telegram_message(f"🚨 BUY ALERT: {ticker} is cheap! (RSI: {rsi:.2f})")
        elif rsi > 70:
            send_telegram_message(f"🚨 SELL ALERT: {ticker} is expensive! (RSI: {rsi:.2f})")
            
    # If this was a manual check via /check command, send the full report
    if is_manual:
        send_telegram_message(status_report)

def handle_user_command(command):
    """Decides what to do when you talk to the bot"""
    command = command.lower().strip()
    
    if command == "/status":
        msg = f"✅ Bot is Online.\n👀 Watching: {len(COINS_TO_WATCH)} coins\n⏳ Interval: {CHECK_INTERVAL}s"
        send_telegram_message(msg)
        
    elif command == "/check":
        send_telegram_message("🔄 Checking prices now...")
        # We tell the scanner: "This is a manual check, tell me everything!"
        run_market_scan(is_manual=True)
        # We don't need to say "Check complete" because the report will arrive instead.
        
    elif command == "/help":
        send_telegram_message("Available commands:\n/status - System health\n/check - Force price check")

if __name__ == "__main__":
    print("🤖 Bot started. Waiting for commands...")
    send_telegram_message("🤖 System Online. Send /help for commands.")
    
    last_check_time = 0
    last_update_id = None # Keeps track of which messages we've seen

    while True:
        try:
            # --- TASK 1: Check for Telegram Commands (Every 2 seconds) ---
            updates = get_new_commands(last_update_id)
            
            for update in updates:
                last_update_id = update["update_id"] + 1 # Update offset so we don't read old msgs
                
                # Check if it's a text message
                if "message" in update and "text" in update["message"]:
                    text = update["message"]["text"]
                    print(f"📩 Received: {text}")
                    handle_user_command(text)

            # --- TASK 2: Check Market Prices (Every 1 Hour) ---
            current_time = time.time()
            if current_time - last_check_time > CHECK_INTERVAL:
                run_market_scan()
                last_check_time = current_time

            # Sleep briefly to save your CPU
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\nBot stopped by user.")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)