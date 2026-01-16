# Real-Time Sentiment Dashboard

A real-time sentiment analysis pipeline that processes text data through Apache Kafka and applies machine learning-based sentiment classification. The system displays live sentiment trends and statistics in an interactive dark-neon themed dashboard.

## What This Project Does

1. **Ingests text data** from various sources (mock, news, YouTube, IMDb)
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
- **Data Sources**: 
  - `main` branch: Mock/fake data
  - `feat/newsapi-integration` branch: Real news articles
  - `feat/youtube-comments` branch: YouTube video comments

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

**Why NewsAPI?** Provides structured, reliable news content from diverse sources, ideal for analyzing sentiment trends across current events and topics.

- Fetches real articles from NewsAPI (free tier: 100 articles/day)
- Producer runs locally on your machine
- Backend services run in Docker
- Requires NewsAPI key (free signup at https://newsapi.org/)

### `feat/youtube-comments` - YouTube Comments
**Use this to analyze YouTube video comments in real-time.**

**Why YouTube?** Captures real-time, streaming behavior from users reacting to video content. Comments are spontaneous and emotion-rich, providing excellent sentiment signals for live discussions.

- Fetches comments from videos based on search queries
- Uses YouTube Data API v3
- Monitors multiple search terms (AI, tech, reviews)
- Producer runs locally on your machine
- Requires YouTube API key (free from Google Cloud Console)

**YouTube API Quotas:**
- Free tier: 10,000 units/day
- Each search = 100 units
- Each comment fetch = 1 unit
- Our setup uses ~300-400 units per 15-min cycle (safe for daily use)

---
## Demo

[Watch Sentiment Dashboard Demo](Screen%20Recording%202026-01-16%20134006.mp4)

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

### Option 2: NewsAPI Branch - Real News Data (Hybrid Setup)

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

### Option 3: YouTube Comments Branch - Real-Time User Reactions

**Captures live user sentiment from YouTube video comments.**

#### Step 1: Setup YouTube API Key

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable "YouTube Data API v3"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the API key

#### Step 2: Clone and Configure

```bash
git clone <repo>
cd sentiment_dashboard
git checkout feat/youtube-comments
```

Create `.env` file in project root:
```
YOUTUBE_API_KEY=your_youtube_api_key_here
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

#### Step 3: Start Backend Services (Docker)

```powershell
docker-compose up kafka zookeeper postgres consumer backend frontend
```

#### Step 4: Setup and Run Producer Locally

**Terminal 2:**

```powershell
cd producer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Install dependencies:**
```
kafka-python==2.0.3
google-api-python-client==2.108.0
python-dotenv==1.0.0
```

**Run producer:**
```powershell
python producer.py
```

**Expected output:**
```
INFO:__main__:YouTube producer initialized successfully
INFO:__main__:Searching videos for: AI technology
INFO:__main__:Fetching comments from: Amazing AI Breakthrough...
INFO:__main__:Sent comment: This is incredible! The future is here...
INFO:__main__:Next fetch in 15 minutes...
```

**What happens:**
- Producer searches for videos based on queries: `['AI technology', 'machine learning', 'tech review']`
- Fetches top comments from recent videos
- Sends comments to Kafka every 15 minutes
- Consumer analyzes sentiment from user reactions

**YouTube API Usage:**
- **Free tier**: 10,000 units/day
- **Each search**: 100 units
- **Each comment fetch**: 1 unit
- **Our setup**: ~300-400 units per 15-min cycle
- **Daily cost**: ~9,600 units (within free tier)

**Customize queries** in `producer.py`:
```python
self.search_queries = ['AI technology', 'machine learning', 'tech review']
```

---

## Architecture Comparison

### Main Branch (Mock Data)
```
Producer (Docker) → Kafka (Docker) → Consumer (Docker) → PostgreSQL (Docker) → API (Docker) → Frontend (Docker)
All in Docker using internal network on kafka:29092
```

### NewsAPI/YouTube/IMDb Branches (Real Data)
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
- Verify producer is sending: Check producer terminal output

**Frontend shows 0 analyzed?**
- Wait 30 seconds for consumer to process first batch
- Check backend API: `http://localhost:8000/api/sentiments/stats?hours=24`

**YouTube API quota exceeded?**
- Check usage: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
- Reduce search queries or increase fetch interval in producer

**IMDb scraping blocked?**
- Add delays between requests in producer
- Check if IMDb structure changed (may need to update scraper)

## License

MIT

