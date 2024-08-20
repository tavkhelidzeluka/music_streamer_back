import os
import re

import rest_framework.permissions
from django.db.models import OuterRef, Exists, Prefetch, BooleanField, Value
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from music_lib.filters import SongFilter
from music_lib.models import Song, Artist, Album, Playlist
from music_lib.serializers import SongSerializer, SongCreateSerializer, ArtistSerializer, AlbumSerializer, \
    PlaylistSerializer, PlaylistBareSerializer, PlaylistCreateSerializer, UpdatePlaylistsSerializer, \
    SongNameFindSerializer


class SongPaginationClass(PageNumberPagination):
    page_size = 20


class MultiSerializersModelViewSet(ModelViewSet):
    serializer_classes = {}

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action) or self.serializer_classes['default']


@extend_schema(tags=['songs'])
@extend_schema_view(
    list=extend_schema(summary="List all songs"),
    retrieve=extend_schema(summary="Get a song by ID"),
    create=extend_schema(summary="Create a new song"),
    update=extend_schema(summary="Update a song"),
    partial_update=extend_schema(summary="Partial update a song"),
    destroy=extend_schema(summary="Delete a song"),
    stream=extend_schema(summary="Stream a song"),
    favorites=extend_schema(summary="Get all liked songs"),
    like=extend_schema(summary="Like or unlike a song"),
)
class SongAPIViewSet(MultiSerializersModelViewSet):
    serializer_classes = {
        'create': SongCreateSerializer,
        'default': SongSerializer
    }

    filter_backends = [DjangoFilterBackend]
    filterset_class = SongFilter
    pagination_class = SongPaginationClass

    def get_queryset(self):
        user = self.request.user
        liked_songs = user.liked_songs.filter(pk=OuterRef('pk'))

        queryset = Song.objects.annotate(
            is_liked=Exists(liked_songs)
        ).select_related('album').prefetch_related('artists').order_by('id')
        return queryset


    @action(detail=True, methods=['get'])
    def stream(self, request: Request, pk: int) -> HttpResponse | StreamingHttpResponse:
        # Assuming 'pk' is the filename or part of the path
        song = get_object_or_404(Song, pk=pk)
        file_path = song.file.path

        if not os.path.exists(file_path):
            raise Http404("Audio file does not exist.")

        if not song.is_available:
            return HttpResponse(
                data={
                    'message': 'Not available'
                },
                status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
            )

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

    @action(detail=False, methods=['get'])
    def favorites(self, request: Request) -> Response:
        user = request.user

        queryset = user.liked_songs.annotate(
            is_liked=Value(True, output_field=BooleanField())
        ).select_related('album').prefetch_related('artists')
        serializer = SongSerializer(queryset, many=True, context={'request': request})
        return Response(data=serializer.data)

    @action(detail=True, methods=['post'], serializer_class=None)
    def like(self, request: Request, pk: int) -> Response:
        song = get_object_or_404(Song, pk=pk)
        user = request.user

        if user.liked_songs.filter(pk=song.pk).exists():
            user.liked_songs.remove(song)
        else:
            user.liked_songs.add(song)

        return Response(data={"message": "ok"})

    @action(detail=True, methods=['get'])
    def is_liked(self, request: Request, pk: int) -> Response:
        song = get_object_or_404(Song, pk=pk)
        user = request.user

        return Response(data={"is_liked": user.liked_songs.filter(pk=song.pk).exists()})


@extend_schema(tags=['artists'])
@extend_schema_view(
    list=extend_schema(summary="List all artists"),
    retrieve=extend_schema(summary="Get an artist by ID"),
)
class ArtistAPIViewSet(ModelViewSet):
    http_method_names = ['get', 'list']
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()


@extend_schema(tags=['albums'])
@extend_schema_view(
    list=extend_schema(summary="List all albums"),
    retrieve=extend_schema(summary="Get an album by ID"),
)
class AlbumAPIViewSet(ModelViewSet):
    http_method_names = ['get', 'list']
    serializer_class = AlbumSerializer

    def get_queryset(self):
        user = self.request.user
        liked_songs = user.liked_songs.filter(pk=OuterRef('pk'))

        queryset = Album.objects.prefetch_related(
            Prefetch('song_set', queryset=Song.objects.annotate(
                is_liked=Exists(liked_songs)
            ))
        )
        return queryset



@extend_schema(tags=['playlists'])
@extend_schema_view(
    list=extend_schema(summary="List all playlists"),
    retrieve=extend_schema(summary="Get a playlist by ID"),
    create=extend_schema(summary="Create a new playlist"),
    update=extend_schema(summary="Update a playlist"),
    partial_update=extend_schema(summary="Partial update a playlist"),
    destroy=extend_schema(summary="Delete a playlist"),
    update_playlists=extend_schema(summary="Update multiple playlists"),
    add_song=extend_schema(summary="Add a song to a playlist"),
    names=extend_schema(summary="Get names of all playlists"),
)
class PlaylistAPIViewSet(MultiSerializersModelViewSet):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    serializer_classes = {
        'update_playlists': UpdatePlaylistsSerializer,
        'create': PlaylistCreateSerializer,
        'default': PlaylistSerializer
    }

    def get_queryset(self):
        user = self.request.user
        liked_songs = user.liked_songs.filter(pk=OuterRef('pk'))

        return Playlist.objects.filter(user=self.request.user).prefetch_related(
            Prefetch('songs', queryset=Song.objects.annotate(
                is_liked=Exists(liked_songs)
            ))
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def add_song(self, request: Request, pk: int) -> Response:
        playlist = get_object_or_404(Playlist, pk=pk)
        song = get_object_or_404(Song, pk=int(request.data.get('song_id', -1)))

        if playlist.songs.filter(pk=song.pk).exists():
            raise Http404()

        playlist.songs.add(song)
        return Response(data={"data": "ok"})

    @action(detail=False)
    def names(self, request: Request) -> Response:
        serializer = PlaylistBareSerializer(self.get_queryset(), many=True)

        return Response(
            data=serializer.data
        )

    @action(detail=False, methods=["post"])
    def update_playlists(self, request: Request) -> Response:
        playlists = Playlist.objects.filter(id__in=request.data.get('ids', []))
        song = get_object_or_404(Song, pk=int(request.data.get('song', -1)))

        for playlist in playlists:
            if playlist.songs.filter(id=song.id):
                playlist.songs.remove(song)
            else:
                playlist.songs.add(song)

        return Response(
            data={
                "message": "ok"
            }
        )
