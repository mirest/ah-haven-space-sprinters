from django.db import models
from ..profiles.models import Profile
from ..articles.models import Article

# Create your models here.


class Comment(models.Model):
    """this model defines how comment table will stored in database"""

    comment_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment_on_text = models.TextField(blank=False, null=True, default=None)
    comment_on_start = models.PositiveIntegerField(null=True, blank=True)
    comment_on_end = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        """make sure comments are arranged in order of time created"""

        ordering = ['created_at']

    def __str__(self):
        """return a string of the comment body"""

        return self.comment_body


class Reply(models.Model):
    """this model defines how reply table will be stored in the database"""

    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        """make sure replies are arranged in order of time created"""
        ordering = ['created_at']

    def __str__(self):
        return self.body


class CommentLike(models.Model):
    """
    Handles liking of a specific user by an authenticated user
    """
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    like_status = models.BooleanField()
    liked_by = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return "like by  {}".format(self.liked_by)
