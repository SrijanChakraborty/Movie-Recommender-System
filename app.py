
from flask import Flask, render_template, request, jsonify
import pickle
import requests
import pandas as pd

app = Flask(__name__)


def fetch_poster(movieId):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=ee46d7f2824234db2ff7c05c6c4f665d&language=en-US".format(
        movieId)
    response = requests.get(url)
    data = response.json()
    poster_path = data["poster_path"]
    if poster_path:
        full_path = "https://image.tmdb.org/t/p/original/" + poster_path
        return full_path
    else:
        return None
    return full_path


@app.route('/get_genres', methods=['GET'])
def get_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en&api_key=ee46d7f2824234db2ff7c05c6c4f665d"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        genres = [{'id': genre['id'], 'name': genre['name']}
                  for genre in data.get('genres', [])]
        return jsonify(genres)
    else:
        return jsonify({"error": "Failed to fetch genres"}), response.status_code


@app.route('/get_movies_by_genre', methods=['GET'])
def get_movies_by_genre():
    genre_id = request.args.get('genre_id')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    url = f"https://api.themoviedb.org/3/discover/movie?api_key=ee46d7f2824234db2ff7c05c6c4f665d&with_genres={
        genre_id}&language=en-US&page={page}"
    response = requests.get(url)
    if response.status_code != 200:
       return jsonify({'error': 'Failed to fetch movies', 'status_code': response.status_code}), response.status_code

    data = response.json()
    movies = data.get('results', [])
    total_pages = data.get('total_pages', 1)
    movie_list = []
    for movie in movies:
        movie_list.append({
            'title': movie.get('title'),
            'poster_path': f"https://image.tmdb.org/t/p/original/{movie.get('poster_path', '')}"
        })

    return jsonify({'movies': movie_list, 'total_pages': total_pages})


with open('D:/Git Folder/Movie-Recommender-System/PickleFile/movies_name.pkl', 'rb') as file:
    movie_dict = pickle.load(file)
movies = pd.DataFrame(movie_dict)


@app.route('/')
def home():
    movie_titles = movies['title'].tolist()
    return render_template('index.html', movie_titles=movie_titles)


@app.route('/get_movie_titles', methods=['GET'])
def get_movie_titles():
    movie_titles = movies['title'].tolist()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    start = (page - 1) * limit
    end = start + limit
    titles = movie_titles[start:end]
    return jsonify(titles)


if __name__ == '__main__':

   app.run(debug=True, port=4000)
