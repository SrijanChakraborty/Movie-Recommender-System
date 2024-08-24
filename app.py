from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd

app = Flask(__name__)

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
