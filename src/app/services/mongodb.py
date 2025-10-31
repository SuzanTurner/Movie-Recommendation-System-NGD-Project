from typing import Any, Dict, List, Optional
from pymongo import MongoClient
import os


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

try:
	mongo_client = MongoClient(MONGO_URI)
	mongo_db = mongo_client["movie_db"]
	movies_col = mongo_db["movies"]
	ratings_col = mongo_db["ratings"]
except Exception as e:
	print(f"MongoDB connection error: {e}")
	mongo_client = None
	mongo_db = None
	movies_col = None
	ratings_col = None


def get_movie_by_id(movie_id: str) -> Optional[Dict[str, Any]]:
	if not movies_col:
		return None
	doc = movies_col.find_one({"_id": movie_id})
	if not doc:
		return None
	doc["_id"] = str(doc["_id"])  # Ensure serializable
	return doc


def search_movies_by_title(query: str, limit: int = 10) -> List[Dict[str, Any]]:
	if not movies_col:
		return []
	cursor = movies_col.find({"title": {"$regex": query, "$options": "i"}}).limit(limit)
	results: List[Dict[str, Any]] = []
	for doc in cursor:
		doc["_id"] = str(doc["_id"])  # Ensure serializable
		results.append(doc)
	return results


def insert_rating(user_id: str, movie_id: str, rating: int, rated_time_ms: int) -> None:
	if not ratings_col:
		return
	try:
		ratings_col.insert_one({
			"user_id": user_id,
			"movie_id": movie_id,
			"rating": rating,
			"rated_time": rated_time_ms,
		})
	except Exception as e:
		print(f"MongoDB rating insert error: {e}")
