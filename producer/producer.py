import json
import logging
import os
import time
from kafka import KafkaProducer
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv('../.env')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class YouTubeSentimentProducer:
    def __init__(self, bootstrap_servers=None, topic='sentiment-data'):
        if bootstrap_servers is None:
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = topic
        
        api_key = os.getenv('YOUTUBE_API_KEY')
        
        if not api_key:
            logger.error("YOUTUBE_API_KEY not set in .env")
            raise ValueError("Missing YouTube API key")
        
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.search_queries = ['AI technology', 'machine learning', 'tech review']
        self.processed_comments = set()
        
        logger.info("YouTube producer initialized successfully")
        
    def fetch_video_comments(self, video_id, max_comments=50):
        """Fetch comments from a specific video"""
        try:
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_comments,
                order='relevance',
                textFormat='plainText'
            )
            
            response = request.execute()
            comments = []
            
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comment_id = item['id']
                
                if comment_id in self.processed_comments:
                    continue
                    
                self.processed_comments.add(comment_id)
                
                comments.append({
                    'text': comment['textDisplay'],
                    'author': comment['authorDisplayName'],
                    'likes': comment['likeCount'],
                    'published': comment['publishedAt']
                })
            
            return comments
            
        except Exception as e:
            logger.error(f"Error fetching comments for video {video_id}: {e}")
            return []
    
    def search_videos(self, query, max_results=5):
        """Search for videos by query"""
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=max_results,
                order='relevance',
                relevanceLanguage='en',
                videoDuration='medium'
            )
            
            response = request.execute()
            video_ids = []
            
            for item in response.get('items', []):
                video_ids.append({
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'channel': item['snippet']['channelTitle']
                })
            
            return video_ids
            
        except Exception as e:
            logger.error(f"Error searching videos for '{query}': {e}")
            return []
    
    def fetch_and_send(self):
        """Fetch comments and send to Kafka"""
        for query in self.search_queries:
            logger.info(f"Searching videos for: {query}")
            videos = self.search_videos(query, max_results=5)
            
            for video in videos:
                logger.info(f"Fetching comments from: {video['title'][:50]}...")
                comments = self.fetch_video_comments(video['id'], max_comments=30)
                
                logger.info(f"Found {len(comments)} comments for this video")
                
                for comment in comments:
                    message = {
                        'text': comment['text'],
                        'source': f"YouTube - {video['channel']}",
                        'video_title': video['title'],
                        'url': f"https://youtube.com/watch?v={video['id']}",
                        'likes': comment['likes'],
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    self.producer.send(self.topic, value=message)
                    logger.info(f"Sent comment: {comment['text'][:50]}...")
                
                time.sleep(1)
    
    def scrape_and_send(self):
        """Continuously fetch and send YouTube comments"""
        while True:
            logger.info("Starting YouTube data fetch...")
            self.fetch_and_send()
            
            next_fetch = datetime.now() + timedelta(minutes=15)
            logger.info(f"Next fetch at {next_fetch.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(900)
    
    def close(self):
        self.producer.close()

if __name__ == "__main__":
    producer = YouTubeSentimentProducer()
    try:
        producer.scrape_and_send()
    except KeyboardInterrupt:
        logger.info("Producer stopped")
        producer.close()