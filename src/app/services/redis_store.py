import os
from typing import List, Tuple
import redis


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

try:
	r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True, socket_connect_timeout=2)
	r.ping()
except Exception as e:
	print(f"Redis connection error: {e}")
	print("  Tip: Start Redis server. Windows: redis-server.exe or choco install redis-64")
	r = None


def increment_movie_score(title: str, amount: float) -> None:
	if not r:
		return
	try:
		r.zincrby("top_movies", amount, title)
	except Exception as e:
		print(f"Redis update error: {e}")


def get_top_movies(limit: int = 5) -> List[Tuple[str, float]]:
	if not r:
		return []
	return r.zrevrange("top_movies", 0, limit - 1, withscores=True)


def health() -> str:
	if not r:
		return "disconnected"
	try:
		r.ping()
		return "connected"
	except Exception:
		return "disconnected"
