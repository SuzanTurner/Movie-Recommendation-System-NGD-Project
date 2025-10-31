# Movie Recommendation System (FastAPI + Streamlit)

Simple recommendation system that combines:
- MongoDB for movies and user ratings
- Redis for a live “Top Movies” scoreboard
- Neo4j for collaborative-filtering recommendations

Includes a REST API (FastAPI) and a minimal UI (Streamlit).

## Setup

1) Install Python dependencies
```bash
pip install -r requirements.txt
```

2) Start required databases
- MongoDB: `mongodb://localhost:27017`
- Redis: `localhost:6379`
- Neo4j: `bolt://localhost:7687` (default user `neo4j`, set password accordingly)

3) Initialize sample data
```bash
python src/init_db.py
```

4) Run the API
```bash
python -m src.app.main
```
Visit API docs: http://localhost:8000/docs

5) Run the UI (optional)
```bash
streamlit run src/streamlit_app.py
```
Open UI: http://localhost:8501

## What you can do
- Browse by name: search movies by title in the UI
- Rate movies: `POST /rate` to record a rating and update the graph
- Get recommendations: `GET /recommend/{user_id}` based on similar users’ likes
- View top list: `GET /top_movies?limit=n` from Redis

## API Endpoints
- `GET /movies/search?q=<name>&limit=<n>`: search by movie title (case-insensitive)
- `GET /movie/{movie_id}`: get a single movie by ID
- `POST /rate`: body `{ user_id, movie_id, rating }`
- `GET /recommend/{user_id}`: graph-based recommendations
- `GET /top_movies?limit=<n>`: top movies from Redis
- `GET /health`: database connectivity snapshot

## How recommendations work
When you rate a movie, the API writes:
- A rating document to MongoDB
- A score bump for the movie title in Redis
- A `(:User)-[:LIKES]->(:Movie)` edge in Neo4j

Recommendations are computed with a Cypher pattern that finds movies liked by other users who like the same movies as you, ordered by frequency.

## Project structure
```
src/
  app/
    __init__.py
    main.py              # FastAPI API
    services/
      __init__.py
      mongodb.py         # MongoDB helpers
      redis_store.py     # Redis helpers
      neo4j_graph.py     # Neo4j helpers
  init_db.py             # Seeds MongoDB, Redis, Neo4j with sample data
  streamlit_app.py       # Streamlit UI
requirements.txt         # Python dependencies
readme.md                # This file
```
