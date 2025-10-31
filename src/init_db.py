"""
Simple database initialization script
Run this once to set up sample data
"""
import time
from pymongo import MongoClient
import redis
from neo4j import GraphDatabase

# Configuration
MONGO_URI = "mongodb://localhost:27017"
REDIS_HOST = "localhost"
NEO_URI = "bolt://127.0.0.1:7687"
NEO_USER = "neo4j"
NEO_PASS = "Chess@123"

print("Initializing databases...")

# MongoDB
print("Setting up MongoDB...")
mc = MongoClient(MONGO_URI)
db = mc["movie_db"]
movies = db["movies"]
movies.delete_many({})
sample_movies = [
	{"_id": "m1", "title": "Inception", "genre": "Sci-Fi", "year": 2010, "director": "Christopher Nolan"},
	{"_id": "m2", "title": "Avatar", "genre": "Adventure", "year": 2009, "director": "James Cameron"},
	{"_id": "m3", "title": "The Matrix", "genre": "Sci-Fi", "year": 1999, "director": "Wachowski Brothers"},
	{"_id": "m4", "title": "Interstellar", "genre": "Sci-Fi", "year": 2014, "director": "Christopher Nolan"},
	{"_id": "m5", "title": "The Dark Knight", "genre": "Action", "year": 2008, "director": "Christopher Nolan"},
	{"_id": "m6", "title": "Pulp Fiction", "genre": "Crime", "year": 1994, "director": "Quentin Tarantino"},
	{"_id": "m7", "title": "The Godfather", "genre": "Crime", "year": 1972, "director": "Francis Ford Coppola"},
	{"_id": "m8", "title": "Fight Club", "genre": "Drama", "year": 1999, "director": "David Fincher"},
	{"_id": "m9", "title": "Forrest Gump", "genre": "Drama", "year": 1994, "director": "Robert Zemeckis"},
	{"_id": "m10", "title": "The Shawshank Redemption", "genre": "Drama", "year": 1994, "director": "Frank Darabont"},
	{"_id": "m11", "title": "Titanic", "genre": "Romance", "year": 1997, "director": "James Cameron"},
	{"_id": "m12", "title": "The Avengers", "genre": "Action", "year": 2012, "director": "Joss Whedon"},
	{"_id": "m13", "title": "Jurassic Park", "genre": "Adventure", "year": 1993, "director": "Steven Spielberg"},
	{"_id": "m14", "title": "Star Wars", "genre": "Sci-Fi", "year": 1977, "director": "George Lucas"},
	{"_id": "m15", "title": "The Lord of the Rings", "genre": "Fantasy", "year": 2001, "director": "Peter Jackson"},
]
movies.insert_many(sample_movies)
print(f"✓ MongoDB initialized with {len(sample_movies)} movies")

# Redis
print("Setting up Redis...")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
r.flushall()
# Initial rankings with varied scores
r.zadd("top_movies", {
	"Inception": 25,
	"The Matrix": 30,
	"The Dark Knight": 28,
	"Interstellar": 22,
	"Pulp Fiction": 35,
	"The Godfather": 40,
	"The Shawshank Redemption": 38,
	"Forrest Gump": 32,
	"Titanic": 20,
	"The Avengers": 18,
	"Jurassic Park": 26,
	"Star Wars": 42,
	"The Lord of the Rings": 36,
	"Avatar": 15,
	"Fight Club": 24
})
print("✓ Redis initialized with top movies rankings")

