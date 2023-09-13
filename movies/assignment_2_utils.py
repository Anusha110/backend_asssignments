from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Max, Min, Avg, Count, Prefetch
from django.db import connection
from .models import Actor, Director, Movie, Rating, Cast




# Task 2

def get_movie_object(movie_id, movie_objects):
    for movie in movie_objects:
        if movie_id == movie.movie_id:
            return movie


def get_director_object(director_name, director_objects):
    for director in director_objects:
        if director_name == director.name:
            return director


def get_actor_object(actor_id, actor_objects):
    for actor in actor_objects:
        if actor_id == actor.actor_id:
            return actor


def populate_actors(actors_list):
    actors_objects = Actor.objects.bulk_create(
        [Actor(actor_id=actor['actor_id'], name=actor['name'], gender=actor['gender']) for actor in actors_list])
    return actors_objects


def populate_directors(directors_list):
    Director.objects.bulk_create([Director(name=director_name) for director_name in directors_list])


def populate_movies(movies_list):

    movies_list_for_bulk_creation = []
    director_names = [movie["director_name"] for movie in movies_list]
    director_objects = Director.objects.filter(name__in=director_names)
    Director_objects = Director.objects.filter(name__in=director_names)

    for movie in movies_list:
        director_obj = get_director_object(movie["director_name"], director_objects)
        movies_list_for_bulk_creation.append(
            Movie(
                movie_id=movie['movie_id'],
                name=movie['name'],
                box_office_collection_in_crores=movie['box_office_collection_in_crores'],
                release_date=datetime.strptime(movie['release_date'], "%Y-%m-%d"),
                director=director_obj)
        )

    movie_objects = Movie.objects.bulk_create(movies_list_for_bulk_creation)
    return movie_objects


def populate_ratings(movie_ratings_list, movie_objects):
    ratings_list_for_bulk_creation = []
    for movie_rating in movie_ratings_list:
        movie_obj = get_movie_object(movie_rating["movie_id"], movie_objects)
        ratings_list_for_bulk_creation.append(
            Rating(movie=movie_obj,
                   rating_one_count=movie_rating["rating_one_count"],
                   rating_two_count=movie_rating["rating_two_count"],
                   rating_three_count=movie_rating["rating_three_count"],
                   rating_four_count=movie_rating["rating_four_count"],
                   rating_five_count=movie_rating["rating_five_count"],
                   ))

    Rating.objects.bulk_create(ratings_list_for_bulk_creation)


def populate_cast(movies_list, actor_objects, movie_objects):
    cast_list = []

    for movie in movies_list:

        movie_obj = get_movie_object(movie["movie_id"], movie_objects)

        for actor in movie["actors"]:
            actor_obj = get_actor_object(actor["actor_id"], actor_objects)
            is_debut_movie = actor["is_debut_movie"] == True
            cast_list.append(Cast(actor=actor_obj, movie=movie_obj, role=actor["role"],
                                  is_debut_movie=is_debut_movie))

    Cast.objects.bulk_create(cast_list)

def populate_database(
        actors_list, movies_list, directors_list, movie_rating_list):

    actor_objects = populate_actors(actors_list)
    populate_directors(directors_list)
    movie_objects = populate_movies(movies_list)
    populate_ratings(movie_rating_list, movie_objects)
    populate_cast(movies_list, actor_objects, movie_objects)


