import os
import re

import rest_framework.permissions
from django.http import FileResponse, Http404, HttpResponse
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from music_lib.models import Song, Artist, Album, Playlist
from music_lib.serializers import SongSerializer, SongCreateSerializer, ArtistSerializer, AlbumSerializer, \
    PlaylistSerializer


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

    @action(detail=True, methods=['get'])
    def stream(self, request, pk=None):
        # Assuming 'pk' is the filename or part of the path
        song = get_object_or_404(Song, pk=pk)
        file_path = song.file.path

        if not os.path.exists(file_path):
            raise Http404("Audio file does not exist.")

        range_header = request.META.get('HTTP_RANGE', None)
        file_size = os.path.getsize(file_path)
        if not range_header:
            # No range header means send the entire file
            return FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')

        # Extract range start and end from Range header (e.g., "bytes=0-499")
        start, end = 0, file_size - 1
        if range_header:
            range_match = re.search(r'bytes=(\d+)-(\d*)', range_header)
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else end

        if start > file_size or end < start:
            return HttpResponse(status=416)  # Range Not Satisfiable

        resp = HttpResponse(content_type='audio/mpeg', status=206)
        resp['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        resp['Accept-Ranges'] = 'bytes'
        resp['Content-Length'] = str(end - start + 1)
        with open(file_path, 'rb') as f:
            f.seek(start)
            resp.write(f.read(end - start + 1))
        return resp


class ArtistAPIViewSet(ModelViewSet):
    http_method_names = ['get', 'list']
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()


class AlbumAPIViewSet(ModelViewSet):
    http_method_names = ['get', 'list']
    serializer_class = AlbumSerializer
    queryset = Album.objects.all()


class PlaylistAPIViewSet(ModelViewSet):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    serializer_class = PlaylistSerializer

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def add_song(self, request: Request, pk: int) -> Response:
        playlist = get_object_or_404(Playlist, pk=pk)
        song = get_object_or_404(Song, pk=request.POST.get('song_id'))

        if playlist.songs.filter(song=song).exists():
            raise Http404()

        playlist.songs.add(song)
        return Response(data={"data": "ok"})
