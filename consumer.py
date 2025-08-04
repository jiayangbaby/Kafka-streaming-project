# consumer.py
from kafka import KafkaConsumer
from pymongo import MongoClient
import json
import sys
import os
import certifi

def main():
    try:
        username = os.environ['MONGO_USERNAME']
        password = os.environ['MONGO_PASSWORD']
        cluster = os.environ['MONGO_CLUSTER']
        # Setup MongoDB connection
        uri = f"mongodb+srv://{username}:{password}@{cluster}.itgvkjj.mongodb.net/?retryWrites=true&w=majority&appName={cluster}"
        mongo_client = MongoClient(uri, tlsCAFile=certifi.where())
        db = mongo_client.stock_data
        collection = db.prices
        
        # Create a capped collection 
        if 'prices' not in db.list_collection_names():
            db.create_collection(
                'prices',
                capped=True,
                size=400 * 1024 * 1024  # 400 MB
            )
            print("Created capped collection 'prices'", file=sys.stderr)

        collection = db.prices
        
        # Setup Kafka consumer
        consumer = KafkaConsumer(
            'stock_prices',
            bootstrap_servers = 'kafka1:9092,kafka2:9092,kafka3:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='stock-consumer-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=10000  # so it doesn't hang forever if topic is empty
        )

        print("Kafka consumer started. Listening to topic 'stock_prices'...", file=sys.stderr)
        
        buffer = []
        for msg in consumer:
            buffer.append(msg.value)
            if len(buffer) >= 100:  # or every 1–2 seconds
                collection.insert_many(buffer)
                buffer.clear()
                print("buffer clear")

        '''for msg in consumer:
            payload = msg.value
            c
            # Insert into MongoDB
            collection.insert_one(payload)
            print("Inserted into MongoDB", file=sys.stderr)'''

    except Exception as e:
        print("Kafka consumer error:", str(e), file=sys.stderr)

    finally:
        try:
            consumer.close()
            print("Kafka consumer closed.", file=sys.stderr)
        except:
            pass

if __name__ == '__main__':
    main()


