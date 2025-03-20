# Generated by Django 2.2.28 on 2025-03-20 12:29

from django.db import migrations, models
import django.db.models.deletion
import music_notes.models


class Migration(migrations.Migration):

    dependencies = [
        ('music_notes', '0005_merge_20250320_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='artist',
            field=models.ForeignKey(default=music_notes.models.Song.default_artist, on_delete=django.db.models.deletion.CASCADE, to='music_notes.Artist'),
        ),
    ]
