"""
Basic interface with TMDb API
"""
import requests

BASE_URL = "https://api.themoviedb.org/3/"
BASE_POSTER_PATH = "https://www.themoviedb.org/t/p/w600_and_h900_bestv2"
BASE_BACKDROP_PATH = "https://www.themoviedb.org/t/p/original"

def _get_year(datestr):
    if not datestr:
        return "-"
    parts = datestr.split("-")
    if len(parts) > 0:
        return parts[0]
    return "-"

def search_movie(query, key, page = 1):
    """
    Searches the TMDb API for movies
    """
    headers = {
        "Authorization": "Bearer " + key
    }
    url = BASE_URL + "search/movie?query=" + query + "&include_adult=false&language=en-US&page=" + str(page)
    results = requests.get(url, headers=headers, timeout=60)
    if not results.ok:
        return []
    json = results.json()
    movies = []
    for result in json["results"]:
        tmdb_id = result["id"]
        title = result["title"] + " (" + _get_year(result["release_date"]) + ")"
        plot = result["overview"]
        poster = BASE_POSTER_PATH + result["poster_path"] if result["poster_path"] else None
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

def search_tv(query, key, page = 1):
    """
    Searches the TMDb API for shows
    """
    headers = {
        "Authorization": "Bearer " + key
    }
    url = BASE_URL + "search/tv?query=" + query + "&include_adult=false&language=en-US&page=" + str(page)
    results = requests.get(url, headers=headers, timeout=60)
    if not results.ok:
        return []
    json = results.json()
    shows = []
    for result in json["results"]:
        tmdb_id = result["id"]
        title = result["name"]
        plot = result["overview"]
        poster = BASE_POSTER_PATH + result["poster_path"] if result["poster_path"] else None
        fanart = BASE_BACKDROP_PATH + result["backdrop_path"] if result["backdrop_path"] else None
        shows.append({
            "id": tmdb_id,
            "title": title,
            "plot": plot,
            "poster": poster,
            "fanart": fanart,
            "playable": False,
            "type": "tv"
        })
    return shows

def get_seasons(tmdb_id, key):
    """
    Returns all the seasons in a show
    """
    headers = {
        "Authorization": "Bearer " + key
    }
    url = BASE_URL + "tv/" + str(tmdb_id)
    result = requests.get(url, headers=headers, timeout=60)
    if not result.ok:
        return []
    json = result.json()
    found = []
    seasons = json["seasons"]
    for season in seasons:
        tmdb_id = json["id"]
        title = season["name"]
        plot = season["overview"]
        poster = BASE_POSTER_PATH + season["poster_path"] if season["poster_path"] else None
        fanart = BASE_BACKDROP_PATH + json["backdrop_path"] if json["backdrop_path"] else None
        number = season["season_number"]
        found.append({
            "id": tmdb_id,
            "title": title,
            "plot": plot,
            "poster": poster,
            "fanart": fanart,
            "season": number,
            "playable": False,
            "type": "season"
        })
    return found

def get_episodes(tmdb_id, season, key):
    headers = {
        "Authorization": "Bearer " + key
    }
    url = BASE_URL + "tv/" + str(tmdb_id) + "/season/" + str(season)
    result = requests.get(url, headers=headers, timeout=60)
    if not result.ok:
        return []
    json = result.json()
    found = []
    episodes = json["episodes"]
    for episode in episodes:
        number = episode["episode_number"]
        title = "Episode " + str(number) + ": " + episode["name"]
        plot = episode["overview"]
        poster = BASE_BACKDROP_PATH + episode["still_path"] if episode["still_path"] else None
        fanart = BASE_BACKDROP_PATH + episode["still_path"] if episode["still_path"] else None
        found.append({
            "id": tmdb_id,
            "title": title,
            "plot": plot,
            "poster": poster,
            "fanart": fanart,
            "season": season,
            "episode": number,
            "playable": True,
            "type": "episode"
        })
    return found
