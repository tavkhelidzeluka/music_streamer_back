# Generated by Django 5.0.6 on 2024-09-03 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music_lib', '0006_song_duration_song_play_count_playevent'),
        ('users', '0002_user_liked_songs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='liked_songs',
            field=models.ManyToManyField(blank=True, related_name='liked_by', to='music_lib.song'),
        ),
    ]