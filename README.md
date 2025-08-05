## Real-Time Stock Streaming Pipeline with Kafka, MongoDB, and Docker
A scalable real-time data pipeline that streams and stores stock prices (e.g. `SPY`, `F`) using **Apache Kafka**, **MongoDB**, and **Docker**. This project demonstrates distributed architecture and fault tolerance using a multi-broker Kafka cluster.

### Set Up Overview
- **Kafka Producer** fetches data from the [Finnhub API](https://finnhub.io/)
- **Kafka Consumer** processes and stores messages in MongoDB Atlas
- **MongoDB** stores time-stamped prices for downstream analytics
- **Kafka Cluster** runs 3 brokers (designed for fault tolerance)
- **Docker Compose** orchestrates the full stack

### Architecture Diagram
```
      Finnhub API
           │
     ┌─────▼─────┐
     │ producer  │
     └─────┬─────┘
           │
     ┌─────▼─────┐
     │  Kafka    │  ◄─────── Zookeeper (leader election)
     └─────┬─────┘
           │
    ┌──────▼────────────┐
    │Topic: stock_prices│
    └──────┬────────────┘
           │
    ┌──────▼────────┐
    │ Broker 1      │ ◄── Leader
    │ Broker 2      │ ◄── Follower
    │ Broker 3      │ ◄── Follower
    └──────┬────────┘
           │
     ┌─────▼─────┐
     │ consumer  │
     └─────┬─────┘
           │
     ┌─────▼────────────┐
     │  MongoDB Atlas   │
     └──────────────────┘
```

---
### Fault Tolerance (redundancy and recovery)

#### Kafka:
- 3 brokers (`kafka1`, `kafka2`, `kafka3`)
- Topics created with `--replication-factor=3`
- Leader election via Zookeeper ensures availability
- Broker restarts automatically via Docker restart policies

#### Producer/Consumer:
- Automatically restart on failure (`restart: always`)
- Retry logic for MongoDB and API calls (planned)

#### MongoDB:
- Hosted on MongoDB Atlas with built-in backup and failover

#### Demo Note:
> For live demos on limited EC2 (e.g., `t2.micro`), only `kafka1` is run due to RAM constraints.  
> The 3-broker setup is retained in code to showcase system design and fault tolerance.

---

### Folder Structure
```bash
kafka-stock-stream/
├── producer.py            # Sends stock prices to Kafka
├── consumer.py            # Consumes and saves to MongoDB
├── docker-compose.yml     # Full cluster + services
├── Dockerfile             # Python app base
├── requirements.txt       # Python deps
├── .env                   # API keys and secrets
└── README.md              # Project Summary
```
---

### How to Run
#### 1: Start Docker services (Kafka + Zookeeper + MongoDB)
```bash
docker-compose up --build
```
#### 2: Create topic 
```bash
docker exec -it kafka1 kafka-topics --create \
  --topic stock_prices \
  --partitions 5 \
  --replication-factor 1 \
  --bootstrap-server kafka1:9092
```
> `replication-factor=1` used here for EC2 demo. Use 3 for production.
#### 3: Start the producer
```bash
docker exec -it producer python producer.py
```
#### 4: Start the consumer
```bash
docker exec -it consumer python consumer.py
```
---
### MongoDB Entry Sample

```json
{
  "symbol": "SPY",
  "price": 627.83,
  "timestamp": 1754260662,
  "created_at": "2025-08-03T22:32:26.438Z",
  "created_at_cst": "2025-08-03T17:32:26.438-05:00"
}
```


