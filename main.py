from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

# Создаем приложение Flask
app = Flask(__name__)

# Настраиваем работу с базой данных
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Создаем соединение с базой данных
db = SQLAlchemy(app)


# __________Описание модели базы данных__________
class Movie(db.Model):
    __tablename__ = "movie"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = "director"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Genre(db.Model):
    __tablename__ = "genre"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


# __________Описание схемы сериализации через marshmallow__________
class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


# __________Создание объектов для сериализации__________
movie_schema = MovieSchema()  # В единственном экземпляре
movies_schema = MovieSchema(many=True)  # Множество экземпляров

director_schema = DirectorSchema()  # В единственном экземпляре
directors_schema = DirectorSchema(many=True)  # Множество экземпляров

genre_schema = GenreSchema()  # В единственном экземпляре
genres_schema = GenreSchema(many=True)  # Множество экземпляров


# __________Создание API__________
api = Api(app)

# __________Создание NameSpace для работы с книгами__________
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


# __________Создание сущностей (представителей класса Book)__________
# m1 = Movie(id=1, name="Harry Potter", year=2000)
# m2 = Movie(id=2, name="Le Comte de Monte-Cristo", year=1844)
#
# a1 = Author(id=1, first_name="Joan", last_name="Rouling")
# a2 = Author(id=2, first_name="Alexandre", last_name="Dumas")


