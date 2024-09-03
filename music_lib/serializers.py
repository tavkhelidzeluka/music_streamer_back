from pathlib import Path

import audioread
from rest_framework import serializers

from music_lib.models import Song, Artist, Album, Playlist


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'


class AlbumSongSerializer(serializers.ModelSerializer):
    artists = ArtistSerializer(many=True, read_only=True)
    is_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Song
        exclude = ['album']


class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    song_set = AlbumSongSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = '__all__'


class SongAlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)

    class Meta:
        model = Album
        fields = '__all__'


class SongSerializer(serializers.ModelSerializer):
    album = SongAlbumSerializer(read_only=True)
    artists = ArtistSerializer(many=True, read_only=True)
    is_liked = serializers.BooleanField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Song
        exclude = ['file']


class SongCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        exclude = ['play_count', 'duration']

    def create(self, validated_data):
        with audioread.audio_open(validated_data['file'].temporary_file_path()) as f:
            duration = f.duration
            validated_data['duration'] = duration
        return super().create(validated_data)


class SongNameFindSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['name']


class PlaylistSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Playlist
        fields = '__all__'


class PlaylistBareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['name']


class PlaylistCreateSerializer(serializers.ModelSerializer):
    songs = serializers.PrimaryKeyRelatedField(many=True, queryset=Song.objects.all())

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'songs']

    def create(self, validated_data):
        songs = validated_data.pop('songs')
        playlist = Playlist.objects.create(**validated_data)
        playlist.songs.add(*songs)
        return playlist


class UpdatePlaylistsSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    song = serializers.PrimaryKeyRelatedField(queryset=Song.objects.all())

    class Meta:
        model = Playlist
        fields = ['ids', 'song']

    def validate_ids(self, value):
        if not all(isinstance(id, int) for id in value):
            raise serializers.ValidationError("All IDs must be integers.")
        return value
