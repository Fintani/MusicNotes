from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import datetime
from django.core.paginator import Paginator
from .forms import EditAccountForm
from django.contrib import messages
from .models import UserProfile, Artist, Album, Song, AlbumReview, SongReview


from music_notes.forms import CategoryForm
from music_notes.forms import PageForm
from music_notes.forms import UserForm, UserProfileForm

def index(request):

    context_dict = {
        "popular_songs": POPULAR_SONGS,
        "highest_rated_songs": HIGHEST_RATED_SONGS,
        "song_suggestions": SONG_SUGGESTIONS,
        "album_suggestions": ALBUM_SUGGESTIONS,
        "recommended_songs": RECOMMENDED_SONGS,
    }

    visitor_cookie_handler(request)

    response = render(request, "music_notes/index.html", context=context_dict)
    return response

def about(request):
    context_dict={}
    #replace these with real values
    context_dict["song_count"] = 100
    context_dict["album_count"] = 100
    context_dict["artist_count"] = 100

    return render(request, "music_notes/about.html", context=context_dict)

def browse(request):
    return render(request, 'music_notes/browse.html')


def register(request):
    registered = False

    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if "picture" in request.FILES:
                profile.picture = request.FILES["picture"]

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  "music_notes/register.html",
                  context = {"user_form": user_form,
                             "profile_form": profile_form,
                             "registered": registered})

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse("music_notes:index"))
            else:
                return HttpResponse("Your music_notes account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, "music_notes/login.html")
    
@login_required
def restricted(request):
    return render(request, "music_notes/restricted.html")

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse("music_notes:index"))

@login_required
def account(request):
    page = request.GET.get('page', 1)
    paginator = Paginator(RATINGS_DB, 5)
    ratings = paginator.get_page(page)
    
    context = {
        "user": request.user,
        "total_ratings": len(RATINGS_DB),
        "ratings": ratings,
    }
    return render(request, "music_notes/account.html", context)


@login_required
def edit_account(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if created and not user_profile.picture:
        user_profile.picture = "profile_images/default_profile.jpg"
        user_profile.save()

    if request.method == "POST":
        form = EditAccountForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()

            if "picture" in request.FILES:
                user_profile.picture = request.FILES["picture"]
                user_profile.save()

            messages.success(request, "Your account has been updated successfully!")
            return redirect("music_notes:account")
    else:
        form = EditAccountForm(instance=request.user)

    return render(request, "music_notes/edit_account.html", {"form": form})

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request,"visits", "1"))
    last_visit_cookie = get_server_side_cookie(request,
                                               "last_visit",
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        "%Y-%m-%d %H:%M:%S")
    
    if (datetime.now()-last_visit_time).days > 0:
        visits = visits +1
        request.session["last_visit"] = str(datetime.now())
    else:
        request.session["last_visit"] = last_visit_cookie

    request.session["visits"] = visits

def search(request):
    context_dict = {}
    if request.method == "POST":
        song_query = request.POST["song_query"]
        context_dict["song_query"] = song_query

        songs = Song.objects.filter(title__contains=song_query)
        context_dict["songs"] = songs

        albums = Album.objects.filter(title__contains=song_query)
        context_dict["albums"] = albums
        


        artists = Artist.objects.filter(name__contains=song_query)
        context_dict["artists"] = artists

        return render(request, "music_notes/search.html",context_dict)
    else:
        return render(request, "music_notes/search.html")

def artist_detail(request, artist_slug):
    artist = get_object_or_404(Artist, slug=artist_slug)
    name = artist.name
    albums = artist.albums.all()
    songs = artist.songs.all()

    return render(request, 'music_notes/artist_detail.html', {
        'artist': artist,
        'name': name,
        'albums': albums,
        'songs': songs
    })

