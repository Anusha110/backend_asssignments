from datetime import datetime
from .models import Actor, Director, Movie, Cast, Rating
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Max, Min, Avg, Count, Prefetch
from django.db import connection


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


def populate_database(
        actors_list, movies_list, directors_list, movie_rating_list):
    actor_objects = populate_actors(actors_list)
    populate_directors(directors_list)
    movie_objects = populate_movies(movies_list)
    populate_ratings(movie_rating_list, movie_objects)
    populate_cast(movies_list, actor_objects, movie_objects)


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


### Assignment 2

# Task 3
def get_no_of_distinct_movies_actor_acted(actor_id):
    return Movie.objects.all().filter(actors__actor_id=actor_id).distinct().count()


# Task 4
def get_movies_directed_by_director(director_obj):
    return Movie.objects.filter(director=director_obj)


# Task 5
def get_average_rating_of_movie(movie_obj):
    try:
        rating_obj = movie_obj.rating
        sum_of_ratings = rating_obj.rating_one_count + rating_obj.rating_two_count * 2 + rating_obj.rating_three_count * 3 + rating_obj.rating_four_count * 4 + rating_obj.rating_five_count * 5
        number_of_ratings = rating_obj.rating_one_count + rating_obj.rating_two_count + rating_obj.rating_three_count + rating_obj.rating_four_count + rating_obj.rating_five_count
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


### Assignment 3

def get_total_number_of_ratings(movie_obj):
    try:
        rating_obj = movie_obj.rating
        number_of_ratings = rating_obj.rating_one_count + rating_obj.rating_two_count + rating_obj.rating_three_count + rating_obj.rating_four_count + rating_obj.rating_five_count
        return number_of_ratings
    except ObjectDoesNotExist:
        return 0


# Task 1

def get_movies_by_given_movie_objs(movie_objs):
    movie_details_list = []

    for movie_obj in movie_objs:
        movie_details_dict = {}
        movie_details_dict["movie_id"] = movie_obj.movie_id
        movie_details_dict["name"] = movie_obj.name

        cast_list = []
        for cast_obj in movie_obj.cast_set.all():
            cast_dict = {}
            cast_dict["actor"] = {"name": cast_obj.actor.name, "actor_id": cast_obj.actor.actor_id}
            cast_dict['role'] = cast_obj.role
            cast_dict["is_debut_movie"] = cast_obj.is_debut_movie
            cast_list.append(cast_dict)

        movie_details_dict["cast"] = cast_list

        movie_details_dict["box_office_collection_in_crores"] = movie_obj.box_office_collection_in_crores
        movie_details_dict["release_date"] = movie_obj.release_date.strftime("%Y-%m-%d")
        movie_details_dict["director_name"] = movie_obj.director.name
        movie_details_dict["average_rating"] = get_average_rating_of_movie(movie_obj)
        movie_details_dict["total_number_of_ratings"] = get_total_number_of_ratings(movie_obj)
        movie_details_list.append(movie_details_dict)

    return movie_details_list


def get_movies_by_given_movie_names(movie_names):
    movie_objs = Movie.objects.filter(name__in=movie_names).prefetch_related("cast_set__actor").select_related(
        "director", "rating")
    return get_movies_by_given_movie_objs(movie_objs)


# Task 2
def get_movies_released_in_summer_in_given_years():
    return get_movies_by_given_movie_objs(
        Movie.objects.all().filter(release_date__year__range=[2005, 2010], release_date__month__in=[5, 6, 7]))


# Task 3
def get_movie_names_with_actor_name_ending_with_smith():
    movie_names = Movie.objects.filter(
        actors__name__iendswith='smith'
    ).distinct().values_list('name', flat=True)

    return list(movie_names)


# Task 4
def get_movie_names_with_ratings_in_given_range():
    return list(Movie.objects.filter(rating__rating_five_count__range=[1000, 3000]).values_list('name', flat=True))


# Task 5
def get_movie_names_with_ratings_above_given_minimum():
    movie_names = Movie.objects.filter(
        Q(rating__rating_five_count__gte=500) | Q(rating__rating_four_count__gt=1000) | Q(
            rating__rating_three_count__gt=2000) | Q(rating__rating_two_count__gt=4000) | Q(
            rating__rating_one_count__gt=8000), release_date__year__gt=2000).value_list('name', flat=True)
    return list(movie_names)


# Task 6
def get_movie_directors_in_given_year():
    director_names = Director.objects.filter(movie__release_date__year=2000).value_list('name', flat=True)
    return list(director_names)


# Task 7
def get_actor_names_debuted_in_21st_century():
    actor_names = Actor.objects.filter(cast__is_debut_movie=True,
                                       movie__release_date__year__range=[2001, 2100]).value_list('name', flat=True)
    return list(actor_names)


# Task 8
def get_director_names_containing_big_as_well_as_movie_in_may():
    director_names = Director.objects.filter(movie__name__contains="big").filter(
        movie__release_date__year=5).values_list('name', flat=True)
    return list(director_names)


# Task 9
def get_director_names_containing_big_and_movie_in_may():
    director_names = Director.objects.filter(movie__name__contains="big", movie__release_date__year=5).values_list(
        'name', flat=True)
    return list(director_names)


# Task 10
def reset_ratings_for_movies_in_this_year():
    Rating.objects.filter(movie__release_date__year=2000).update(rating_one_count=0, rating_two_count=0,
                                                                 rating_three_count=0, rating_four_count=0,
                                                                 rating_five_count=0)


