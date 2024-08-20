from django.db import models
from django_filters import rest_framework as filters


class SongFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_name_or_artist', label='Search by name or artist')

    def filter_name_or_artist(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value)
            | models.Q(artists__name__icontains=value)
        )