# Ratings in MongoDB
print("Setting up ratings in MongoDB...")
ratings = db["ratings"]
ratings.delete_many({})
base_ts = int(time.time() * 1000)
ratings_data = [
	("alice", base_ts - 10000, "m1", 5),
	("alice", base_ts - 9000, "m3", 5),
	("alice", base_ts - 8000, "m5", 4),
	("alice", base_ts - 7000, "m6", 5),
	("bob", base_ts - 6000, "m2", 4),
	("bob", base_ts - 5000, "m4", 5),
	("bob", base_ts - 4000, "m7", 5),
	("bob", base_ts - 3000, "m12", 4),
	("charlie", base_ts - 2000, "m1", 5),
	("charlie", base_ts - 1000, "m5", 5),
	("charlie", base_ts, "m8", 4),
	("diana", base_ts - 1500, "m9", 5),
	("diana", base_ts - 500, "m10", 5),
	("diana", base_ts - 250, "m11", 4),
	("eve", base_ts - 750, "m14", 5),
	("eve", base_ts - 600, "m15", 5),
	("eve", base_ts - 450, "m13", 4),
]
ratings.insert_many([
	{"user_id": u, "rated_time": ts, "movie_id": m, "rating": r}
	for (u, ts, m, r) in ratings_data
])
print(f"✓ MongoDB initialized with {len(ratings_data)} ratings")

# Neo4j
print("Setting up Neo4j...")
driver = GraphDatabase.driver(NEO_URI, auth=(NEO_USER, NEO_PASS))
with driver.session() as s:
	# Clear existing data
	s.run("MATCH (n) DETACH DELETE n")
	
	# Create users
	users = ["alice", "bob", "charlie", "diana", "eve", "frank", "grace"]
	for user_id in users:
		s.run("CREATE (u:User {user_id: $user_id})", user_id=user_id)
	
	# Create movies with titles
	movie_data = [
		("m1", "Inception"), ("m2", "Avatar"), ("m3", "The Matrix"), 
		("m4", "Interstellar"), ("m5", "The Dark Knight"), ("m6", "Pulp Fiction"),
		("m7", "The Godfather"), ("m8", "Fight Club"), ("m9", "Forrest Gump"),
		("m10", "The Shawshank Redemption"), ("m11", "Titanic"), ("m12", "The Avengers"),
		("m13", "Jurassic Park"), ("m14", "Star Wars"), ("m15", "The Lord of the Rings")
	]
	
	for movie_id, title in movie_data:
		s.run("CREATE (m:Movie {movie_id: $movie_id, title: $title})", 
				movie_id=movie_id, title=title)
	
	# Create LIKES relationships (more diverse)
	relationships = [
		("alice", "m1"), ("alice", "m3"), ("alice", "m5"), ("alice", "m6"),
		("bob", "m2"), ("bob", "m4"), ("bob", "m7"), ("bob", "m12"),
		("charlie", "m1"), ("charlie", "m5"), ("charlie", "m8"), ("charlie", "m14"),
		("diana", "m9"), ("diana", "m10"), ("diana", "m11"), ("diana", "m15"),
		("eve", "m14"), ("eve", "m15"), ("eve", "m13"), ("eve", "m3"),
		("frank", "m7"), ("frank", "m6"), ("frank", "m5"), ("frank", "m8"),
		("grace", "m11"), ("grace", "m9"), ("grace", "m4"), ("grace", "m15"),
	]
	
	for user_id, movie_id in relationships:
		s.run("""
			MATCH (u:User {user_id: $user_id}), (m:Movie {movie_id: $movie_id})
			CREATE (u)-[:LIKES]->(m)
		""", user_id=user_id, movie_id=movie_id)
	

driver.close()
print(f"✓ Neo4j initialized with {len(users)} users, {len(movie_data)} movies, and {len(relationships)} relationships")

print("\n" + "="*50)
print("✅ All databases initialized successfully!")
print("="*50)
print(f"\n📊 Summary:")
print(f"   • {len(sample_movies)} movies in MongoDB")
print(f"   • Top movies rankings in Redis")
print(f"   • Ratings stored in MongoDB")
print(f"   • Graph relationships in Neo4j")
print(f"\n🎬 Sample movies: m1-m15")
print(f"👥 Sample users: alice, bob, charlie, diana, eve, frank, grace")
print(f"\nYou can now start the API with: python -m src.app.main")
print("="*50)
