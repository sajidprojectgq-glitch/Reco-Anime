import os,json
import sqlite3
import random
from collections import defaultdict


path = "static/api.json"



def fetch(path):
    if os.path.exists(path):
        with open(path,"r", encoding='utf-8') as file:
            data = json.load(file)
            return data
    else:
        print('Not found')

def load_data():
    api = []
    data = fetch(path)
    for anime in data:
        api.append(anime)
    return api

def watch():
    try:
        api_data = load_data()

        # Categories
        good, skip, watchskip, bad, awesome, must = [], [], [], [], [], []

        # ✅ Categorize first
        for anime in api_data:
            worth = anime.get('worth_watch', {})
            if 'must watch' in worth:
                must.append(anime)
            elif 'awesome' in worth:
                awesome.append(anime)
            elif 'good' in worth:
                good.append(anime)
            elif 'skip' in worth:
                skip.append(anime)
            elif "watch or skip" in worth:
                watchskip.append(anime)
            elif 'bad' in worth:
                bad.append(anime)

        # ✅ Sorting helper
        def sort_by_popularity(anime_list, reverse=True):
            return sorted(
                anime_list,
                key=lambda x: x.get("api_data", {}).get("popularity", 0),
                reverse=reverse
            )

        # ✅ Sort every category
        must = sort_by_popularity(must)
        awesome = sort_by_popularity(awesome)
        good = sort_by_popularity(good)
        skip = sort_by_popularity(skip)
        watchskip = sort_by_popularity(watchskip)
        bad = sort_by_popularity(bad)

        return {
            "must": must,
            "awesome": awesome,
            "good": good,
            "skip": skip,
            "watchskip": watchskip,
            "bad": bad,
        }
    except KeyError:
        return {}

def api_id(mal_id):
    try:
        api_data = load_data()
        for anime in api_data:
            api = anime.get("api_data", {})
            if api.get("mal_id") == mal_id:
                return anime   # return dict directly
        return None
    except (TypeError, KeyError):
        return None
    
def api_id2(mal_id):
    try:
        api_data = load_data()
        result = []

        for anime in api_data:
            api = anime.get('api_data', {})
            anime_id = api.get('mal_id')

            if anime_id == mal_id:
                result.append(anime)

        return result
    except TypeError:
        return []



def fetch_data(query):
    api_data = load_data()
    result = []

    # Normalize query: make it lowercase, handle empty
    query = query.lower().strip() if query else ""

    for anime in api_data:
        api = anime.get("api_data", {})
        title = api.get("title_english", "") or ""
        name = anime.get("title", "") or ""

        # Lowercase match
        if query in title.lower() or query in name.lower():
            result.append(anime)

    return result

def genres_fetch(genre=None, themes=None):
    result = []
    anime_data = load_data()

    if genre is None and themes is None:
        return result
    
    for anime in anime_data:
        api = anime.get('api_data', {})
        anime_genres = api.get('genres', [])
        anime_themes = api.get('themes', [])

        match_genres =  any(g in anime_genres for g in genre) if genre else True
        match_themes =  any(t in anime_themes for t in themes) if themes else True

        if match_genres and match_themes:
            result.append(anime)
    
    return result


def random_fetch(count=30):
    api_data = load_data()
    if not api_data:
        return []

    # Only keep anime that are worth watching
    valid_tags = {"must watch", "awesome", "good"}
    filtered_data = [a for a in api_data if a.get("worth_watch", "").lower() in valid_tags]

    if not filtered_data:
        return []

    # Group anime by genre
    genre_dict = defaultdict(list)
    for anime in filtered_data:
        for g in anime["api_data"].get("genres", []):
            genre_dict[g].append(anime)

    result = []
    genres = list(genre_dict.keys())

    # Keep picking until we reach `count`
    while len(result) < count and genres:
        g = random.choice(genres)  # pick a random genre
        if genre_dict[g]:
            result.append(random.choice(genre_dict[g]))  # pick a random anime from that genre
        else:
            genres.remove(g)

    return result


def get_similar_anime(target_anime, all_anime, limit=30):
    """Find anime similar to target_anime based on shared genres/themes."""
    if not target_anime or not all_anime:
        return []

    target_genres = set(target_anime["api_data"].get("genres", []))
    target_themes = set(target_anime["api_data"].get("themes", []))

    scored = []
    for anime in all_anime:
        if anime["api_data"]["mal_id"] == target_anime["api_data"]["mal_id"]:
            continue  # skip same anime

        genres = set(anime["api_data"].get("genres", []))
        themes = set(anime["api_data"].get("themes", []))

        # Calculate similarity score
        score = len(target_genres & genres) + len(target_themes & themes)

        if score > 0:
            scored.append((score, anime))

    # Sort by similarity (highest score first) and limit
    scored.sort(key=lambda x: x[0], reverse=True)
    return [anime for _, anime in scored[:limit]]
