from django.db import models

from .constants import ReactionTypeEnum


class User(models.Model):
    name = models.CharField(max_length=100)
    profile_pic = models.URLField()

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField("User", through="Membership")

class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

class Post(models.Model):
    content = models.CharField(max_length=1000)
    posted_at = models.DateTimeField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)

class Comment(models.Model):
    content = models.CharField(max_length=1000)
    commented_at = models.DateTimeField()
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent_comment = models.ForeignKey("self", on_delete=models.CASCADE, null=True, related_name="replies")


class Reaction(models.Model):
    reaction_type = models.CharField(max_length=100, choices=ReactionTypeEnum.choices())
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    reacted_at = models.DateTimeField()
    reacted_by = models.ForeignKey(User, on_delete=models.CASCADE)

