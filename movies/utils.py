from datetime import datetime

from models import Actor, Director, Movie, Cast, Rating


def populate_database(
        actors_list, movies_list, directors_list, movie_rating_list):
    """
    :param actors_list:[
        {
            "actor_id": "actor_1",
            "name": "Actor 1"
        }
    ]
    :param movies_list: [
        {
            "movie_id": "movie_1",
            "name": "Movie 1",
            "actors": [
                {
                    "actor_id": "actor_1",
                    "role": "hero",
                    "is_debut_movie": False
                }
            ],
            "box_office_collection_in_crores": "12.3",
            "release_date": "2020-3-3",
            "director_name": "Director 1"
        }
    ]
    :param directors_list: [
        "Director 1"
    ]
    :param movie_rating_list: [
        {
            "movie_id": "movie_1",
            "rating_one_count": 4,
            "rating_two_count": 4,
            "rating_three_count": 4,
            "rating_four_count": 4,
            "rating_five_count": 4
        }
    ]
    """


def populate_actors(actors_list):
    actors = Actor.objects.bulk_create([Actor(actor_id=actor['actor_id'], name=actor['name']) for actor in actors_list])
    return actors

def populate_directors(directors_list):
    directors = Director.objects.bulk_create([Director(name=director_name) for director_name in directors_list])


def populate_movies(movies_list, director_objects, actor_objects):
    movies_list_for_creation = []
    for movie in movies_list:

        actor_obj = get_actor_object(movie['actor_id'], actor_objects)
        director_obj = get_director_object(director_objects, movie["director_name"])

        movies_list_for_creation.append(
            Movie(
                movie_id=movie['movie_id'],
                name=movie['name'],
                box_office_collection_in_crores=movie['box_office_collection_in_crores'],
                #actors=populate_actors(movie['actors']),
                release_date=datetime.strptime(movie['release_date'], "%Y-%m-%d"),
                director=director_obj
            ))


"""
def populate_cast(actors_list, actor_objects, movie_obj):

    cast_list= []

    for actor in actors_list:
        actor_obj = get_actor_object(actor["actor_id"], actor_objects)
        cast_list.append(Cast(actor=actor_obj), movie=movie_obj, role=actor["role"], is_debut_movie=actpr)
"""

def get_director_object(director_name, director_objects):
    for director in director_objects:
        if director_name == director.name:
            return director

def get_actor_object(actor_id, actor_objects):
    for actor in actor_objects:
        if actor_id == actor.actor_id:
            return actor

