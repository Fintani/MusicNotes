import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "music_notes_project.settings")

import django
import datetime
django.setup()
from music_notes.models import Song, Album, Artist, User, SongReview

def populate():
    theboywiththearabstrap_songs = [
        {'title': 'Ease Your Feet in the Sea'},
        {'title':'A Summer Wasting'},
        {'title':'The boy With the Arab Strap'} 
    ]
    
    names = ['Noah', 'Oliver', 'Olivia', 'Amelia']
    ratings = [5, 1, 3, 4, 5, 2, 4, 1, 5, 1, 5, 4]
    reviews = {1 : "Bad", 2 : "Meh", 3 : "Average", 4 : "Good", 5 : "Great"}
    
    users = []
    
    for i in names:
        new = User(username=i, password='password', email=i + "@gmail.com")
        new.save()
        users.append(new)
    
    belleandsebastian_albums = {
        'The Boy With the Arab Strap' : {'release':'1998-01-01',
                                         "songs" : theboywiththearabstrap_songs}
    }

    artists = {
        'Belle and Sebastian': {'albums': belleandsebastian_albums},
    }
    
    count = 0

    for artist, artist_data in artists.items():
        ar = add_artist(artist)
        for album, album_data in artist_data["albums"].items():
            al = add_album(album, ar)
            for s in album_data["songs"]:
                s = add_song(s["title"], ar, al)
                
                songReview1 = SongReview(song=s, user=users[0],review=reviews[ratings[count]],rating=ratings[count])
                songReview2 = SongReview(song=s, user=users[1],review=reviews[ratings[count+1]],rating=ratings[count+1])
                songReview3 = SongReview(song=s, user=users[2],review=reviews[ratings[count+2]],rating=ratings[count+2])
                songReview4 = SongReview(song=s, user=users[3],review=reviews[ratings[count+3]],rating=ratings[count+3])
                
                songReview1.save()
                songReview2.save()
                songReview3.save()
                songReview4.save()
                
                s.calculate_average()
                count += 4

    for ar in Artist.objects.all():
        for al in Album.objects.filter(artist=ar):
            for s in Song.objects.filter(album=al):
                print(f"- {ar}: {al}: {s}")
    

def add_song(title, artist, album):
    s = Song.objects.get_or_create(title=title, artist=artist, album=album)[0]
    s.save()
    return s

def add_album(title, artist):
    al = Album.objects.get_or_create(title=title, artist=artist)[0]
    al.save()
    return al

def add_artist(name):
    ar = Artist.objects.get_or_create(name=name)[0]
    ar.save()
    return ar

if __name__ == "__main__":
    print("Starting music_notes population script...")
    populate()
