from rest_framework.viewsets import ModelViewSet

from music_lib.models import Song, Artist, Album
from music_lib.serializers import SongSerializer, ArtistSerializer, AlbumSerializer


class SongAPIViewSet(ModelViewSet):
    serializer_class = SongSerializer
    queryset = Song.objects.all()


class ArtistAPIViewSet(ModelViewSet):
    http_method_names = ['get', 'list']
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()


class AlbumAPIViewSet(ModelViewSet):
    http_method_names = ['get', 'list']
    serializer_class = AlbumSerializer
    queryset = Album.objects.all()
