"""
Basic interface with TMDb API
"""
import requests

API_KEY = ""
HEADERS = {
    "Authorization": "Bearer " + API_KEY
}
BASE_URL = "https://api.themoviedb.org/3/"
BASE_POSTER_PATH = "https://www.themoviedb.org/t/p/w600_and_h900_bestv2"
BASE_BACKDROP_PATH = "https://www.themoviedb.org/t/p/original"

def search_movie(query, page = 1):
    """
    Searches the TMDb API for movies
    """
    url = BASE_URL + "search/movie?query=" + query + "&include_adult=false&language=en-US&page=" + str(page)
    results = requests.get(url, headers=HEADERS, timeout=60)
    if not results.ok:
        return []
    json = results.json()
    movies = []
    for result in json["results"]:
        tmdb_id = result["id"]
        title = result["title"]
        plot = result["overview"]
        poster = BASE_POSTER_PATH + result["poster_path"]
        fanart = BASE_BACKDROP_PATH + result["backdrop_path"] if result["backdrop_path"] else None
        movies.append({
            "id": tmdb_id,
            "title": title,
            "plot": plot,
            "poster": poster,
            "fanart": fanart,
            "playable": True,
            "type": "movie"
        })
    return movies
