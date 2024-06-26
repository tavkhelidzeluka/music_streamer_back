from rest_framework import serializers

from music_lib.models import Song, Artist, Album, Playlist


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'


class AlbumSongSerializer(serializers.ModelSerializer):
    artists = ArtistSerializer(many=True, read_only=True)

    class Meta:
        model = Song
        exclude = ['album']


class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    song_set = AlbumSongSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = '__all__'


class SongSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)
    artists = ArtistSerializer(many=True, read_only=True)

    class Meta:
        model = Song
        fields = '__all__'


class SongCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = '__all__'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        # if not request.user.is_superuser:
        self.fields['album'].queryset = Album.objects.filter(artist__user=request.user)
        self.fields['artists'].child_relation.queryset = Artist.objects.filter(user=request.user)


class PlaylistSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Playlist
        fields = '__all__'
