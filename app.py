
from flask import Flask, render_template, request, jsonify
import pickle
import requests
import pandas as pd
import numpy as np
import joblib

app = Flask(__name__)

with open('D:/Git Folder/Movie-Recommender-System/PickleFile/movies_name.pkl', 'rb') as file:
    movie_dict = pickle.load(file)
movies = pd.DataFrame(movie_dict)


data = joblib.load(
    'D:\\Git Folder\\Movie-Recommender-System\\PickleFile\\model_save')


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


movie_titles = movies['title'].tolist()

@app.route('/')
def home():
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


def recommended(movie):
    if not isinstance(data, np.ndarray):
        print("Error: Data is not a NumPy array.")
        return [], []

    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distance = data[movie_index]

        if not isinstance(distance, (list, np.ndarray)):
            raise TypeError("Expected distance to be a list or numpy array.")

        movie_list = sorted(list(enumerate(distance)),
                            reverse=True, key=lambda x: x[1])[1:11]

        recommended_movies = []
        for i in movie_list:
            movie_id = movies.iloc[i[0]]['id']
            title = movies.iloc[i[0]]['title']
            poster_path = fetch_poster(movie_id)

            recommended_movies.append({
                'id': movie_id,
                'title': title,
                'poster_path': poster_path
            })
            print("recommended_movies==>", recommended_movies)

        return recommended_movies
    except Exception as e:
        print(f"An error occurred: {e}")
        return [], []


@app.route('/recommend', methods=['GET'])
def recommend1():
    print("similarity==>", data)
    movie_title = request.args.get('movie_title')
    if not movie_title:
        return "Movie title not provided", 400

    print("movie_title===>", movie_title)

    if data is None:
        return "Error: Recommendation system not available due to pickle file corruption", 500

    recommended_movies = recommended(movie_title)

    print("Recommended==>", recommended_movies)
    return render_template('recommended.html',
                           selected_movie=movie_title,
                           recommended_movies=recommended_movies)


if __name__ == '__main__':
    app.run(debug=True, port=4000)