### Assignment 4

# Task 1
def get_average_box_office_collections():
    avg_box_office_collection = \
        Movie.objects.all().aggregate(avg_box_office_collection=Avg('box_office_collection_in_crores'))[
            'avg_box_office_collection']
    if avg_box_office_collection == None:
        return 0
    return round(avg_box_office_collection, 3)


# Task 2
def get_movies_with_distinct_actors_count():
    return list(Movie.objects.all().annotate(actors_count=Count('actors', distinct=True)))


# Task 3
def get_male_and_female_actors_count_for_each_movie():
    return list(Movie.objects.all().annotate(male_actors_count=Count('actors', filter=Q(actors__gender="MALE")),
                                             female_actors_count=Count('actors', filter=Q(actors__gender="FEMALE"))))


# Task 4
def get_roles_count_for_each_movie():
    return list(Movie.objects.annotate(roles_count=Count('cast__role', distinct=True)))


# Task 5
def get_role_frequency():
    role_frequency_dict = {}
    for role_dict in Cast.objects.values('role').annotate(Count('role')):
        role_frequency_dict[role_dict['role']] = role_dict['role__count']
    return role_frequency_dict


# Task 6
def get_role_frequency_in_order():
    return list(
        Cast.objects.values('role').annotate(roles_count=Count('role')).values_list('role', 'roles_count').order_by(
            '-movie__release_date'))


# Task 7
def get_no_of_movies_and_distinct_roles_for_each_actor():
    return list(Actor.objects.annotate(movies_count=Count('movie', distinct=True),
                                       roles_count=Count('cast__role', distinct=True)))


# Task 8
def get_movies_with_atleast_forty_actors():
    return list(Movie.objects.annotate(actor_count=Count('actors', distinct=True)).filter(actor_count__gte=40))


# Task 9
def get_average_no_of_actors_for_all_movies():
    avg_no_of_actors = Movie.objects.annotate(num_of_actors=Count('actors', distinct=True)).aggregate(
        avg_no_of_actors=Avg('num_of_actors'))['avg_no_of_actors']

    if avg_no_of_actors == None:
        return 0
    return round(avg_no_of_actors, 3)


## Assignment 5

# Task 1
## Implemented in Assigment 2 Task 1

# Task 2
def remove_all_actors_from_given_movie(movie_object):
    Movie.objects.filter(movie=movie_object).actors.clear()


# Task 3
def get_all_rating_objects_for_given_movies(movie_objs):
    return Rating.objects.filter(movie__in=movie_objs)


# Task 4
## Implemented in Assigment 3 Task 1: get_movies_by_given_movie_names()

# Task 5
def get_all_actor_objects_acted_in_given_movies(movie_objs):
    return Actor.objects.filter(movie__in=movie_objs).distinct()


# Task 6
def get_female_cast_details_from_movies_having_more_than_five_female_cast():
    movie_objs = Movie.objects.annotate(female_actor_count=Count('actors', filter=Q(actors__gender="FEMALE"))).filter(
        female_actor_count__gt=0).prefetch_related(
        Prefetch("cast_set", queryset=Cast.objects.filter(actor__gender="FEMALE")), "cast_set__actor").select_related(
        "director", "rating")
    # Doubt (prefetch_related(Prefetch("cast_set__actor") -Related actor object doesn't exist
    return get_movies_by_given_movie_objs(movie_objs)


# Task 7

def get_actor_details_by_given_actor_objs(actor_objs):
    actor_details_list = []

    for actor_obj in actor_objs:
        actor_details_dict = {}
        actor_details_dict["name"] = actor_obj.name
        actor_details_dict["actor_id"] = actor_obj.actor_id
        movies_list = []
        for movie_obj in actor_obj.movie_set.all():
            movie_dict = {}
            movie_dict["movie_id"] = movie_obj.movie_id
            movie_dict["name"] = movie_obj.name

            cast_list = []
            for cast_obj in movie_obj.cast_set.all():
                cast_dict = {}
                cast_dict['role'] = cast_obj.role
                cast_dict["is_debut_movie"] = cast_obj.is_debut_movie
                cast_list.append(cast_dict)

            movie_dict["cast"] = cast_list

            movie_dict["box_office_collection_in_crores"] = movie_obj.box_office_collection_in_crores
            movie_dict["release_date"] = movie_obj.release_date.strftime("%Y-%m-%d")
            movie_dict["director_name"] = movie_obj.director.name
            movie_dict["average_rating"] = get_average_rating_of_movie(movie_obj)
            movie_dict["total_number_of_ratings"] = get_total_number_of_ratings(movie_obj)
            movies_list.append(movie_dict)
        actor_details_dict["movies"] = movies_list
        actor_details_list.append(actor_details_dict)

    return actor_details_list


def get_actor_movies_released_in_year_greater_than_or_equal_to_2000():
    return get_actor_details_by_given_actor_objs(
        Actor.objects.filter(movie__release_date__year__gte=2000).prefetch_related(Prefetch("movie_set",
                                                                                            queryset=Movie.objects.filter(
                                                                                                release_date__year__gte=2000).select_related(
                                                                                                "director", "rating"))))


def reset_ratings_for_movies_in_given_year(year):
    Rating.objects.filter(movie__release_date__year=year).update(rating_one_count=0, rating_two_count=0,
                                                                 rating_three_count=0, rating_four_count=0,
                                                                 rating_five_count=0)
