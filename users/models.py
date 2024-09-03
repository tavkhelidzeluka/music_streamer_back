from django.db import models
from django.contrib.auth.models import AbstractUser
from music_lib.models import Song


class User(AbstractUser):
    liked_songs = models.ManyToManyField(Song, blank=True, related_name='liked_by')
