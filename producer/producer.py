import json
import logging
import os
import time
import requests
from kafka import KafkaProducer
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('../.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentProducer:
    def __init__(self, bootstrap_servers=None, topic='sentiment-data'):
        if bootstrap_servers is None:
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = topic
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.newsapi_url = 'https://newsapi.org/v2/everything'
        
    def fetch_news(self):
        """Fetch articles from NewsAPI"""
        params = {
            'q': 'product review',  # Search query
            'sortBy': 'publishedAt',
            'language': 'en',
            'apiKey': self.newsapi_key,
            'pageSize': 10
        }
        
        try:
            response = requests.get(self.newsapi_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                return data.get('articles', [])
            else:
                logger.error(f"NewsAPI error: {data.get('message')}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch news: {e}")
            return []
    
    def scrape_and_send(self):
        """Continuously fetch and send news articles"""
        while True:
            articles = self.fetch_news()
            
            for article in articles:
                message = {
                    'text': article.get('description') or article.get('title'),
                    'source': article.get('source', {}).get('name', 'News'),
                    'url': article.get('url'),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                self.producer.send(self.topic, value=message)
                logger.info(f"Sent message: {message['text'][:50]}...")
            
            # Wait before fetching again (avoid rate limits)
            time.sleep(300)  # 5 minutes
    
    def close(self):
        self.producer.close()

if __name__ == "__main__":
    producer = SentimentProducer()
    try:
        producer.scrape_and_send()
    except KeyboardInterrupt:
        logger.info("Producer stopped")
        producer.close()