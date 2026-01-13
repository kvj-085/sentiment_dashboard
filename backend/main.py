from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import psycopg
from psycopg.rows import dict_row
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="Sentiment Dashboard API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
import os
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'sentiment_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

class SentimentResult(BaseModel):
    id: int
    text: str
    sentiment: str
    score: float
    source: str
    timestamp: datetime
    created_at: datetime

class SentimentStats(BaseModel):
    total_count: int
    positive_count: int
    negative_count: int
    positive_percentage: float
    negative_percentage: float
    average_score: float

def get_db_connection():
    """Create database connection"""
    return psycopg.connect(**DB_CONFIG, row_factory=dict_row)

@app.get("/")
def read_root():
    return {"message": "Sentiment Dashboard API", "version": "1.0.0"}

@app.get("/api/sentiments", response_model=List[SentimentResult])
def get_sentiments(limit: int = 100, offset: int = 0):
    """Get sentiment results with pagination"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM sentiment_results
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sentiments/stats", response_model=SentimentStats)
def get_sentiment_stats(hours: Optional[int] = 24):
    """Get sentiment statistics for the last N hours"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        time_filter = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_count,
                SUM(CASE WHEN sentiment = 'POSITIVE' THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN sentiment = 'NEGATIVE' THEN 1 ELSE 0 END) as negative_count,
                AVG(score) as average_score
            FROM sentiment_results
            WHERE created_at >= %s
        """, (time_filter,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        total = result['total_count'] or 0
        positive = result['positive_count'] or 0
        negative = result['negative_count'] or 0
        
        return {
            'total_count': total,
            'positive_count': positive,
            'negative_count': negative,
            'positive_percentage': (positive / total * 100) if total > 0 else 0,
            'negative_percentage': (negative / total * 100) if total > 0 else 0,
            'average_score': result['average_score'] or 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sentiments/timeline")
def get_sentiment_timeline(hours: Optional[int] = 24):
    """Get sentiment distribution over time"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        time_filter = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                sentiment,
                COUNT(*) as count
            FROM sentiment_results
            WHERE created_at >= %s
            GROUP BY hour, sentiment
            ORDER BY hour
        """, (time_filter,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sentiments/recent")
def get_recent_sentiments(limit: int = 10):
    """Get most recent sentiment analyses"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT text, sentiment, score, source, created_at
            FROM sentiment_results
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
