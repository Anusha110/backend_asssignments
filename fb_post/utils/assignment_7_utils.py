from assignments.fb_post.models import Post, Comment, Reaction, User, Membership, Group
from django.db.models import Count, F, Prefetch
from assignments.fb_post.exceptions import InvalidGroupNameException, InvalidMemberException, InvalidGroupException, \
    UserNotInGroupException, UserIsNotAdminException, InvalidOffSetValueException, InvalidLimitSetValueException
from .assignment_6_utils import raise_exception_if_invalid_user_id, get_post_details_object


# region Validation Functions

def raise_exception_if_invalid_group_name(group_name):
    if (group_name == ""):
        raise InvalidGroupNameException


def raise_exception_if_invalid_member_ids(member_ids):
    user_ids = list(User.objects.values_list("id", flat=True))

    for member_id in member_ids:
        if member_id not in user_ids:
            raise InvalidMemberException


def raise_exception_if_invalid_group_id(group_id):
    if not Group.objects.filter(id=group_id).exists():
        raise InvalidGroupException


def raise_exception_if_user_not_in_group(user_id, group_id):
    if not Membership.objects.filter(group_id=group_id, member_id=user_id).exists():
        raise UserNotInGroupException


def raise_exception_if_user_not_admin(user_id, group_id):
    membership = Membership.objects.get(group_id=group_id, member_id=user_id)
    if membership.is_admin == False:
        raise UserIsNotAdminException


def raise_exception_if_invalid_offset_value(offset):
    if offset < 0:
        raise InvalidOffSetValueException


def raise_exception_if_invalid_limit_value(limit):
    if limit <= 0:
        raise InvalidLimitSetValueException


# endregion

# Task 2
def create_group(user_id, name, member_ids):
    raise_exception_if_invalid_user_id(user_id)
    raise_exception_if_invalid_group_name(name)
    raise_exception_if_invalid_member_ids(member_ids)

    group = Group.objects.create(name=name)

    member_ids = list(set(member_ids))  # unique member Ids
    members_list = []

    for member_id in member_ids:
        members_list.append(Membership(group_id=group.id, member_id=member_id))

    members_list.append(Membership(group_id=group.id, member_id=user_id, is_admin=True))

    Membership.objects.bulk_create(members_list)

    return group.id


# Task 3
def add_member_to_group(user_id, new_member_id, group_id):
    raise_exception_if_invalid_user_id(user_id)
    raise_exception_if_invalid_member_ids([new_member_id])
    raise_exception_if_invalid_group_id(group_id)
    raise_exception_if_user_not_in_group(user_id, group_id)
    raise_exception_if_user_not_admin(user_id, group_id)

    if Membership.objects.filter(group_id=group_id, member_id=new_member_id).exists():
        pass
    else:
        Membership.objects.create(group_id=group_id, member_id=new_member_id)


# Task 4
def remove_member_from_group(user_id, member_id, group_id):
    raise_exception_if_invalid_user_id(user_id)
    raise_exception_if_invalid_member_ids([member_id])
    raise_exception_if_invalid_group_id(group_id)
    raise_exception_if_user_not_in_group(user_id, group_id)
    raise_exception_if_user_not_in_group(member_id, group_id)
    raise_exception_if_user_not_admin(user_id, group_id)

    Membership.objects.get(group_id=group_id, member_id=member_id).delete()


# Task 5
def make_member_as_admin(user_id, member_id, group_id):
    raise_exception_if_invalid_user_id(user_id)
    raise_exception_if_invalid_member_ids([member_id])
    raise_exception_if_invalid_group_id(group_id)
    raise_exception_if_user_not_in_group(user_id, group_id)
    raise_exception_if_user_not_in_group(member_id, group_id)
    raise_exception_if_user_not_admin(user_id, group_id)

    membership_obj = Membership.objects.get(group_id=group_id, member_id=member_id)

    if membership_obj.is_admin is False:
        membership_obj.is_admin = True
        membership_obj.save()


# Task 6
# Added logic to existing create_post() function as specified

# Task 7
def get_group_feed(user_id, group_id, offset, limit):

    raise_exception_if_invalid_user_id(user_id)
    raise_exception_if_invalid_group_id(group_id)
    raise_exception_if_user_not_in_group(user_id, group_id)
    raise_exception_if_invalid_offset_value(offset)
    raise_exception_if_invalid_limit_value(limit)

    posts = Post.objects.filter(group_id=group_id) \
                .select_related('posted_by', 'group') \
                .prefetch_related("reaction_set",
                                  Prefetch("comments",
                                           queryset=Comment.objects.select_related(
                                               "commented_by").prefetch_related(
                                               "reaction_set",
                                               Prefetch(
                                                   "replies",
                                                   queryset=Comment.objects.select_related(
                                                       "commented_by", ).prefetch_related(
                                                       "reaction_set"))))) \
                .order_by('-posted_by')[offset:offset + limit]

    group_feed = []
    for post in posts:
        group_feed.append(get_post_details_object(post))

    return group_feed


# Task 8
def get_posts_with_more_comments_than_reactions():
    post_ids = Post.objects.annotate(number_of_comments=Count('comments', distinct=True),
                                     number_of_reactions=Count('reaction', distinct=True)).filter(
        number_of_comments__gt=F('number_of_reactions')).values_list('id', flat=True)

    return list(post_ids)


# Task 9
# Updated exiting get_user_posts function as specified

# Task 10
def get_silent_group_members(group_id):
    raise_exception_if_invalid_group_id(group_id)
    return list(User.objects.exclude(posts__group_id=group_id).values_list('id', flat=True))