with app.app_context():

    # # __________Создание таблиц__________
    # db.drop_all()
    # db.create_all()

    # __________Открытие сессии и сохранение данных в БД__________

    with db.session.begin():

    # __________________________________________
    # _______________Movies Views________________
    # __________________________________________


        @movies_ns.route('/')  # /movies/
        class MoviesView(Resource):
            def get(self):  # Получение данных
                # Получение фильмов через обращение к объекту БД
                movie_query = db.session.query(Movie).all()

                # Получение фильмов определенного режиссера через обращение к объекту БД
                director_id = request.args.get("director_id")
                if director_id is not None:
                    movie_query = movie_query.filter(Movie.director_id == director_id)

                # Получение фильмов определенного жанра через обращение к объекту БД
                genre_id = request.args.get("genre_id")
                if genre_id is not None:
                    movie_query = movie_query.filter(Movie.genre_id == genre_id)

                # Получение списка результатов через метод сериализации
                return movies_schema.dump(movie_query), 200

            def post(self):  # Добавление данных
                # Работа с запросом. Получение данных в формате JSON
                red_json = request.json
                # Распаковка JSON. Десериализация.
                new_movie = Movie(**red_json)
                # Открытие сессии и сохранение фильма в БД
                with db.session.begin():
                    db.session.add(new_movie)
                # Код 201: Объект создан.
                return "Movie created", 201


        @movies_ns.route('/<int:id>')  # /movies/<int:id>
        class MovieView(Resource):
            def get(self, id: int):  # Получение данных
                try:
                    # Получение данных из БД по ID
                    movie = db.session.query(Movie).filter(Movie.id == id).one()
                    # Сериализация данных
                    return movie_schema.dump(movie), 200
                # Ошибка в случае если в базе нет фильма по id из запроса
                except Exception as e:
                    return str(e), 404

            def put(self, id: int):  # Замена данных
                # Получение данных из БД по id
                movie = db.session.query(Movie).get(id)
                # Получение параметров фильма из запроса в формате JSON
                red_json = request.json

                # Замена параметров фильма на данные из запроса
                movie.title = red_json.get("title")
                movie.description = red_json.get("description")
                movie.trailer = red_json.get("trailer")
                movie.year = red_json.get("year")
                movie.rating = red_json.get("rating")
                movie.genre_id = red_json.get("genre_id")
                movie.director_id = red_json.get("director_id")

                # Добавление фильма в базу
                db.session.add(movie)
                # Подтверждение изменения
                db.session.commit()
                return "Movie updated", 204

            def patch(self, id: int):  # Частичное обновление данных
                # Получение данных из БД по ID
                movie = db.session.query(Movie).get(id)
                # Получение параметров фильма из запроса в формате JSON
                red_json = request.json

                # Замена параметров фильма на данные из запроса,
                # но только в случае наличия самих этих данных
                if "title" in red_json:
                    movie.title = red_json.get("title")
                if "description" in red_json:
                    movie.description = red_json.get("description")
                if "trailer" in red_json:
                    movie.trailer = red_json.get("trailer")
                if "year" in red_json:
                    movie.year = red_json.get("year")
                if "rating" in red_json:
                    movie.rating = red_json.get("rating")
                if "genre_id" in red_json:
                    movie.genre_id = red_json.get("genre_id")
                if "director_id" in red_json:
                    movie.director_id = red_json.get("director_id")

                # Добавление фильма в базу
                db.session.add(movie)
                # Подтверждение изменения
                db.session.commit()
                return "Movie updated", 204

            def delete(self, id: int):  # Удаление данных
                # Получение данных из БД по ID
                movie = db.session.query(Movie).get(id)

                # Удаление книги из базы
                db.session.delete(movie)
                # Подтверждение изменения
                db.session.commit()
                return "Movie deleted", 204


        # __________________________________________
        # _______________Directors Views______________
        # __________________________________________


        @directors_ns.route('/')  # /directors/
        class DirectorsView(Resource):
            def get(self):  # Получение данных
                # Получение всех режиссеров через обращение к объекту БД
                all_directors = db.session.query(Director).all()
                # Получение списка результатов через метод сериализации
                return directors_schema.dump(all_directors), 200

            def post(self):  # Добавление данных
                # Работа с запросом. Получение данных в формате JSON
                red_json = request.json
                # Распаковка JSON. Десериализация.
                new_director = Director(**red_json)
                # Открытие сессии и сохранение режиссера в БД
                with db.session.begin():
                    db.session.add(new_director)
                # Код 201: Объект создан.
                return "Director created", 201


        @directors_ns.route('/<int:id>')  # /directors/<int:uid>
        class DirectorView(Resource):
            def get(self, id: int):  # Получение данных
                try:
                    # Получение данных из БД по ID
                    director = db.session.query(Director).filter(Director.id == id).one()
                    # Сериализация данных
                    return director_schema.dump(director), 200
                # Ошибка в случае если в базе нет режиссера по ID из запроса
                except Exception as e:
                    return str(e), 404

            def put(self, id: int):  # Замена данных
                # Получение данных из БД по ID
                director = db.session.query(Director).get(id)
                # Получение параметров режиссера из запроса в формате JSON
                red_json = request.json

                # Замена параметров режиссера на данные из запроса
                director.name = red_json.get("name")

                # Добавление режиссера в базу
                db.session.add(director)
                # Подтверждение изменения
                db.session.commit()
                return "Director updated", 204

            def patch(self, id: int):  # Частичное обновление данных
                # Получение данных из БД по ID
                director = db.session.query(Director).get(id)
                # Получение параметров режиссера из запроса в формате JSON
                red_json = request.json

                # Замена параметров режиссера на данные из запроса,
                # но только в случае наличия самих этих данных
                if "name" in red_json:
                    director.name = red_json.get("name")

                # Добавление режиссера в базу
                db.session.add(director)
                # Подтверждение изменения
                db.session.commit()
                return "Director updated", 204

            def delete(self, id: int):  # Удаление данных
                # Получение данных из БД по ID
                director = db.session.query(Director).get(id)

                # Удаление режиссера из базы
                db.session.delete(director)
                # Подтверждение изменения
                db.session.commit()
                return "Director deleted", 204


        # __________________________________________
        # _______________Genres Views______________
        # __________________________________________


        @genres_ns.route('/')  # /genres/
        class GenresView(Resource):
            def get(self):  # Получение данных
                # Получение всех жанров через обращение к объекту БД
                all_genres = db.session.query(Genre).all()
                # Получение списка результатов через метод сериализации
                return genres_schema.dump(all_genres), 200

            def post(self):  # Добавление данных
                # Работа с запросом. Получение данных в формате JSON
                red_json = request.json
                # Распаковка JSON. Десериализация.
                new_genre = Genre(**red_json)
                # Открытие сессии и сохранение жанра в БД
                with db.session.begin():
                    db.session.add(new_genre)
                # Код 201: Объект создан.
                return "Genre created", 201


        @genres_ns.route('/<int:id>')  # /genres/<int:uid>
        class GenreView(Resource):
            def get(self, id: int):  # Получение данных
                try:
                    # Получение данных из БД по ID
                    genre = db.session.query(Genre).filter(Genre.id == id).one()
                    # Сериализация данных
                    return genre_schema.dump(genre), 200
                # Ошибка в случае если в базе нет жанра по ID из запроса
                except Exception as e:
                    return str(e), 404

            def put(self, id: int):  # Замена данных
                # Получение данных из БД по ID
                genre = db.session.query(Genre).get(id)
                # Получение параметров жанра из запроса в формате JSON
                red_json = request.json

                # Замена параметров жанра на данные из запроса
                genre.name = red_json.get("name")

                # Добавление жанра в базу
                db.session.add(genre)
                # Подтверждение изменения
                db.session.commit()
                return "Genre updated", 204

            def patch(self, id: int):  # Частичное обновление данных
                # Получение данных из БД по ID
                genre = db.session.query(Genre).get(id)
                # Получение параметров жанра из запроса в формате JSON
                red_json = request.json

                # Замена параметров жанра на данные из запроса,
                # но только в случае наличия самих этих данных
                if "name" in red_json:
                    genre.name = red_json.get("name")

                # Добавление жанра в базу
                db.session.add(genre)
                # Подтверждение изменения
                db.session.commit()
                return "Genre updated", 204

            def delete(self, id: int):  # Удаление данных
                # Получение данных из БД по ID
                genre = db.session.query(Genre).get(id)

                # Удаление жанра из базы
                db.session.delete(genre)
                # Подтверждение изменения
                db.session.commit()
                return "Genre deleted", 204


        if __name__ == "__main__":
            app.run(debug=False)