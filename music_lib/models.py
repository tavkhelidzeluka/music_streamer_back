from pathlib import Path

from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()
    is_verified = models.BooleanField(default=False)


class Album(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    cover = models.ImageField()


class Song(models.Model):
    artists = models.ManyToManyField(Artist)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    file = models.FileField()
    is_available = models.BooleanField(default=True)

