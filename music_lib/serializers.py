from rest_framework import serializers

from music_lib.models import Song, Artist, Album


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'


class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)

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

