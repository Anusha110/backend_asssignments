from .constants import ReactionTypeEnum
from .models import Post, Comment, Reaction, User, Group, Membership
from django.db.models import Count, Q, F, Prefetch
from datetime import datetime
from .exceptions import InvalidUserException, InvalidPostException, InvalidCommentException, \
    InvalidReactionTypeException, InvalidPostContent, InvalidCommentContent, InvalidReplyContent, \
    UserCannotDeletePostException, InvalidGroupNameException, InvalidMemberException, InvalidGroupException, \
    UserNotInGroupException, UserIsNotAdminException, InvalidOffSetValueException, InvalidLimitSetValueException

# region Validation Functions

def raise_exception_if_invalid_user_id(user_id):
    if not User.objects.filter(id=user_id).exists():
        raise InvalidUserException


def raise_exception_if_invalid_post_id_else_return_post(post_id):
    post = Post.objects.filter(id=post_id)
    if not post.exists():
        raise InvalidPostException
    return post[0]


def raise_exception_if_invalid_comment_id_else_return_comment(comment_id):
    comment = Comment.objects.filter(id=comment_id)
    if not comment.exists():
        raise InvalidCommentException
    return comment[00]


def raise_exception_if_invalid_post_content(post_content):
    if post_content == "":
        raise InvalidPostContent


def raise_exception_if_invalid_comment_content(comment_content):
    if comment_content == "":
        raise InvalidCommentContent


def raise_exception_if_invalid_reply_content(reply_content):
    if reply_content == "":
        raise InvalidReplyContent


def raise_exception_if_invalid_reaction_type(reaction_type):
    if reaction_type.name not in ReactionTypeEnum.__members__:
        raise InvalidReactionTypeException


def raise_exception_if_user_cannot_delete_post(user_id, post):
    if post.posted_by_id != user_id:
        raise UserCannotDeletePostException

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
def create_post(user_id, post_content, group_id=None):
    raise_exception_if_invalid_user_id(user_id)
    raise_exception_if_invalid_post_content(post_content)

    if group_id != None:
        raise_exception_if_invalid_group_id(group_id)
        raise_exception_if_user_not_in_group(user_id, group_id)

    post = Post.objects.create(
        content=post_content,
        posted_at=datetime.now(),
        posted_by_id=user_id,
        group_id=group_id
    )

    return post.id


# Task 3
def create_comment(user_id, post_id, comment_content):
    raise_exception_if_invalid_user_id(user_id)
    raise_exception_if_invalid_post_id_else_return_post(post_id)
    raise_exception_if_invalid_comment_content(comment_content)

    comment = Comment.objects.create(
        content=comment_content,
        commented_at=datetime.now(),
        commented_by_id=user_id,
        post_id=post_id,
    )

    return comment.id


# Task 4
def reply_to_comment(user_id, comment_id, reply_content):

    raise_exception_if_invalid_user_id(user_id)
    comment = raise_exception_if_invalid_comment_id_else_return_comment(comment_id)
    raise_exception_if_invalid_reply_content(reply_content)

    if comment.parent_comment_id is not None:
        comment_id = comment.parent_comment.id

    reply = Comment.objects.create(
        content=reply_content,
        commented_at=datetime.now(),
        commented_by_id=user_id,
        post_id=comment.post.id,
        parent_comment_id=comment_id
    )

    return reply


# Task 5
def react_to_post(user_id, post_id, reaction_type):
    raise_exception_if_invalid_user_id(user_id)
    raise_exception_if_invalid_post_id_else_return_post(post_id)
    raise_exception_if_invalid_reaction_type(reaction_type)

    try:
        reaction = Reaction.objects.get(reacted_by_id=user_id, post_id=post_id)

        if reaction.reaction_type == str(reaction_type):
            reaction.delete()
        else:
            reaction.reaction_type = reaction_type
            reaction.reacted_at = datetime.now()
            reaction.save()
    except:
        Reaction.objects.create(reaction_type=reaction_type, post_id=post_id, reacted_at=datetime.now(),
                                reacted_by_id=user_id)


# Task 6
def react_to_comment(user_id, comment_id, reaction_type):
    raise_exception_if_invalid_user_id(user_id)
    raise_exception_if_invalid_comment_id_else_return_comment(comment_id)
    raise_exception_if_invalid_reaction_type(reaction_type)

    try:
        reaction = Reaction.objects.get(reacted_by_id=user_id, comment_id=comment_id)

        if reaction.reaction_type == str(reaction_type):
            reaction.delete()
        else:
            reaction.reaction_type = reaction_type
            reaction.reacted_at = datetime.now()
            reaction.save()
    except:
        Reaction.objects.create(reaction_type=reaction_type, comment_id=comment_id, reacted_at=datetime.now(),
                                reacted_by_id=user_id)


# Task 7
def get_total_reaction_count():
    return Reaction.objects.all().aggregate(count=Count('id'))


# Task 8
def get_reaction_metrics(post_id):
    # Doubt Changing enum display in output?
    raise_exception_if_invalid_post_id_else_return_post(post_id)
    return dict(Reaction.objects.values_list('reaction_type').annotate(Count('id')).filter(post_id=post_id))


# Task 9
def delete_post(user_id, post_id):
    raise_exception_if_invalid_user_id(user_id)
    post = raise_exception_if_invalid_post_id_else_return_post(post_id)
    raise_exception_if_user_cannot_delete_post(user_id, post)

    post.delete()


