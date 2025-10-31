import os
from typing import List, Dict, Any
from neo4j import GraphDatabase


NEO_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO_USER = os.getenv("NEO4J_USER", "neo4j")
NEO_PASS = os.getenv("NEO4J_PASS", "Chess@123")

try:
	neo_driver = GraphDatabase.driver(NEO_URI, auth=(NEO_USER, NEO_PASS), connection_timeout=2)
	neo_driver.verify_connectivity()
except Exception as e:
	print(f"Neo4j connection error: {e}")
	print("  Tip: Start Neo4j Desktop or Docker container")
	neo_driver = None


def create_like_edge(user_id: str, movie_id: str, title: str) -> None:
	if not neo_driver:
		return
	try:
		with neo_driver.session() as s:
			s.run(
				"""
				MERGE (u:User {user_id:$user_id})
				MERGE (m:Movie {movie_id:$movie_id, title:$title})
				MERGE (u)-[:LIKES]->(m)
				""",
				user_id=user_id,
				movie_id=movie_id,
				title=title or "Unknown",
			)
	except Exception as e:
		print(f"Neo4j update error: {e}")


def recommend_for_user(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
	if not neo_driver:
		return []
	query = """
	MATCH (u:User {user_id:$uid})-[:LIKES]->(m:Movie)<-[:LIKES]-(other:User)-[:LIKES]->(rec:Movie)
	WHERE NOT (u)-[:LIKES]->(rec)
	RETURN rec.movie_id as movie_id, rec.title as title, count(*) as freq
	ORDER BY freq DESC
	LIMIT $limit
	"""
	try:
		with neo_driver.session() as s:
			rows = s.run(query, uid=user_id, limit=limit)
			return [dict(r) for r in rows]
	except Exception as e:
		print(f"Recommendation error: {e}")
		return []


def health() -> str:
	if not neo_driver:
		return "disconnected"
	try:
		neo_driver.verify_connectivity()
		return "connected"
	except Exception:
		return "disconnected"
