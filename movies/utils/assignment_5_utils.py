from assignments.movies.models import Actor, Director, Movie, Cast, Rating
from django.db.models import Q, Count, Prefetch
from .assignment_3_utils import get_movies_by_given_movie_objs
from .assignment_2_utils import get_average_rating_of_movie, get_total_number_of_ratings


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
def get_cast_details_list(movie_obj):
    cast_list = []
    for cast_obj in movie_obj.cast_set.all():
        cast_dict = {}
        cast_dict['role'] = cast_obj.role
        cast_dict["is_debut_movie"] = cast_obj.is_debut_movie
        cast_list.append(cast_dict)
    return  cast_list

def get_movie_details_dict(movie_obj):
    movie_dict = {}
    movie_dict["movie_id"] = movie_obj.movie_id
    movie_dict["name"] = movie_obj.name
    movie_dict["cast"] = get_cast_details_list(movie_obj)
    movie_dict["box_office_collection_in_crores"] = movie_obj.box_office_collection_in_crores
    movie_dict["release_date"] = movie_obj.release_date.strftime("%Y-%m-%d")
    movie_dict["director_name"] = movie_obj.director.name
    movie_dict["average_rating"] = get_average_rating_of_movie(movie_obj)
    movie_dict["total_number_of_ratings"] = get_total_number_of_ratings(movie_obj)


def get_actor_details_by_given_actor_objs(actor_objs):
    actor_details_list = []

    for actor_obj in actor_objs:

        actor_details_dict = {}
        actor_details_dict["name"] = actor_obj.name
        actor_details_dict["actor_id"] = actor_obj.actor_id

        movies_list = []
        for movie_obj in actor_obj.movie_set.all():
            movies_list.append(get_movie_details_dict(movie_obj))

        actor_details_dict["movies"] = movies_list
        actor_details_list.append(actor_details_dict)

    return actor_details_list


def get_actor_movies_released_in_year_greater_than_or_equal_to_2000():
    return get_actor_details_by_given_actor_objs(
        Actor.objects.filter(movie__release_date__year__gte=2000) \
            .prefetch_related(Prefetch("movie_set", queryset=Movie.objects.filter(release_date__year__gte=2000) \
                                       .select_related("director", "rating"))))


# Task 8
def reset_ratings_for_movies_in_given_year(year):
    Rating.objects.filter(movie__release_date__year=year).update(rating_one_count=0, rating_two_count=0,
                                                                 rating_three_count=0, rating_four_count=0,
                                                                 rating_five_count=0)
