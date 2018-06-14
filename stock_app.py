from dotenv import load_dotenv
import csv
import json
import os
import pdb
import requests
import datetime
load_dotenv()# loads environment variables set in a ".env" file, including the value of the ALPHAVANTAGE_API_KEY variable
# see: https://www.alphavantage.co/support/#api-key

def parse_response(response_text):
    # response_text can be either a raw JSON string or an already-converted dictionary
    if isinstance(response_text, str): # if not yet converted, then:
        response_text = json.loads(response_text) # convert string to dictionary

    results = []
    time_series_daily = response_text["Time Series (Daily)"] #> a nested dictionary
    for trading_date in time_series_daily: # FYI: can loop through a dictionary's top-level keys/attributes
        #print(trading_date)
        prices = time_series_daily[trading_date] #> {'1. open': '101.0924', '2. high': '101.9500', '3. low': '100.5400', '4. close': '101.6300', '5. volume': '22165128'}
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results

def write_prices_to_file(prices=[], filename="db/prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"], # change attribute name to match project requirements
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"]
            }
            writer.writerow(row)





if __name__ == '__main__': # only execute if file invoked from the command-line, not when imported into other files, like tests

    #load_dotenv() # loads environment variables set in a ".env" file, including the value of the ALPHAVANTAGE_API_KEY variable

    api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "You might want to check the ENV file for 'ALPHAVANTAGE_API_KEY'."
    print("                                       ")
    print(api_key)

    # CAPTURE USER INPUTS (SYMBOL)

    print("                                       ")
    symbol = input("Welcome to the Stock Quotation System. Please input a stock symbol (e.g. 'AMZN'): ")

    # VALIDATE SYMBOL AND PREVENT UNECESSARY REQUESTS

    try:
        float(symbol)
        quit("CHECK YOUR SYMBOL DUDE. I WAS EXPECTING A NON-NUMERIC SYMBOL")
    except ValueError as e:
        pass

    # ASSEMBLE REQUEST URL
    # ... see: https://www.alphavantage.co/support/#api-key

    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    #request_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + symbol + "&apikey=" + api_key

    # ISSUE "GET" REQUEST
    print("                                       ")
    print("ISSUING A REQUEST")
    response = requests.get(request_url)

    # VALIDATE RESPONSE AND HANDLE ERRORS

    if "Error Message" in response.text:
        print("REQUEST ERROR, PLEASE TRY AGAIN. CHECK YOUR STOCK SYMBOL.")
        quit("Stopping the program")

    # PARSE RESPONSE (AS LONG AS THERE ARE NO ERRORS)

    daily_prices = parse_response(response.text)
    #date = str(date.today())
    # WRITE TO CSV

    #write_prices_to_file(prices=daily_prices, filename="db/prices.csv")

    # PERFORM CALCULATIONS
    # ... todo (HINT: use the daily_prices variable, and don't worry about the CSV file anymore :-)

    now = str(datetime.datetime.now()) #Give me today's date and time and print it
    # I couldn't figure out an efficient way to format the time in less than the millionth of the second, sorry :()
    print("                                       ")
    print("----------------------------------------------")
    print("This is " + symbol + "'s" + " Stock Report for today's date " + now)
    print("                                       ")

    #Give me today's high, low, close, open, and tell me if the price is up or down.
    highest_daily_price = daily_prices[0]["high"]
    highest_daily_price = float(highest_daily_price)
    highest_daily_price_usd = "${0:,.2f}".format(highest_daily_price)
    print("" + "High is: " + highest_daily_price_usd)
    print("                                     ")

    lowest_daily_price = daily_prices[0]["low"]
    lowest_daily_price = float(lowest_daily_price)
    lowest_daily_price_usd = "${0:,.2f}".format(lowest_daily_price)
    print("" + "Low is: " + lowest_daily_price_usd)
    print("                                     ")

    latest_opening_price = daily_prices[0]["open"]
    latest_opening_price = float(latest_opening_price)
    latest_opening_price_usd = "${0:,.2f}".format(latest_opening_price)
    print( "" + "Open is: " + latest_opening_price_usd)
    print("                                     ")

    latest_closing_price = daily_prices[0]["close"]
    latest_closing_price = float(latest_closing_price)
    latest_closing_price_usd = "${0:,.2f}".format(latest_closing_price)
    print( "" + "Close is: " + latest_closing_price_usd)
    print("                                     ")

    price_change = "${0:,.2f}".format(latest_closing_price-latest_opening_price)

    volume = daily_prices[0]["volume"]
    volume = float(volume)
    volume = "{0:,.2f}".format(volume)
    print("" + "Trading Volume for " + symbol + " is: " + volume + " shares")
    print("                                     ")

    print("The Price Change for " + symbol + " today is " + price_change)
    print("----------------------------------------------")
    print("                                       ")
    # PRODUCE FINAL RECOMMENDATION
    # ... todo
    high = daily_prices[0]["high"]
    low = daily_prices[0]["low"]
    open = daily_prices[0]["open"]
    close = daily_prices[0]["close"]

    if close > open:
        print("Today's close is more than 5% than the open....If you want to take profits, it's time to sell!)")
    elif close < open:
        print("Today's open is less than the close...If you're an aggressive investor, it's time to buy!")
    print("                                       ")
    quit("Please restart the application to check another stock. Happy Investing! ;) ")
