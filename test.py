from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv
load_dotenv()

username = os.getenv('MONGO_USERNAME')
password = os.getenv('MONGO_PASSWORD')
cluster = os.getenv('MONGO_CLUSTER')


uri = f"mongodb+srv://{username}:{password}@{cluster}.itgvkjj.mongodb.net/?retryWrites=true&w=majority&appName={cluster}"
#uri = "mongodb+srv://jiayangwang93:JatebMV35bJ0Bv2x@cluster0.itgvkjj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, tlsCAFile=certifi.where())

print(client.list_database_names())
