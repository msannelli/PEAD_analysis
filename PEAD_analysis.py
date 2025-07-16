import yfinance as yf
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt

# Download stock price data between two dates, with adjusted prices
def get_stock_data(ticker, start_date, end_date):
    stock = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)  # avoids future warning
    return stock[['Open', 'Close']]

# Define earnings events (ticker, date of earnings release, and EPS surprise)
earnings_events = [
    {'ticker': 'AAPL', 'date': '2024-01-25', 'surprise': 0.15},
    {'ticker': 'MSFT', 'date': '2024-01-30', 'surprise': 0.12},
    {'ticker': 'GOOGL', 'date': '2024-02-01', 'surprise': 0.17}
]

# Simulate PEAD strategy: Buy after strong earnings surprise and hold for a number of days
def simulate_pead(earnings_events, hold_days=10):
    results = []

    for event in earnings_events:
        ticker = event['ticker']
        event_date = pd.to_datetime(event['date'])
        surprise = event['surprise']

        # Only analyze if earnings surprise is significant (e.g. > 10%)
        if surprise < 0.1:
            continue

        # Define start and end of holding period (buffer extra days for weekends/holidays)
        start_date = event_date + timedelta(days=1)
        end_date = start_date + timedelta(days=hold_days * 2)

        # Download price data
        stock_data = get_stock_data(ticker, start_date, end_date)

        # Skip if insufficient data
        if stock_data.empty or len(stock_data) < hold_days:
            continue

        # Use position-based indexing to safely extract values
        entry_price = stock_data['Open'].iloc[0].item()
        exit_price = stock_data['Close'].iloc[hold_days - 1].item()
        return_pct = round((exit_price - entry_price) / entry_price * 100, 2)

        # Get entry and exit dates as strings
        entry_date_str = stock_data.index[0].strftime('%Y-%m-%d')
        exit_date_str = stock_data.index[hold_days - 1].strftime('%Y-%m-%d')

        # Store the results
        results.append({
            'Ticker': ticker,
            'Entry Date': entry_date_str,
            'Exit Date': exit_date_str,
            'Entry Price': round(entry_price, 2),
            'Exit Price': round(exit_price, 2),
            'Return %': return_pct
        })

    return pd.DataFrame(results)

# Run the simulation and print the results
pead_results = simulate_pead(earnings_events)
print(pead_results)