# Task 10
def get_posts_with_more_positive_reactions():
    positive_reactions = [ReactionTypeEnum.THUMBS_UP, ReactionTypeEnum.LIT, ReactionTypeEnum.LOVE,
                          ReactionTypeEnum.HAHA, ReactionTypeEnum.WOW]
    negative_reactions = [ReactionTypeEnum.THUMBS_DOWN, ReactionTypeEnum.SAD, ReactionTypeEnum.ANGRY]

    return list(Post.objects.annotate(
        positive_reaction_count=Count('reaction', filter=Q(reaction__reaction_type__in=positive_reactions)),
        negative_reaction_count=Count('reaction', filter=Q(reaction__reaction_type__in=negative_reactions))).filter(
        positive_reaction_count__gt=F('negative_reaction_count')).values_list('id', flat=True))


# Task 11
def get_posts_reacted_by_user(user_id):
    raise_exception_if_invalid_user_id(user_id)
    return list(Reaction.objects.filter(user_id=user_id, post_id__isnull=False).value_list('post_id', flat=True))


# Task 12
def get_reactions_to_post(post_id):
    raise_exception_if_invalid_post_id_else_return_post(post_id)
    reactions = Reaction.objects.filter(post_id=post_id).select_related('reacted_by')

    reaction_list = []

    for reaction in reactions:
        reaction_dict = {}
        reaction_dict["user_id"] = reaction.reacted_by_id
        reaction_dict["name"] = reaction.reacted_by.name
        reaction_dict["profile_pic"] = reaction.reacted_by.profile_pic
        reaction_dict["reaction"] = str(reaction.reaction_type.name)
        reaction_list.append((reaction_dict))

    return reaction_list


# Task 13

def get_comment_reply_details(comment):

    replies_list = []
    for reply in comment.replies.all():
        reply_dict = {
            "comment_id": reply.id,
            "commenter": {
                "user_id": reply.commented_by_id,
                "name": reply.commented_by.name,
                "profile_pic": reply.commented_by.profile_pic
            },
            "commented_at": str(reply.commented_at),
            "comment_content": reply.content,
            "reactions": {
                "count": reply.reaction_set.count(),
                "type": reply.reaction_set.values_list("reaction_type", flat=True)
            }
        }
        replies_list.append(reply_dict)

    return replies_list

def get_post_comment_details(post):

    comments_details_list = []

    for comment in post.comments.all():
        comment_details_dict = {
            "comment_id": comment.id,
            "commenter": {
                "user_id": comment.commented_by_id,
                "name": comment.commented_by.name,
                "profile_pic": comment.commented_by.profile_pic
            },
            "commented_at": str(comment.commented_at),
            "comment_content": comment.content,
            "reactions": {
                "count": comment.reaction_set.count(),
                "type": comment.reaction_set.values_list("reaction_type", flat=True)
            },
            "replies_count": comment.replies.count(),
            "replies": get_comment_reply_details(comment),
        }
        comments_details_list.append(comment_details_dict)

    return comments_details_list

def get_post_details_object(post):

    post_details_dict = {
        "post_id": post.id,
        "posted_by": {
            "name": post.posted_by.name,
            "user_id": post.posted_by_id,
            "profile_pic": post.posted_by.profile_pic
        },
        "posted_at": str(post.posted_at),
        "posted_content": post.content,
        "reactions": {
            "count": post.reaction_set.count(),
            "type": post.reaction_set.values_list("reaction_type", flat=True)
        }
    }

    if post.group == None:
        post_details_dict["group"] = None
    else:
        post_details_dict["group"] = {
            "group_id": post.group.id,
            "name": post.group.name
        }

    post_details_dict["comments"] = get_post_comment_details(post)
    post_details_dict["comments_count"] = post.comments.count()

    return post_details_dict

def get_post(post_id):
    raise_exception_if_invalid_post_id_else_return_post(post_id)

    post = Post.objects.filter(id=post_id).select_related('posted_by', 'group')\
        .prefetch_related("reaction_set",Prefetch("comments",
                                                  queryset=Comment.objects.select_related("commented_by")\
                                                  .prefetch_related("reaction_set", Prefetch("replies",
                                                                                             queryset=Comment.objects.select_related("commented_by").prefetch_related("reaction_set"))))).first()

    return get_post_details_object(post)
    # Doubt: In order to get reactions, its hitting database. Usage of List.

# Task 14
def get_user_posts(user_id):
    raise_exception_if_invalid_user_id(user_id)

    user_posts_details = []
    posts = Post.objects.filter(posted_by_id=user_id) \
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
                                               "reaction_set")))))

    for post in posts:
        user_posts_details.append((get_post_details_object(post)))

    return user_posts_details


# Task 15
def get_replies_for_comment(comment_id):

    raise_exception_if_invalid_comment_id_else_return_comment(comment_id)
    reply_objs = Comment.objects.filter(parent_comment_id=comment_id).select_related("commented_by")

    reply_details_list = []
    for reply_obj in reply_objs:
        reply_details_dict = {
            "comment_id": reply_obj.id,
            "commenter": {
                "user_id": reply_obj.commented_by_id,
                "name": reply_obj.commented_by.name,
                "profile_pic": reply_obj.commented_by.profile_pic
            },
            "commented_at": str(reply_obj.commented_at),
            "comment_content": reply_obj.content
        }
        reply_details_list.append(reply_details_dict)

    return reply_details_list
