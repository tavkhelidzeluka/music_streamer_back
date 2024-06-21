from rest_framework.routers import DefaultRouter

from music_lib.api_views import SongAPIViewSet, ArtistAPIViewSet, AlbumAPIViewSet

router = DefaultRouter()
router.register('songs', SongAPIViewSet, basename='song')
router.register('artists', ArtistAPIViewSet, basename='artist')
router.register('albums', AlbumAPIViewSet, basename='album')


urlpatterns = [
    *router.urls
]
