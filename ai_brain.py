import os
import feedparser
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def get_latest_news():
    """Fetches news headlines."""
    feed = feedparser.parse("https://cointelegraph.com/rss")
    return [entry.title for entry in feed.entries[:3]]

def get_market_mood(headline):
    """Returns POSITIVE, NEGATIVE, or NEUTRAL."""
    try:
        completion = client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            messages=[
                {"role": "system", "content": "Analyze crypto news. Reply ONLY: POSITIVE, NEGATIVE, or NEUTRAL."},
                {"role": "user", "content": headline}
            ]
        )
        return completion.choices[0].message.content.strip().upper()
    except:
        return "NEUTRAL"

def generate_market_reason():
    """One short sentence reason."""
    headlines = get_latest_news()
    try:
        completion = client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            messages=[
                {"role": "system", "content": "Summarize why the market is moving in ONE short sentence. Be casual."},
                {"role": "user", "content": str(headlines)}
            ]
        )
        return completion.choices[0].message.content.strip()
    except:
        return "Market is showing typical volatility."

def check_news_safety():
    """True if no NEGATIVE news found."""
    headlines = get_latest_news()
    for head in headlines:
        if get_market_mood(head) == "NEGATIVE":
            return False
    return True

def get_sentiment_score():
    """Returns 0.0 to 1.0 based on news."""
    headlines = get_latest_news()
    if not headlines: return 0.5
    total = 0
    for h in headlines:
        mood = get_market_mood(h)
        if mood == "POSITIVE": total += 1.0
        elif mood == "NEUTRAL": total += 0.5
    return total / len(headlines)

def generate_morning_briefing():
    """3 Simple bullet points for 8 AM."""
    headlines = get_latest_news()
    try:
        completion = client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            messages=[
                {"role": "system", "content": "Provide 3 short bullet points of crypto news. No bolding. Use '-'."},
                {"role": "user", "content": str(headlines)}
            ]
        )
        return completion.choices[0].message.content.strip()
    except:
        return "Check your charts, headlines are stuck."

def ask_crypto_mentor(question):
    """Sarcastic mentor response."""
    try:
        completion = client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            messages=[
                {"role": "system", "content": "You are 'Matatu Pilot', a sarcastic crypto pro. Max 2 sentences."},
                {"role": "user", "content": question}
            ]
        )
        return completion.choices[0].message.content.strip()
    except:
        return "The engine is stalling. Ask me later."