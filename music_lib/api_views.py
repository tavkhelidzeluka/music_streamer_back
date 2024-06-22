from rest_framework.viewsets import ModelViewSet

from music_lib.models import Song, Artist, Album
from music_lib.serializers import SongSerializer, SongCreateSerializer, ArtistSerializer, AlbumSerializer


class MultiSerializersModelViewSet(ModelViewSet):
    serializer_classes = {}

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action) or self.serializer_classes['default']


class SongAPIViewSet(MultiSerializersModelViewSet):
    serializer_classes = {
        'create': SongCreateSerializer,
        'default': SongSerializer
    }
    queryset = Song.objects.all()


class ArtistAPIViewSet(ModelViewSet):
    http_method_names = ['get', 'list']
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()


class AlbumAPIViewSet(ModelViewSet):
    http_method_names = ['get', 'list']
    serializer_class = AlbumSerializer
    queryset = Album.objects.all()
