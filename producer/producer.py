import json
import logging
import os
import time
import praw
from kafka import KafkaProducer
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('../.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditSentimentProducer:
    def __init__(self, bootstrap_servers=None, topic='sentiment-data'):
        if bootstrap_servers is None:
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = topic
        
        # Reddit API setup (no authentication needed for read-only)
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.error("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET not set in .env")
            raise ValueError("Missing Reddit API credentials")
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent='SentimentDashboard/1.0'
        )
        
        self.subreddits = ['technology', 'artificial']
        
        logger.info("Reddit producer initialized successfully")
        
        
    def fetch_reddit_data(self):
        """Fetch posts and comments from specified subreddits"""
        for subreddit_name in self.subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Fetch top posts from last 24 hours
                for post in subreddit.top(time_filter='day', limit=10):
                    # Send post title
                    message = {
                        'text': post.title,
                        'source': f'Reddit - r/{subreddit_name}',
                        'type': 'post',
                        'url': post.url,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    self.producer.send(self.topic, value=message)
                    logger.info(f"Sent post from r/{subreddit_name}: {post.title[:50]}...")
                    
                    # Fetch and send top-level comments
                    post.comments.replace_more(limit=0)  # Load all comments without "More Comments"
                    
                    for i, comment in enumerate(post.comments):
                        if i >= 5:  # Limit to 5 top comments per post
                            break
                        
                        if comment.body and len(comment.body) > 10:  # Skip very short comments
                            message = {
                                'text': comment.body,
                                'source': f'Reddit - r/{subreddit_name} (comment)',
                                'type': 'comment',
                                'url': f"https://reddit.com{comment.permalink}",
                                'timestamp': datetime.utcnow().isoformat()
                            }
                            
                            self.producer.send(self.topic, value=message)
                            logger.info(f"Sent comment from r/{subreddit_name}: {comment.body[:50]}...")
                            
            except Exception as e:
                logger.error(f"Error fetching from r/{subreddit_name}: {e}")
    
    def scrape_and_send(self):
        """Continuously fetch and send Reddit data"""
        while True:
            logger.info("Fetching Reddit data...")
            self.fetch_reddit_data()
            
            # Wait 15 minutes before next fetch
            logger.info("Next fetch in 15 minutes...")
            time.sleep(900)
    
    def close(self):
        self.producer.close()

if __name__ == "__main__":
    producer = RedditSentimentProducer()
    try:
        producer.scrape_and_send()
    except KeyboardInterrupt:
        logger.info("Producer stopped")
        producer.close()