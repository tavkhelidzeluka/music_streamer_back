from pathlib import Path

from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()
    is_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Album(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    cover = models.ImageField()

    def __str__(self) -> str:
        return self.title


class Song(models.Model):
    artists = models.ManyToManyField(Artist)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    file = models.FileField()
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

