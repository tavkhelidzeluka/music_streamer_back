from pathlib import Path

from django.conf import settings
from django.db import models


def generate_song_file_path(instance: 'Song', filename: str) -> str:
    return f'album/{instance.album.title}/songs/{filename}'


def generate_cover_image_path(instance: 'Album', filename: str) -> str:
    return f'album/{instance.title}/{filename}'


def upload_playlist_cover_to(instance: 'Playlist', filename: str) -> str:
    return f'users/playlists/{instance.name}/{filename}'


class Artist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    bio = models.TextField()
    is_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Album(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    cover = models.ImageField(upload_to=generate_cover_image_path)

    def __str__(self) -> str:
        return self.title


class Song(models.Model):
    artists = models.ManyToManyField(Artist)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=generate_song_file_path)
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Playlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song, blank=True)

    cover = models.ImageField(upload_to=upload_playlist_cover_to, null=True, blank=True)
    name = models.CharField(max_length=255)