def album_detail(request, artist_slug, album_slug):
    #details
    album = get_object_or_404(Album, slug=album_slug, artist__slug=artist_slug)
    songs = album.songs.all()
    artist = album.artist
    release_date = album.release_date
    #reviews
    page = request.GET.get('page', 1)
    all_reviews = AlbumReview.objects.filter(album=album).select_related('user').order_by('-created_at')
    paginator = Paginator(all_reviews, 5)  # 5 reviews per page
    reviews = paginator.get_page(page)

    return render(request, 'music_notes/album_detail.html', {
        'album': album,
        'songs': songs,
        'artist': artist,
        'release_date': release_date,
        'reviews': reviews,
        'total_reviews': paginator.count,
    })

def song_detail(request, artist_slug, album_slug, song_slug):
    #details
    song = get_object_or_404(
        Song,
        slug=song_slug,
        album__slug=album_slug,
        album__artist__slug=artist_slug
    )
    #reviews
    page = request.GET.get('page', 1)
    all_reviews = SongReview.objects.filter(song=song).select_related('user').order_by('-created_at')
    paginator = Paginator(all_reviews, 5)  # 5 reviews per page
    reviews = paginator.get_page(page)

    return render(request, 'music_notes/song_detail.html', {
        'song': song,
        'album': song.album,
        'artist': song.album.artist,
        'duration': song.duration,
        'reviews': reviews,
        'total_reviews': paginator.count,
    })


# THE ENTRIES BELOW ARE JUST FOR TESTING PURPOSES. REPLACE IT WITH REAL DATABASE QUERIES

# INDEX PAGE
POPULAR_SONGS = [
    {"title": "Song 1", "artist": "Artist A"},
    {"title": "Song 2", "artist": "Artist B"},
    {"title": "Song 3", "artist": "Artist C"},
    {"title": "Song 4", "artist": "Artist D"},
    {"title": "Song 5", "artist": "Artist E"},
]

HIGHEST_RATED_SONGS = [
    {"title": "Song 1", "artist": "Artist X"},
    {"title": "Song 2", "artist": "Artist Y"},
    {"title": "Song 3", "artist": "Artist Z"},
    {"title": "Song 4", "artist": "Artist W"},
    {"title": "Song 5", "artist": "Artist V"},
    {"title": "Song 6", "artist": "Artist U"},
    {"title": "Song 7", "artist": "Artist T"},
    {"title": "Song 8", "artist": "Artist S"},
    {"title": "Song 9", "artist": "Artist R"},
    {"title": "Song 10", "artist": "Artist Q"},
]

SONG_SUGGESTIONS = [
    {"id": 1, "title": "Search Song 1"},
    {"id": 2, "title": "Search Song 2"},
]

ALBUM_SUGGESTIONS = [
    {"id": 1, "title": "Search Album 1"},
    {"id": 2, "title": "Search Album 2"},
]

RECOMMENDED_SONGS = [
    {"title": "Recommended 1", "artist": "Artist M"},
    {"title": "Recommended 2", "artist": "Artist N"},
    {"title": "Recommended 3", "artist": "Artist O"},
    {"title": "Recommended 4", "artist": "Artist P"},
]

# ACCOUNT PAGE
RATINGS_DB = [
    {"value": 3, "song_or_album": "Shape of You", "artist": "Ed Sheeran", "date": "2025-03-01"},
    {"value": 4, "song_or_album": "Blinding Lights", "artist": "The Weeknd", "date": "2025-02-28"},
    {"value": 3, "song_or_album": "Bohemian Rhapsody", "artist": "Queen", "date": "2025-02-25"},
    {"value": 5, "song_or_album": "Thriller", "artist": "Michael Jackson", "date": "2025-02-20"},
    {"value": 5, "song_or_album": "Numb", "artist": "Linkin Park", "date": "2025-02-15"},
    {"value": 4, "song_or_album": "Someone Like You", "artist": "Adele", "date": "2025-02-10"},
    {"value": 2, "song_or_album": "Old Town Road", "artist": "Lil Nas X", "date": "2025-02-05"},
]