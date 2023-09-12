from assignments.movies.models import Actor, Director, Movie, Rating
from django.db.models import Q
from .assignment_2_utils import get_average_rating_of_movie, get_total_number_of_ratings


# Task 1

def get_cast_details_list(movie_obj):
    cast_details_list = []
    for cast_obj in movie_obj.cast_set.all():
        cast_dict = {}
        cast_dict["actor"] = {"name": cast_obj.actor.name, "actor_id": cast_obj.actor.actor_id}
        cast_dict['role'] = cast_obj.role
        cast_dict["is_debut_movie"] = cast_obj.is_debut_movie
        cast_details_list.append(cast_dict)
    return cast_details_list


def get_movies_by_given_movie_objs(movie_objs):
    movie_details_list = []

    for movie_obj in movie_objs:
        movie_details_dict = {}
        movie_details_dict["movie_id"] = movie_obj.movie_id
        movie_details_dict["name"] = movie_obj.name
        movie_details_dict["cast"] = get_cast_details_list(movie_obj)
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
