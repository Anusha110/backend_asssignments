from django.db import models

from .constants import ReactionType


class User(models.Model):
    name = models.CharField(max_length=100)
    profile_pic = models.CharField(max_length=150)


class Post(models.Model):
    content = models.CharField(max_length=1000)
    posted_at = models.DateTimeField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")


class Comment(models.Model):
    content = models.CharField(max_length=1000)
    commented_at = models.DateTimeField()
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent_comment = models.ForeignKey("self", on_delete=models.CASCADE, null=True, related_name="replies")


class Reaction(models.Model):
    reaction_type = models.CharField(max_length=100, choices=ReactionType.choices())
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, related_name="post_reactions")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, related_name="comment_reactions")
    reacted_at = models.DateTimeField()
    reacted_by = models.ForeignKey(User, on_delete=models.CASCADE)
