from .models import Actor, Movie, Cast
from django.db.models import Q, Avg, Count


# Task 1
def get_average_box_office_collections():
    avg_box_office_collection = \
        Movie.objects.all().aggregate(avg_box_office_collection=Avg('box_office_collection_in_crores'))[
            'avg_box_office_collection']

    if avg_box_office_collection is None:
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
    role_frequency = Cast.objects.values('role').annotate(roles_count=Count('role')).values_list('role', 'roles_count').order_by(
            '-movie__release_date')
    return list(role_frequency)


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

    if avg_no_of_actors is None:
        return 0
    return round(avg_no_of_actors, 3)
