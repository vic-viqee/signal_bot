import requests
import os
from dotenv import load_dotenv

# Load secrets from the .env file
load_dotenv()

def send_telegram_message(message):
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("Error: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID is missing in .env file")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    # Test the function
    send_telegram_message("Hello from Python! Your bot is alive 🤖")
    
# ... (Keep existing code above) ...

def get_new_commands(offset=None):
    """Checks for new messages sent to the bot."""
    bot_token = os.getenv('TELEGRAM_TOKEN')
    
    # We ask Telegram: "Give me any new messages since ID 'offset'"
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {"timeout": 1} 
    if offset:
        params["offset"] = offset
        
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("ok") and len(data.get("result", [])) > 0:
            return data["result"] # Returns a list of new messages
    except Exception as e:
        print(f"Error checking commands: {e}")
        
    return []