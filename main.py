import time
from datetime import datetime
from data_manager import get_crypto_data
from indicators import add_indicators
from notifier import send_telegram_message, get_new_commands
from keep_alive import keep_alive  # <--- Import the web server

# --- CONFIGURATION ---
COINS_TO_WATCH = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD']
CHECK_INTERVAL = 3600  # Check market every 1 hour (3600 seconds)
RSI_LOWER_LIMIT = 30   # Buy Signal
RSI_UPPER_LIMIT = 70   # Sell Signal

def run_market_scan(is_manual=False):
    """Checks all coins for trading signals"""
    timestamp = datetime.now().strftime('%H:%M')
    print(f"\n--- Market Scan at {timestamp} ---")
    
    # Initialize the report string for manual checks
    status_report = f"📊 **Manual Market Report ({timestamp})**\n"
    
    for ticker in COINS_TO_WATCH:
        # 1. Fetch Data
        df = get_crypto_data(ticker)
        if df is None:
            continue

        # 2. Analyze
        df = add_indicators(df)
        rsi = df.iloc[-1]['RSI_14']
        
        print(f"   {ticker}: RSI {rsi:.2f}")

        # 3. Build Manual Report
        icon = "🟢" if rsi < 35 else "🔴" if rsi > 65 else "⚪"
        status_report += f"{icon} {ticker}: RSI {rsi:.2f}\n"

        # 4. Notify (Automatic Alerts)
        if rsi < RSI_LOWER_LIMIT:
            send_telegram_message(f"🚨 BUY ALERT: {ticker} is cheap! (RSI: {rsi:.2f})")
        elif rsi > RSI_UPPER_LIMIT:
            send_telegram_message(f"🚨 SELL ALERT: {ticker} is expensive! (RSI: {rsi:.2f})")
            
    # 5. Send Report (Manual Mode Only)
    if is_manual:
        send_telegram_message(status_report)

def handle_user_command(command):
    """Decides what to do when you talk to the bot"""
    command = command.lower().strip()
    
    if command == "/status":
        msg = f"✅ **System Online**\n" \
              f"👀 Watching: {len(COINS_TO_WATCH)} coins\n" \
              f"⏳ Interval: {CHECK_INTERVAL}s"
        send_telegram_message(msg)
        
    elif command == "/check":
        send_telegram_message("🔄 Checking prices now...")
        run_market_scan(is_manual=True)
        
    elif command == "/help":
        send_telegram_message("Available commands:\n/status - System health\n/check - Force price check")

if __name__ == "__main__":
    print("🤖 Bot started. Waiting for commands...")
    send_telegram_message("🤖 System Online. Send /help for commands.")
    
    # --- START THE WEB SERVER (Crucial for Cloud Deployment) ---
    keep_alive()  
    # -----------------------------------------------------------

    last_check_time = 0
    last_update_id = None 

    while True:
        try:
            # --- TASK 1: Check for Telegram Commands (Every 2 seconds) ---
            updates = get_new_commands(last_update_id)
            
            for update in updates:
                last_update_id = update["update_id"] + 1 
                
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