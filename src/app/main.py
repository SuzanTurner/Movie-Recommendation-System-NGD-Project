from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import time

from .services.mongodb import (
	get_movie_by_id,
	search_movies_by_title,
	insert_rating,
	movies_col,
)
from .services.redis_store import get_top_movies, increment_movie_score, health as redis_health
from .services.neo4j_graph import create_like_edge, recommend_for_user, health as neo_health


app = FastAPI(title="Movie Recommendation API", version="1.0.0")


class RateRequest(BaseModel):
	user_id: str
	movie_id: str
	rating: int = Field(ge=1, le=5)


@app.get("/")

def root():
	return {"message": "Movie Recommendation API", "docs": "/docs"}


@app.get("/movie/{movie_id}")

def get_movie(movie_id: str):
	doc = get_movie_by_id(movie_id)
	if not doc:
		raise HTTPException(status_code=404, detail="Movie not found")
	return {"movie": doc}


@app.get("/movies/search")

def search_movies(q: str, limit: int = 10):
	if not q or q.strip() == "":
		raise HTTPException(status_code=400, detail="Query 'q' is required")
	results = search_movies_by_title(q, limit)
	return {"movies": results}


@app.get("/top_movies")

def top_movies(limit: int = 5):
	items = get_top_movies(limit)
	return {"top_movies": items}


@app.post("/rate")

def rate_movie(req: RateRequest):
	# Store rating in MongoDB
	insert_rating(req.user_id, req.movie_id, req.rating, int(time.time() * 1000))

	# Update Redis score
	title = None
	if movies_col:
		m = movies_col.find_one({"_id": req.movie_id})
		if m:
			title = m.get("title")
	if title:
		increment_movie_score(title, req.rating)

	# Create LIKES edge in Neo4j
	create_like_edge(req.user_id, req.movie_id, title or "Unknown")

	return {"status": "ok"}


@app.get("/recommend/{user_id}")

def recommend(user_id: str):
	recs = recommend_for_user(user_id)
	return {"recommendations": recs}


@app.get("/health")

def health():
	status = {"status": "ok"}
	# Mongo
	try:
		if movies_col:
			movies_col.find_one()
			status["mongodb"] = "connected"
		else:
			status["mongodb"] = "disconnected"
	except Exception:
		status["mongodb"] = "disconnected"
	# Redis
	status["redis"] = redis_health()
	# Neo4j
	status["neo4j"] = neo_health()
	return status


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)
