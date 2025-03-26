import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "music_notes_project.settings")

import django
import datetime
django.setup()
from music_notes.models import Song, Album, Artist

def populate():
    theboywiththearabstrap_songs = [
        {'title': 'Ease Your Feet in the Sea',
         "duration" : datetime.timedelta(minutes=3, seconds=35)},
        {'title':'A Summer Wasting',
        "duration" : datetime.timedelta(minutes=2, seconds=6)},
        {'title':'The boy With the Arab Strap',
        "duration" : datetime.timedelta(minutes=5, seconds=14)} 
    ]

    belleandsebastian_albums = {
        'The Boy With the Arab Strap' : {'release':'1998-01-01',
                                         "songs" : theboywiththearabstrap_songs}
    }

    artists = {
        'Belle and Sebastian': {'albums': belleandsebastian_albums},
    }

    for artist, artist_data in artists.items():
        ar = add_artist(artist)
        for album, album_data in artist_data["albums"].items():
            al = add_album(album, ar, album_data["release"])
            for s in album_data["songs"]:
                add_song(s["title"], ar, al, s["duration"])

    for ar in Artist.objects.all():
        for al in Album.objects.filter(artist=ar):
            for s in Song.objects.filter(album=al):
                print(f"- {ar}: {al}: {s}")

def add_song(title, artist, album, duration):
    s = Song.objects.get_or_create(title=title, artist=artist, album=album, duration=duration)[0]
    s.save()
    return s

def add_album(title, artist, release):
    al = Album.objects.get_or_create(title=title, artist=artist, release_date=release)[0]
    al.save()
    return al

def add_artist(name):
    ar = Artist.objects.get_or_create(name=name)[0]
    ar.save()
    return ar

if __name__ == "__main__":
    print("Starting music_notes population script...")
    populate()
