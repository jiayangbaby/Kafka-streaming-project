# producer.py
import time
import requests
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import os
import sys
#In to the script, debug 1
print("Starting producer...", file=sys.stderr)


API_KEY = os.getenv("API_KEY")
#API Error handling
if not API_KEY:
    print("❌ API_KEY is missing!", file=sys.stderr)
    exit(1)

# 5 targeted ETF APIs
ETF_STOCKS = ["SPY", "IBIT", "QQQ", "XLF", "VOO"]
BASE_URL = 'https://finnhub.io/api/v1/quote?symbol={}&token=' + API_KEY

#Waiting time handling, retry set up
while True:
    try:
        producer = KafkaProducer(
            bootstrap_servers='kafka1:9092,kafka2:9092,kafka3:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        break  # success
    except NoBrokersAvailable:
        print("Kafka not ready, retrying in 3s...")
        time.sleep(3)


while True:
    for symbol in ETF_STOCKS:
        try:
            response = requests.get(BASE_URL.format(symbol))
            print(f"HTTP status for {symbol}:", response.status_code, file=sys.stderr)
            data = response.json()
            print(f"Response data for {symbol}:", data, file=sys.stderr)
            
            # Data validation
            current_price = data.get('c')
            if not current_price or current_price == 0:
                print(f"⚠️ No valid price for {symbol} (value: {current_price}) — skipping...", file=sys.stderr)
                continue

            payload = {
                'symbol': symbol,
                'price': data['c'],
                'timestamp': time.time()
            }
            print("Pushing to Kafka:", payload, file=sys.stderr)
            producer.send('stock_prices', value=payload)
        
        except Exception as e:
            print(f"Error fetching {symbol}:", str(e), file=sys.stderr)
        # 60 request per min limit, set the streaming frequency to 5 sec
        time.sleep(5)
