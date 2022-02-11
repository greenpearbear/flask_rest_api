from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __table_name__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    __table_name__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __table_name__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        genre_id = request.args.get('genre_id')
        director_id = request.args.get('director_id')
        if genre_id or director_id:
            all_movies_filter = \
                db.session.query(Movie).filter(Movie.genre_id == genre_id, Movie.director_id == director_id)
            return MovieSchema(many=True).dump(all_movies_filter), 200
        if genre_id:
            all_movies_filter = \
                db.session.query(Movie).filter(Movie.genre_id == genre_id)
            return MovieSchema(many=True).dump(all_movies_filter), 200
        if director_id:
            all_movies_filter = \
                db.session.query(Movie).filter(Movie.director_id == director_id)
            return MovieSchema(many=True).dump(all_movies_filter), 200
        all_movies = db.session.query(Movie).all()
        return MovieSchema(many=True).dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)

        return "", 201


@movies_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid: int):
        try:
            movie = db.session.query(Movie).filter(Movie.id == uid).one()
            return MovieSchema().dump(movie), 200

        except Exception as e:
            return str(e), 404

    def put(self, uid: int):
        try:
            movie = db.session.query(Movie).filter(Movie.id == uid).one()
            req_json = request.json
            movie.id = req_json.get("id")
            movie.title = req_json.get("title")
            movie.description = req_json.get("description")
            movie.trailer = req_json.get("trailer")
            movie.year = req_json.get("year")
            movie.rating = req_json.get("rating")
            movie.genre_id = req_json.get("genre_id")
            movie.director_id = req_json.get("director_id")

            with db.session.begin():
                db.session.add(movie)

            return "", 200

        except Exception as e:
            return str(e), 404

    def delete(self, uid: int):
        try:
            movie = db.session.query(Movie).filter(Movie.id == uid).one()

            with db.session.begin():
                db.session.delete(movie)

            return "", 204
        except Exception as e:
            return str(e), 404


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return DirectorSchema(many=True).dump(all_directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)

        with db.session.begin():
            db.session.add(new_director)

        return "", 201


@directors_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid: int):
        try:
            director = db.session.query(Director).filter(Director.id == uid).one()
            return DirectorSchema().dump(director), 200
        except Exception as e:
            return str(e), 404

    def put(self, uid: int):
        try:
            req_json = request.json
            director = db.session.query(Director).filter(Director.id == uid).one()
            director.id = req_json.get('id')
            director.name = req_json.get('name')

            with db.session.begin():
                db.session.add(director)

            return "", 200
        except Exception as e:
            return str(e), 404

    def delete(self, uid: int):
        try:
            director = db.session.query(Director).filter(Director.id == uid).one()

            with db.session.begin():
                db.session.delete(director)
            return "", 204
        except Exception as e:
            return str(e), 404


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genre = db.session.query(Genre).all()
        return GenreSchema(many=True).dump(all_genre), 200

    def post(self):
        req_json = request.json
        genre = Genre(**req_json)

        with db.session.begin():
            db.session.add(genre)
        return "", 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid: int):
        try:
            genre = db.session.query(Genre).filter(Genre.id == uid).one()
            return GenreSchema().dump(genre), 200
        except Exception as e:
            return str(e), 404

    def put(self, uid: int):
        try:
            req_json = request.json
            genre = db.session.query(Genre).filter(Genre.id == uid).one()
            genre.id = req_json.get('id')
            genre.name = req_json.get('name')

            with db.session.begin():
                db.session.add(genre)
            return "", 200
        except Exception as e:
            return str(e), 404

    def delete(self, uid: int):
        try:
            genre = db.session.query(Genre).filter(Genre.id == uid).one()

            with db.session.begin():
                db.session.delete(genre)
            return "", 204

        except Exception as e:
            return str(e), 404


if __name__ == '__main__':
    app.run(debug=True)
