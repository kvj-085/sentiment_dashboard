# Real-Time Sentiment Dashboard

A real-time sentiment analysis pipeline that processes text data through Apache Kafka and applies machine learning-based sentiment classification. The system displays live sentiment trends and statistics in an interactive dark-neon themed dashboard.

## What This Project Does

1. **Ingests text data** from various sources (fake or real news)
2. **Processes through Kafka** message queue for scalability
3. **Analyzes sentiment** using HuggingFace DistilBERT model
4. **Stores results** in PostgreSQL database
5. **Visualizes trends** in a real-time React dashboard

## Tech Stack

- **Message Queue**: Apache Kafka + Zookeeper
- **Backend**: FastAPI (Python)
- **Frontend**: React.js with Chart.js
- **Database**: PostgreSQL
- **ML/NLP**: HuggingFace Transformers (DistilBERT)
- **Containerization**: Docker & Docker Compose
- **Data Source**: 
  - `main` branch: Mock/fake data
  - `feat/newsapi-integration` branch: Real NewsAPI articles

## Project Structure

```
sentiment_dashboard/
├── frontend/              # React dashboard (dark neon theme)
├── backend/               # FastAPI REST API
├── producer/              # Kafka producer (data ingestion)
├── consumer/              # Kafka consumer (sentiment analysis)
├── docker-compose.yml     # Service orchestration
├── .env.example           # Environment template
└── README.md
```

## Branches

### `main` - Mock Data (Default)
**Use this to get started quickly with fake data generation.**

- Generates mock product reviews automatically
- No external API keys needed
- Perfect for testing and development
- Includes everything in Docker containers

### `feat/newsapi-integration` - Real News Data
**Use this to analyze real news articles from NewsAPI.**

- Fetches real articles from NewsAPI (free tier: 100 articles/day)
- Producer runs locally on your machine
- Backend services run in Docker
- Requires NewsAPI key (free signup at https://newsapi.org/)

---

## Setup & Usage

### Prerequisites

- **Docker & Docker Compose** installed
- **Python 3.10+** (for running producer locally)
- **Node.js 16+** (optional, for local frontend development)
- **Git**

### Option 1: Main Branch - Mock Data with Docker (Fastest)

**Clone and run everything in Docker:**

```bash
git clone <repo>
cd sentiment_dashboard
docker-compose up
```

**What happens:**
- All services (Kafka, PostgreSQL, producer, consumer, backend, frontend) start in Docker containers
- Producer generates fake product review data every 10 seconds
- Consumer analyzes sentiment and stores in database
- Dashboard updates in real-time

**Access points:**
- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000/api
- PostgreSQL: localhost:5432 (credentials in docker-compose.yml)

**Kafka Details (Docker only):**
- Internal communication: `kafka:29092` (used by consumer/producer in Docker)
- External access: `localhost:9092` (not used in main branch)

**Ports Summary:**
| Service | Port | Access |
|---------|------|--------|
| Frontend (React) | 3000 | http://localhost:3000 |
| Backend (FastAPI) | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | localhost:5432 |
| Kafka (external) | 9092 | localhost:9092 |
| Zookeeper | 2181 | localhost:2181 |

---

### Option 2: NewsAPI Branch - Real Data (Hybrid Setup)

**This approach runs backend services in Docker and producer locally on your machine.**

#### Step 1: Setup NewsAPI Key

1. Sign up for free at https://newsapi.org/
2. Copy your API key

#### Step 2: Clone and Configure

```bash
git clone <repo>
cd sentiment_dashboard
git checkout feat/newsapi-integration
```

Create `.env` file in project root:
```
NEWSAPI_KEY=your_actual_newsapi_key_here
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

#### Step 3: Start Backend Services (Docker)

```powershell
docker-compose up kafka zookeeper postgres consumer backend frontend
```

**What starts in Docker:**
- Zookeeper (port 2181)
- Kafka (ports 9092 external, 29092 internal)
- PostgreSQL (port 5432)
- Consumer (analyzes sentiment from Kafka)
- Backend API (port 8000)
- Frontend (port 3000)

**Kafka Details (Hybrid setup):**
- Internal Docker communication: `kafka:29092` (consumer, backend in Docker)
- External (your machine): `localhost:9092` (local producer)

#### Step 4: Setup and Run Producer Locally

**Terminal 2** - In a new terminal on your machine:

```powershell
cd producer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Install dependencies:**
```
kafka-python==2.0.3
requests==2.31.0
python-dotenv==1.0.0
```

**Run producer:**
```powershell
python producer.py
```

**Expected output:**
```
INFO:__main__:Sent message: Great product quality...
INFO:__main__:Sent message: Excellent service desk for ITIL organizations...
```

**What happens:**
- Producer fetches articles from NewsAPI every 5 minutes
- Sends to Kafka on `localhost:9092`
- Consumer (in Docker) receives from `kafka:29092` and analyzes sentiment
- Results displayed on dashboard

#### Access points (Hybrid setup):

| Service | Port | Where | Access |
|---------|------|-------|--------|
| Frontend | 3000 | Docker | http://localhost:3000 |
| Backend API | 8000 | Docker | http://localhost:8000/api |
| PostgreSQL | 5432 | Docker | localhost:5432 |
| Kafka Producer | 9092 | Your Machine | localhost:9092 |
| Kafka Consumer | 29092 | Docker Internal | kafka:29092 |

**NewsAPI Limitations:**
- Free tier: 100 requests/day
- Producer fetches every 5 minutes
- Articles limited based on query availability
- Consider upgrading for higher limits

---

## Architecture Comparison

### Main Branch (Mock Data)
```
Producer (Docker) → Kafka (Docker) → Consumer (Docker) → PostgreSQL (Docker) → API (Docker) → Frontend (Docker)
All in Docker using internal network on kafka:29092
```

### NewsAPI Branch (Real Data)
```
Producer (Local Machine) ──→ Kafka (Docker) ←── Consumer (Docker) → PostgreSQL (Docker) → API (Docker) → Frontend (Docker)
                    localhost:9092        kafka:29092
```

---

## Common Commands

```bash
# Start all services
docker-compose up

# Stop all services
docker-compose down

# View logs
docker-compose logs -f consumer
docker-compose logs -f backend

# Rebuild images
docker-compose build

# Remove volumes (clears database)
docker-compose down -v
```

## Troubleshooting

**Producer can't connect to Kafka?**
- Check `.env` has `KAFKA_BOOTSTRAP_SERVERS=localhost:9092`
- Ensure Kafka container is running: `docker-compose ps`

**Consumer not analyzing messages?**
- Check consumer logs: `docker-compose logs consumer`
- Verify producer is sending: `docker-compose logs producer`

**Frontend shows 0 analyzed?**
- Wait 30 seconds for consumer to process first batch
- Check backend API: `http://localhost:8000/api/sentiments/stats?hours=24`

## License

MIT