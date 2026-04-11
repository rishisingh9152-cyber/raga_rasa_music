"""Comprehensive seed script for RagaRasa database with all collections and relationships"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from uuid import uuid4
import random

from app.config import settings
from app.services.song_scanner import SongScanner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveSeeder:
    """Comprehensive seeder for all RagaRasa collections"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.scanner = SongScanner()
        
    async def connect(self):
        """Connect to MongoDB"""
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
        await self.client.admin.command('ping')
        logger.info("MongoDB connection successful")
        
    async def clear_collections(self):
        """Clear all existing collections"""
        logger.info("Clearing existing collections...")
        collections = await self.db.list_collection_names()
        for collection in collections:
            await self.db[collection].delete_many({})
            logger.info(f"  Cleared collection: {collection}")
            
    async def seed_songs(self):
        """Upload all 68 songs with complete metadata"""
        logger.info("=" * 60)
        logger.info("SEEDING SONGS")
        logger.info("=" * 60)
        
        all_songs = self.scanner.get_all_songs()
        
        if not all_songs:
            logger.warning("No songs found on disk!")
            return []
        
        logger.info(f"Scanning {len(all_songs)} songs from disk...")
        
        # Breakdown by rasa
        rasa_counts = {}
        for song in all_songs:
            rasa = song.get('rasa', 'Unknown')
            rasa_counts[rasa] = rasa_counts.get(rasa, 0) + 1
        
        logger.info("Songs by Rasa:")
        for rasa, count in sorted(rasa_counts.items()):
            logger.info(f"  {rasa}: {count} songs")
        
        # Enhance song data with audio features based on rasa
        rasa_features = {
            "Shringar": {"energy": 0.7, "valence": 0.8, "tempo": 120},
            "Shaant": {"energy": 0.3, "valence": 0.6, "tempo": 80},
            "Veer": {"energy": 0.85, "valence": 0.7, "tempo": 140},
            "Shok": {"energy": 0.4, "valence": 0.3, "tempo": 90}
        }
        
        songs_to_insert = []
        for song in all_songs:
            rasa = song.get('rasa', 'Shaant')
            features = rasa_features.get(rasa, {"energy": 0.5, "valence": 0.5, "tempo": 100})
            
            song_doc = {
                "_id": song['_id'],
                "title": song['title'],
                "artist": song.get('artist', 'Unknown Artist'),
                "rasa": rasa,
                "audio_url": song['audio_url'],
                "file_path": song['file_path'],
                "duration": song['duration'],
                "file_size": song['file_size'],
                "file_size_mb": song['file_size_mb'],
                "audio_features": {
                    "energy": features["energy"],
                    "valence": features["valence"],
                    "tempo": features["tempo"],
                    "bitrate": "192 kbps"
                },
                "play_count": random.randint(0, 50),
                "average_rating": random.uniform(3.5, 5.0),
                "rating_count": random.randint(0, 30),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            songs_to_insert.append(song_doc)
        
        # Insert all songs
        result = await self.db.songs.insert_many(songs_to_insert)
        logger.info(f"✓ Inserted {len(result.inserted_ids)} songs")
        
        return all_songs
    
    async def seed_users(self, count=5):
        """Create sample users"""
        logger.info("=" * 60)
        logger.info("SEEDING USERS")
        logger.info("=" * 60)
        
        users = []
        user_ids = []
        
        for i in range(count):
            user_id = f"user_{uuid4().hex[:8]}"
            user_doc = {
                "_id": user_id,
                "user_id": user_id,
                "email": f"user{i+1}@ragarasa.com",
                "name": f"User {i+1}",
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                "preferences": {
                    "favorite_ragas": random.sample(["Shringar", "Shaant", "Veer", "Shok"], 2),
                    "preferred_time_of_day": random.choice(["morning", "afternoon", "evening"]),
                    "listening_frequency": random.choice(["daily", "weekly", "sometimes"])
                },
                "total_sessions": 0,
                "total_time_minutes": 0
            }
            users.append(user_doc)
            user_ids.append(user_id)
        
        if users:
            result = await self.db.users.insert_many(users)
            logger.info(f"✓ Created {len(result.inserted_ids)} users")
        
        return user_ids
    
    async def seed_sessions(self, user_ids, songs):
        """Create sample sessions with all related data"""
        logger.info("=" * 60)
        logger.info("SEEDING SESSIONS WITH EMOTIONS, RECOMMENDATIONS, RATINGS")
        logger.info("=" * 60)
        
        rasas = ["Shringar", "Shaant", "Veer", "Shok"]
        emotions = ["happy", "calm", "energetic", "sad", "neutral"]
        
        sessions_to_insert = []
        ratings_to_insert = []
        images_to_insert = []
        psychometric_to_insert = []
        
        session_count = random.randint(3, 8)
        
        for user_id in user_ids:
            for session_idx in range(session_count):
                session_id = f"session_{uuid4().hex[:12]}"
                
                # Randomly select emotion and corresponding rasa
                emotion = random.choice(emotions)
                emotion_rasa_map = {
                    "happy": "Shringar",
                    "calm": "Shaant",
                    "energetic": "Veer",
                    "sad": "Shok",
                    "neutral": "Shaant"
                }
                rasa = emotion_rasa_map[emotion]
                
                # Get songs for this rasa
                rasa_songs = [s for s in songs if s.get('rasa') == rasa]
                recommended_songs = [s['_id'] for s in random.sample(rasa_songs, min(5, len(rasa_songs)))]
                played_songs = recommended_songs[:random.randint(2, len(recommended_songs))]
                
                # Session data
                session_created = datetime.utcnow() - timedelta(days=random.randint(1, 60))
                session_started = session_created + timedelta(minutes=random.randint(1, 5))
                session_ended = session_started + timedelta(minutes=random.randint(10, 45))
                
                session_doc = {
                    "_id": session_id,
                    "session_id": session_id,
                    "user_id": user_id,
                    "created_at": session_created,
                    "started_at": session_started,
                    "ended_at": session_ended,
                    "emotion": emotion,
                    "rasa": rasa,
                    "confidence": round(random.uniform(0.6, 0.99), 3),
                    "cognitive_data": {
                        "pre_test": {
                            "memory_score": random.randint(1, 6),
                            "reaction_time": random.randint(200, 600),
                            "accuracy_score": round(random.uniform(60, 95), 2)
                        },
                        "post_test": {
                            "memory_score": random.randint(1, 6),
                            "reaction_time": random.randint(150, 500),
                            "accuracy_score": round(random.uniform(65, 98), 2)
                        }
                    },
                    "recommended_songs": recommended_songs,
                    "played_songs": played_songs,
                    "ratings": [],  # Will be populated with rating_ids
                    "images": [],  # Will be populated with image_ids
                    "psychometric_tests": [],  # Will be populated with test_ids
                    "feedback": None,
                    "status": "completed",
                    "duration_minutes": round((session_ended - session_started).total_seconds() / 60, 2)
                }
                sessions_to_insert.append(session_doc)
                
                # Create ratings for played songs
                rating_ids = []
                for played_song_id in played_songs:
                    rating_id = f"rating_{uuid4().hex[:12]}"
                    rating_doc = {
                        "_id": rating_id,
                        "rating_id": rating_id,
                        "session_id": session_id,
                        "user_id": user_id,
                        "song_id": played_song_id,
                        "rating": random.randint(3, 5),
                        "feedback_text": random.choice([
                            "Great song for my mood!",
                            "Really relaxing",
                            "Perfect therapeutic music",
                            "Helped me feel better",
                            None,
                            None
                        ]),
                        "timestamp": session_ended - timedelta(minutes=random.randint(1, 10)),
                        "emotion_before": emotion,
                        "emotion_after": random.choice(emotions)
                    }
                    ratings_to_insert.append(rating_doc)
                    rating_ids.append(rating_id)
                
                # Add rating IDs to session
                session_doc["ratings"] = rating_ids
                
                # Create session images (captured during session)
                image_ids = []
                for img_idx in range(random.randint(3, 10)):
                    image_id = f"image_{uuid4().hex[:12]}"
                    image_doc = {
                        "_id": image_id,
                        "image_id": image_id,
                        "session_id": session_id,
                        "timestamp": session_started + timedelta(minutes=random.randint(0, int(session_doc["duration_minutes"]))),
                        "image_path": f"C:\\RagaRasa\\Sessions\\{session_id}\\frame_{img_idx:04d}.jpg",
                        "emotion_detected": emotion,
                        "confidence": round(random.uniform(0.5, 0.99), 3),
                        "facial_features": {
                            "face_detected": True,
                            "expression_intensity": round(random.uniform(0.3, 1.0), 2),
                            "gaze_direction": random.choice(["forward", "down", "up", "left", "right"])
                        }
                    }
                    images_to_insert.append(image_doc)
                    image_ids.append(image_id)
                
                session_doc["images"] = image_ids
                
                # Create psychometric tests (pre and post)
                test_ids = []
                
                # Pre-test
                pre_test_id = f"test_{uuid4().hex[:12]}"
                pre_test_doc = {
                    "_id": pre_test_id,
                    "test_id": pre_test_id,
                    "session_id": session_id,
                    "user_id": user_id,
                    "test_type": "pre_test",
                    "timestamp": session_started - timedelta(minutes=2),
                    "data": {
                        "memory_score": random.randint(1, 6),
                        "reaction_time": random.randint(200, 600),
                        "accuracy_score": round(random.uniform(60, 95), 2)
                    },
                    "notes": "Pre-session cognitive assessment"
                }
                psychometric_to_insert.append(pre_test_doc)
                test_ids.append(pre_test_id)
                
                # Post-test
                post_test_id = f"test_{uuid4().hex[:12]}"
                post_test_doc = {
                    "_id": post_test_id,
                    "test_id": post_test_id,
                    "session_id": session_id,
                    "user_id": user_id,
                    "test_type": "post_test",
                    "timestamp": session_ended + timedelta(minutes=1),
                    "data": {
                        "memory_score": random.randint(1, 6),
                        "reaction_time": random.randint(150, 500),
                        "accuracy_score": round(random.uniform(65, 98), 2)
                    },
                    "notes": "Post-session cognitive assessment",
                    "improvement_percentage": round(random.uniform(5, 35), 2)
                }
                psychometric_to_insert.append(post_test_doc)
                test_ids.append(post_test_id)
                
                session_doc["psychometric_tests"] = test_ids
                
                # Add feedback to session
                session_doc["feedback"] = {
                    "mood_after": random.choice(["much better", "better", "same", "slightly better"]),
                    "session_rating": random.randint(4, 5),
                    "comment": random.choice([
                        "Great therapeutic experience",
                        "Very relaxing session",
                        "Loved the music recommendations",
                        "Felt more focused after",
                        None
                    ]),
                    "would_recommend": True,
                    "energy_level_after": random.randint(3, 5)
                }
        
        # Insert all data
        if sessions_to_insert:
            result = await self.db.sessions.insert_many(sessions_to_insert)
            logger.info(f"✓ Created {len(result.inserted_ids)} sessions")
        
        if ratings_to_insert:
            result = await self.db.ratings.insert_many(ratings_to_insert)
            logger.info(f"✓ Created {len(result.inserted_ids)} ratings")
        
        if images_to_insert:
            result = await self.db.images.insert_many(images_to_insert)
            logger.info(f"✓ Created {len(result.inserted_ids)} images")
        
        if psychometric_to_insert:
            result = await self.db.psychometric_tests.insert_many(psychometric_to_insert)
            logger.info(f"✓ Created {len(result.inserted_ids)} psychometric tests")
    
    async def seed_context_scores(self, user_ids, sessions_count=20):
        """Create context scores for analytics"""
        logger.info("=" * 60)
        logger.info("SEEDING CONTEXT SCORES")
        logger.info("=" * 60)
        
        context_scores = []
        
        for i in range(sessions_count):
            user_id = random.choice(user_ids)
            score_id = f"score_{uuid4().hex[:12]}"
            
            score_doc = {
                "_id": score_id,
                "score_id": score_id,
                "user_id": user_id,
                "session_id": f"session_{uuid4().hex[:12]}",
                "timestamp": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                "wellness_score": round(random.uniform(60, 100), 2),
                "engagement_score": round(random.uniform(50, 100), 2),
                "emotional_stability": round(random.uniform(40, 100), 2),
                "cognitive_improvement": round(random.uniform(20, 50), 2),
                "overall_therapy_effectiveness": round(random.uniform(60, 95), 2)
            }
            context_scores.append(score_doc)
        
        if context_scores:
            result = await self.db.context_scores.insert_many(context_scores)
            logger.info(f"✓ Created {len(result.inserted_ids)} context scores")
    
    async def verify_data(self):
        """Verify all data was inserted correctly"""
        logger.info("=" * 60)
        logger.info("DATA VERIFICATION")
        logger.info("=" * 60)
        
        collections_info = {
            "songs": await self.db.songs.count_documents({}),
            "users": await self.db.users.count_documents({}),
            "sessions": await self.db.sessions.count_documents({}),
            "ratings": await self.db.ratings.count_documents({}),
            "images": await self.db.images.count_documents({}),
            "psychometric_tests": await self.db.psychometric_tests.count_documents({}),
            "context_scores": await self.db.context_scores.count_documents({})
        }
        
        logger.info("Database Summary:")
        for collection, count in collections_info.items():
            logger.info(f"  {collection}: {count} documents")
        
        # Sample data verification
        logger.info("\nSample Data:")
        
        sample_song = await self.db.songs.find_one({})
        if sample_song:
            logger.info(f"  Sample Song: {sample_song['title']} ({sample_song['rasa']})")
        
        sample_session = await self.db.sessions.find_one({})
        if sample_session:
            logger.info(f"  Sample Session: {sample_session['session_id']} - User: {sample_session['user_id']}")
            logger.info(f"    Emotion: {sample_session['emotion']}, Rasa: {sample_session['rasa']}")
            logger.info(f"    Songs Played: {len(sample_session['played_songs'])}, Ratings: {len(sample_session['ratings'])}")
            logger.info(f"    Images: {len(sample_session['images'])}, Tests: {len(sample_session['psychometric_tests'])}")
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


async def main():
    """Main seeding function"""
    seeder = ComprehensiveSeeder()
    
    try:
        await seeder.connect()
        await seeder.clear_collections()
        
        # Seed all collections
        songs = await seeder.seed_songs()
        user_ids = await seeder.seed_users(count=5)
        await seeder.seed_sessions(user_ids, songs)
        await seeder.seed_context_scores(user_ids, sessions_count=20)
        
        # Verify
        await seeder.verify_data()
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ SEEDING COMPLETE")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        await seeder.close()


if __name__ == "__main__":
    asyncio.run(main())
