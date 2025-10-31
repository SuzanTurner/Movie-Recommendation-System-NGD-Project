"""
Streamlit UI for Movie Recommendation API
"""
import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Movie Recommendation System", layout="wide")
st.title("🎬 Movie Recommendation System")

page = st.sidebar.selectbox("Navigate", ["Browse Movies", "Rate Movie", "Get Recommendations", "Top Movies"])

if page == "Browse Movies":
	st.header("Browse Movies by Name")
	query = st.text_input("Enter Movie Name (partial match)", value="Inception")
	limit = st.slider("Max results", min_value=1, max_value=20, value=5)
	if st.button("Search"):
		try:
			response = requests.get(f"{API_URL}/movies/search", params={"q": query, "limit": limit})
			if response.status_code == 200:
				movies = response.json().get("movies", [])
				if not movies:
					st.info("No movies found")
				else:
					for m in movies:
						with st.container():
							st.subheader(m.get("title", "Unknown"))
							st.write(f"ID: {m.get('_id')}")
							st.write(f"Genre: {m.get('genre', 'N/A')}")
							st.write(f"Year: {m.get('year', 'N/A')}")
			else:
				st.error("Search failed")
		except Exception as e:
			st.error(f"Error: {str(e)}")

elif page == "Rate Movie":
	st.header("Rate a Movie")
	user_id = st.text_input("User ID", value="alice")
	movie_id = st.text_input("Movie ID", value="m1")
	rating = st.slider("Rating", min_value=1, max_value=5, value=5)
	if st.button("Submit Rating"):
		try:
			response = requests.post(f"{API_URL}/rate", json={"user_id": user_id, "movie_id": movie_id, "rating": rating})
			if response.status_code == 200:
				st.success("✅ Rating submitted!")
			else:
				st.error("Error submitting rating")
		except Exception as e:
			st.error(f"Error: {str(e)}")

elif page == "Get Recommendations":
	st.header("Get Recommendations")
	user_id = st.text_input("Enter User ID", value="alice")
	if st.button("Get Recommendations"):
		try:
			response = requests.get(f"{API_URL}/recommend/{user_id}")
			if response.status_code == 200:
				recommendations = response.json().get("recommendations", [])
				if recommendations:
					for rec in recommendations:
						st.write(f"**{rec.get('title')}** (ID: {rec.get('movie_id')}) - Frequency: {rec.get('freq')}")
				else:
					st.info("No recommendations found")
		except Exception as e:
			st.error(f"Error: {str(e)}")

elif page == "Top Movies":
	st.header("Top Rated Movies")
	limit = st.slider("Number of movies", min_value=1, max_value=20, value=5)
	if st.button("Refresh"):
		try:
			response = requests.get(f"{API_URL}/top_movies?limit={limit}")
			if response.status_code == 200:
				top_movies = response.json().get("top_movies", [])
				for i, (title, score) in enumerate(top_movies, 1):
					st.metric(f"{i}. {title}", f"{score:.1f} points")
		except Exception as e:
			st.error(f"Error: {str(e)}")

st.sidebar.markdown("---")
if st.sidebar.button("Check API Health"):
	try:
		response = requests.get(f"{API_URL}/health")
		if response.status_code == 200:
			health = response.json()
			st.sidebar.write("**Database Status:**")
			for db, status in health.items():
				if db != "status":
					st.sidebar.write(f"{db}: {status}")
	except:
		st.sidebar.error("Cannot connect to API")
