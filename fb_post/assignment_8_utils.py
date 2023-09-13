from .models import Post, Comment, User
from django.db.models import Prefetch
from .assignment_6_utils import raise_exception_if_invalid_user_id, raise_exception_if_invalid_group_id, \
    raise_exception_if_user_not_in_group, \
    raise_exception_if_invalid_offset_value, raise_exception_if_invalid_limit_value, \
    get_post_details_object


# Interactor

def get_user_post(user_id):
    raise_exception_if_invalid_user_id(user_id)
    users_posts_dict = get_user_post_dict(user_id)  # Call Storage function
    return users_posts_dict

def get_group_feed(user_id, group_id, offset, limit):

    raise_exception_if_invalid_user_id(user_id)
    raise_exception_if_invalid_group_id(group_id)
    raise_exception_if_user_not_in_group(user_id, group_id)
    raise_exception_if_invalid_offset_value(offset)
    raise_exception_if_invalid_limit_value(limit)

    group_feed_dict = get_group_feed_dict(group_id, offset, limit)  # Call Storage function
    return group_feed_dict




# Storage

def get_comment_dict(comment):
    comment_dict = {
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
        }
    }

    return comment_dict


def get_detailed_reply_objects(replies):
    replies_list = []
    for reply in replies:
        reply_dict = get_comment_dict(reply)
        replies_list.append(reply_dict)

    return replies_list


def get_detailed_comment_objects(comments):
    comments_details_list = []

    for comment in comments:
        comment_dict = get_comment_dict(comment)
        comment_dict["replies_count"] = comment.replies.count()
        comment_dict["replies"] = get_detailed_reply_objects(comment.replies.all())
        comments_details_list.append(comment_dict)

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
            "count": post.reaction_set.count(),  # TODO: should add field to model: reaction_count
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

    post_details_dict["comments"] = get_comments_on_post(post)
    post_details_dict["comments_count"] = post.comments.count()  # TODO: should add field to model: comment_count

    return post_details_dict

def get_comments_on_post(post):
    queryset = Comment.objects.prefetch_related("reaction_set", "commented_by")
    comments = post.comments.prefetch_related("commented_by", "reaction_set", Prefetch("replies", queryset=queryset))
    return get_detailed_comment_objects(comments)

def get_user_post_dict(user_id):
    user_posts_details = []
    posts = Post.objects.filter(posted_by_id=user_id).prefetch_related("posted_by", "group", "reaction_set", "comments")

    for post in posts:
        user_posts_details.append(get_post_details_object(post))

    return user_posts_details


def get_group_feed_dict(group_id, offset, limit):
    posts = Post.objects.filter(group_id=group_id).prefetch_related("posted_by", "group", "reaction_set", "comments")\
                                                .order_by('-posted_by')[offset:offset + limit]
    group_post_details = []

    for post in posts:
        group_post_details.append(get_post_details_object(post))

    return group_post_details
