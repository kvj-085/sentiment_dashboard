# Real-Time Sentiment Dashboard

A real-time sentiment analysis dashboard that uses Apache Kafka for data streaming, HuggingFace Transformers for sentiment analysis, FastAPI for the backend, and React for the frontend.

## 🏗️ Architecture

- **Kafka Producer**: Scrapes tweets/news headlines and streams them to a Kafka topic
- **Kafka Consumer**: Consumes messages, performs sentiment analysis using HuggingFace, and stores results in PostgreSQL
- **FastAPI Backend**: Provides REST API endpoints for fetching sentiment data
- **React Frontend**: Displays real-time sentiment trends with interactive charts
- **PostgreSQL Database**: Stores sentiment analysis results

## 🚀 Tech Stack

- **Data Streaming**: Apache Kafka
- **Backend**: FastAPI (Python)
- **ML Model**: HuggingFace Transformers (DistilBERT)
- **Database**: PostgreSQL
- **Frontend**: React + Chart.js
- **Deployment**: Docker & Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- Node.js 18+ (for local development)

## 🛠️ Quick Start with Docker

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd sentiment_dashboard
   ```

2. **Start all services with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the applications**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 💻 Local Development Setup

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment and install dependencies**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Run the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```

### Producer Setup

1. **Navigate to producer directory**:
   ```bash
   cd producer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the producer**:
   ```bash
   python producer.py
   ```

### Consumer Setup

1. **Navigate to consumer directory**:
   ```bash
   cd consumer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the consumer**:
   ```bash
   python consumer.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

## 📊 API Endpoints

- `GET /` - Health check
- `GET /api/sentiments` - Get sentiment results with pagination
- `GET /api/sentiments/stats` - Get sentiment statistics
- `GET /api/sentiments/timeline` - Get sentiment distribution over time
- `GET /api/sentiments/recent` - Get most recent sentiment analyses

## 🔧 Configuration

### Database Configuration

Edit database credentials in:
- `docker-compose.yml` for Docker setup
- `backend/main.py` for local development
- `consumer/consumer.py` for local development

### Kafka Configuration

Kafka broker address can be configured in:
- `producer/producer.py`
- `consumer/consumer.py`
- `docker-compose.yml`

## 📝 Data Flow

1. **Producer** scrapes/generates text data and sends it to Kafka topic `sentiment-data`
2. **Kafka** streams the messages to consumers
3. **Consumer** receives messages, analyzes sentiment using HuggingFace model, and stores results in PostgreSQL
4. **Backend** provides API endpoints to fetch data from PostgreSQL
5. **Frontend** displays real-time sentiment trends with charts and tables

## 🎯 Features

- ✅ Real-time data streaming with Kafka
- ✅ Sentiment analysis using state-of-the-art ML models
- ✅ RESTful API with FastAPI
- ✅ Interactive dashboard with Chart.js
- ✅ PostgreSQL for persistent storage
- ✅ Dockerized deployment
- ✅ Real-time statistics and trends

## 🚀 Suggested Enhancements

- [ ] Real-time refresh with WebSockets
- [ ] Location-based sentiment mapping
- [ ] Exporting data to CSV/PDF
- [ ] User authentication
- [ ] Twitter API integration
- [ ] News API integration
- [ ] Advanced filtering and search
- [ ] Historical data analysis
- [ ] Email alerts for sentiment thresholds

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Kafka Connection Issues
- Ensure Kafka and Zookeeper are running
- Check `KAFKA_ADVERTISED_LISTENERS` in docker-compose.yml

### Database Connection Issues
- Verify PostgreSQL is running
- Check database credentials
- Ensure the database `sentiment_db` exists

### Frontend Not Loading Data
- Verify backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Ensure API_URL is correct in frontend

## 📞 Support

For issues and questions, please open an issue in the repository.
