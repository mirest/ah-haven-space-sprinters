from django.db import models
from authors.apps.profiles.models import Profile
from authors.apps.articles.models import Article
from authors.apps.comments.models import Comment
from authors.apps.authentication.models import User
from authors.apps.profiles.models import Follower
from django.db.models.signals import post_save
from background_task import background
from django.utils import timezone


class Notification(models.Model):

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    notification_message = models.TextField()
    notified = models.ManyToManyField(
        User, related_name='notified')
    created_at = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name='read')
    email_sent = models.BooleanField(default=False)
    classification = models.TextField(default="article")

    class Meta:

        ordering = ['-created_at']

    def __str__(self):
        return self.notification_message


def send_follower_notification_reciever(sender, instance, created, **kwargs):
    user = User.objects.get(id=instance.author.id)
    if created:
        message = (user.username +
                   "has published an article titled" + instance.title)
        send_follower_notification(instance.author, message, instance)


def send_follower_notification(author, notification, article):

    authorlist = Follower.objects.filter(
        follow=author).values_list(
        'author', flat=True)
    followers_list = User.objects.filter(
        username__in=[author for author in authorlist])

    if followers_list:
        create_notification = Notification(
            notification_message=notification,
            classification="article", article=article)
        create_notification.save()
        for follower in followers_list:
            if follower.profile.app_notification_enabled is True:
                create_notification.notified.add(follower.id)


post_save.connect(send_follower_notification_reciever, sender=Article)


class CommentNotification(models.Model):

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    notification_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.ManyToManyField(
        User, related_name='comment_notified', blank=True)
    read_by = models.ManyToManyField(User, related_name='comment_read')
    email_sent = models.BooleanField(default=False)
    classification = models.TextField(default="comment")

    class Meta:

        ordering = ['created_at']

    def __str__(self):
        return self.notification_message


def send_comment_notification_receiver(sender, instance, created, **kwargs):
    user = User.objects.get(id=instance.author.id)
    if created:
        message = (user.username +
                   " commented on" + instance.article.title)

        article_id = instance.article.id
