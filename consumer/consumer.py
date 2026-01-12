import json
from kafka import KafkaConsumer
from transformers import pipeline
import psycopg
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentConsumer:
    def __init__(self, 
                 bootstrap_servers='localhost:9092',
                 topic='sentiment-data',
                 db_config=None):
        
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='sentiment-consumer-group'
        )
        
        # Initialize HuggingFace sentiment analysis model
        logger.info("Loading sentiment analysis model...")
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        logger.info("Model loaded successfully!")
        
        # Database configuration
        self.db_config = db_config or {
            'host': 'localhost',
            'database': 'sentiment_db',
            'user': 'postgres',
            'password': 'postgres'
        }
        
        self.init_database()
    
    def init_database(self):
        """Initialize database table if it doesn't exist"""
        try:
            conn = psycopg.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sentiment_results (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL,
                    sentiment VARCHAR(20) NOT NULL,
                    score FLOAT NOT NULL,
                    source VARCHAR(50),
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Database initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def analyze_and_store(self, message):
        """Analyze sentiment and store in PostgreSQL"""
        try:
            text = message['text']
            
            # Perform sentiment analysis
            result = self.sentiment_analyzer(text)[0]
            sentiment = result['label']
            score = result['score']
            
            # Store in database
            conn = psycopg.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sentiment_results (text, sentiment, score, source, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                text,
                sentiment,
                score,
                message.get('source', 'unknown'),
                datetime.fromisoformat(message['timestamp'])
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Analyzed and stored: {sentiment} ({score:.2f}) - {text[:50]}...")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def consume(self):
        """Consume messages from Kafka"""
        logger.info("Starting to consume messages...")
        
        for message in self.consumer:
            self.analyze_and_store(message.value)
    
    def close(self):
        self.consumer.close()

if __name__ == "__main__":
    consumer = SentimentConsumer()
    try:
        consumer.consume()
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
        consumer.close()
