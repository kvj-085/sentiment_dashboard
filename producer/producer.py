import json
import time
import random
import os
from kafka import KafkaProducer
from datetime import datetime
import logging

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
        
    def scrape_and_send(self):
        """
        Simulates scraping tweets/news headlines and sends them to Kafka.
        In production, replace with actual Twitter API or news scraping.
        """
        # Sample data for demonstration
        sample_texts = [
            "I love this product! It's amazing and works perfectly.",
            "Terrible experience. Very disappointed with the service.",
            "Not bad, could be better but acceptable overall.",
            "This is the worst thing I've ever purchased.",
            "Absolutely fantastic! Exceeded all my expectations!",
            "Meh, it's okay. Nothing special about it.",
            "Outstanding quality and great customer support!",
            "I hate it. Complete waste of money.",
            "Pretty good, I'm satisfied with my purchase.",
            "Horrible quality. Do not recommend at all."
        ]
        
        while True:
            try:
                # Simulate scraping
                text = random.choice(sample_texts)
                
                # Create message
                message = {
                    'text': text,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'twitter'  # or 'news'
                }
                
                # Send to Kafka
                self.producer.send(self.topic, value=message)
                logger.info(f"Sent message: {text[:50]}...")
                
                # Wait before next message (simulate real-time scraping)
                time.sleep(random.randint(2, 5))
                
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                time.sleep(5)
    
    def close(self):
        self.producer.close()

if __name__ == "__main__":
    producer = SentimentProducer()
    try:
        producer.scrape_and_send()
    except KeyboardInterrupt:
        logger.info("Shutting down producer...")
        producer.close()
