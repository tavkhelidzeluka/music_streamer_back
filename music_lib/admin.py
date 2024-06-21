from django.contrib import admin

from music_lib.models import Artist, Album, Song


admin.site.register([Artist, Album, Song])
