from flask import Flask, render_template, url_for, request,redirect,flash,jsonify
from fetch import *
import secrets

app = Flask(__name__,template_folder='templates', static_folder='static', static_url_path='/')
app.secret_key = "super-secret-key-123"  #just for show # use any random string, keep it private

@app.route('/')
def home():
    worth = watch()
    return render_template('home.html', **worth)

@app.route('/view/<anime_id>')
@app.route('/view')
def view(anime_id):
    random = random_fetch()
    worth = watch()
    return render_template("view.html",**worth,anime_id=anime_id,random=random)

@app.route('/details/<int:mal_id>')   # enforce mal_id as int
def details(mal_id):
    all_anime = load_data()
    detail = api_id2(mal_id)
    random_anime = random_fetch()
    target = next((a for a in all_anime if a["api_data"]["mal_id"] == mal_id), None)
    similar = get_similar_anime(target, all_anime, limit=16)

    return render_template("details.html", anime_id=mal_id, detail=detail, random_anime=random_anime, similar=similar )



@app.route('/search')
def search():
    query = request.args.get('query')
    genres = request.args.getlist('genre')
    themes = request.args.getlist('themes')

    results = None
    querys = None

    if query:  
        # If user searched from bar
        querys = fetch_data(query)

    if genres or themes:  
        # If user applied filters
        results = genres_fetch(genres, themes=themes)

    return render_template(
        "search.html",
        query=query,
        querys=querys,
        results=results
    )


import random

@app.route("/random")
def random_reco():
    all_anime = load_data()
    return render_template('view.html')
    


if __name__ == "__main__":
    app.run(debug=True)