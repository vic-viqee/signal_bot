import pandas_ta as ta
from data_manager import get_crypto_data

def add_indicators(df):
    # 1. Clean the data
    if df.columns.nlevels > 1:
        df.columns = df.columns.droplevel(1)
        
    # 2. Calculate RSI
    df.ta.rsi(length=14, append=True)
    
    return df

if __name__ == "__main__":
    # Test with Solana
    print("Testing indicators on Solana...")
    data = get_crypto_data('SOL-USD')
    
    if data is not None:
        data_with_math = add_indicators(data)
        print(data_with_math.tail())