from rest_framework.routers import DefaultRouter

from music_lib.api_views import SongAPIViewSet, ArtistAPIViewSet, AlbumAPIViewSet, PlaylistAPIViewSet

router = DefaultRouter()
router.register('songs', SongAPIViewSet, basename='song')
router.register('artists', ArtistAPIViewSet, basename='artist')
router.register('albums', AlbumAPIViewSet, basename='album')
router.register('playlists', PlaylistAPIViewSet, basename='playlist')

urlpatterns = [
    *router.urls
]
