import yfinance as yf

# Now we accept a 'ticker' argument
def get_crypto_data(ticker):
    print(f"Fetching data for {ticker}...")
    
    # We use the variable 'ticker' here
    try:
        df = yf.download(tickers=ticker, period='7d', interval='1h', progress=False)
        
        if df.empty:
            print(f"Error: No data found for {ticker}")
            return None
            
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

if __name__ == "__main__":
    # Test it with something other than Bitcoin to prove it works
    test_data = get_crypto_data('ETH-USD')
    
    if test_data is not None:
        print("Success! Downloaded Ethereum data.")
        print(test_data.tail(2))