def populate_database_with_fixture_data():
    # TODO: Move fixture data to appropriate file
    actor_list = [
        {
            "actor_id": "actor_1",
            "name": "Actor 1",
            "gender": "FEMALE"
        },
        {
            "actor_id": "actor_2",
            "name": "Actor 2",
            "gender": "MALE"
        },
        {
            "actor_id": "actor_3",
            "name": "Actor 3",
            "gender": "FEMALE"
        },
        {
            "actor_id": "actor_4",
            "name": "Actor 4",
            "gender": "FEMALE"
        }
    ]

    movies_list = [
        {
            "movie_id": "movie_1",
            "name": "Movie 1",
            "actors": [
                {
                    "actor_id": "actor_2",
                    "role": "hero",
                    "is_debut_movie": True
                }
            ],
            "box_office_collection_in_crores": "21.3",
            "release_date": "2018-3-3",
            "director_name": "Director 1"
        },
        {
            "movie_id": "movie_2",
            "name": "Movie 2",
            "actors": [
                {
                    "actor_id": "actor_1",
                    "role": "hero",
                    "is_debut_movie": False
                }
            ],
            "box_office_collection_in_crores": "12.3",
            "release_date": "2020-3-3",
            "director_name": "Director 2"
        },
        {
            "movie_id": "movie_3",
            "name": "Movie 3",
            "actors": [
                {
                    "actor_id": "actor_2",
                    "role": "hero",
                    "is_debut_movie": False
                },
                {
                    "actor_id": "actor_3",
                    "role": "heroine",
                    "is_debut_movie": True
                }
            ],
            "box_office_collection_in_crores": "75.3",
            "release_date": "2022-3-3",
            "director_name": "Director 1"
        },
        {
            "movie_id": "movie_4",
            "name": "Movie 4",
            "actors": [
                {
                    "actor_id": "actor_1",
                    "role": "villain",
                    "is_debut_movie": True
                },
                {
                    "actor_id": "actor_4",
                    "role": "hero",
                    "is_debut_movie": False
                },
                {
                    "actor_id": "actor_2",
                    "role": "heroine",
                    "is_debut_movie": False
                },
            ],
            "box_office_collection_in_crores": "54.3",
            "release_date": "2019-1-3",
            "director_name": "Director 3"
        }
    ]

    directors_list = [
        "Director 1",
        "Director 2",
        "Director 3"
    ]

    movie_rating_list = [
        {
            "movie_id": "movie_1",
            "rating_one_count": 3,
            "rating_two_count": 4,
            "rating_three_count": 7,
            "rating_four_count": 9,
            "rating_five_count": 2
        },
        {
            "movie_id": "movie_2",
            "rating_one_count": 1,
            "rating_two_count": 8,
            "rating_three_count": 9,
            "rating_four_count": 15,
            "rating_five_count": 6
        },
        {
            "movie_id": "movie_3",
            "rating_one_count": 14,
            "rating_two_count": 4,
            "rating_three_count": 2,
            "rating_four_count": 2,
            "rating_five_count": 1
        },
        {
            "movie_id": "movie_4",
            "rating_one_count": 5,
            "rating_two_count": 7,
            "rating_three_count": 9,
            "rating_four_count": 3,
            "rating_five_count": 3
        }
    ]

    populate_database(actor_list, movies_list, directors_list, movie_rating_list)


# Task 3
def get_no_of_distinct_movies_actor_acted(actor_id):
    return Movie.objects.all().filter(actors__actor_id=actor_id).distinct().count()


# Task 4
def get_movies_directed_by_director(director_obj):
    return Movie.objects.filter(director=director_obj)


# Task 5

def get_total_number_of_ratings(movie_obj):
    try:
        rating_obj = movie_obj.rating
        number_of_ratings = rating_obj.rating_one_count + rating_obj.rating_two_count + rating_obj.rating_three_count + rating_obj.rating_four_count + rating_obj.rating_five_count
        return number_of_ratings
    except ObjectDoesNotExist:
        return 0

def get_average_rating_of_movie(movie_obj):
    try:
        rating_obj = movie_obj.rating
        sum_of_ratings = rating_obj.rating_one_count + rating_obj.rating_two_count * 2 + rating_obj.rating_three_count * 3 + rating_obj.rating_four_count * 4 + rating_obj.rating_five_count * 5
        number_of_ratings = get_total_number_of_ratings(movie_obj)
        return sum_of_ratings / number_of_ratings
    except ObjectDoesNotExist:
        return 0


# Task 6
def delete_movie_rating(movie_obj):
    Rating.objects.filter(movie=movie_obj).delete()


# Task 7
def get_all_actor_objects_acted_in_given_movies(movie_objs):
    return Actor.objects.filter(movie__in=movie_objs).distinct()


# Task 8
def update_director_for_given_movie(movie_obj, director_obj):
    movie_obj.director = director_obj
    movie_obj.save()


# Task 9
def get_distinct_movies_acted_by_actor_whose_name_contains_john():
    return Movie.objects.filter(actors__name__contains="john").distinct()


# Task 10
def remove_all_actors_from_given_movie(movie_obj):
    movie_obj.actors.clear()


# Task 11
def get_all_rating_objects_for_given_movies(movie_objs):
    return Rating.objects.filter(movie__in=movie_objs)

