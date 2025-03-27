from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.db.models import Avg
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


from music_notes.forms import CategoryForm, PageForm, UserForm, UserProfileForm, AddAlbumReview, AddSongReview

def index(request):

    HIGHEST_RATED_ALBUMS = Album.objects.order_by('-averageRating')
    HIGHEST_RATED_SONGS = Song.objects.order_by('-averageRating')

    context_dict = {
        "highest_rated_albums": HIGHEST_RATED_ALBUMS,
        "highest_rated_songs": HIGHEST_RATED_SONGS,
    }

    visitor_cookie_handler(request)

    response = render(request, "music_notes/index.html", context=context_dict)
    return response

def about(request):
    context_dict={}
    #replace these with real values
    context_dict["song_count"] = len(Song.objects.filter())
    context_dict["album_count"] = len(Album.objects.filter())
    context_dict["artist_count"] = len(Artist.objects.filter())

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
    reviews = AlbumReview.objects.filter(user=request.user)
    
    user_reviews = []
    for i in reviews:
        user_reviews.append({"value":i.rating, "artist": i.album.artist.name, "song_or_album": i.album, "date": i.created_at})

    reviews = SongReview.objects.filter(user=request.user)
    for i in reviews:
        user_reviews.append({"value":i.rating, "artist": i.song.artist.name, "song_or_album": i.song, "date": i.created_at})
    
    paginator = Paginator(user_reviews, 5)
    ratings = paginator.get_page(page)
    
    context = {
        "user": request.user,
        "total_ratings": len(reviews),
        "ratings": ratings,
    }
    return render(request, "music_notes/account.html", context)

@login_required
def add(request):
    if request.method == "POST":
        album_title = request.POST["title"]
        artist_name = request.POST["artist"]
        
        artists = Artist.objects.filter(name=artist_name)
        
        if len(artists) == 0:
            artist = Artist(name=artist_name)
            artist.save()
        else:
            artist = artists[0]
        
        album = Album(title=album_title, artist=artist)
        album.save()
        return redirect(reverse("music_notes:index"))
    return render(request, "music_notes/add.html")

@login_required
def add_song(request, artist_slug, album_slug):
    if request.method == "POST":
        
        title = request.POST["title"]
        
        album = Album.objects.filter(slug=album_slug)
        song = Song(title=title, artist=album[0].artist, album=album[0])
        song.save()
        
        songs = Song(album=album[0])
        reviews = AlbumReview.objects.filter(album=album[0])
        
        return redirect(("music_notes:index"))
    
    album = Album.objects.filter(slug=album_slug)
    return render(request, "music_notes/add_song.html", {
        'album': album[0],
        'artist': album[0].artist
    })


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
    #reviews
    page = request.GET.get('page', 1)
    all_reviews = AlbumReview.objects.filter(album=album).select_related('user').order_by('-created_at')
    paginator = Paginator(all_reviews, 5)  # 5 reviews per page
    reviews = paginator.get_page(page)
    
    average = AlbumReview.objects.filter(album=album).aggregate(Avg('rating'))
    print(average)
    album.averageRating = average['rating__avg']
    album.save()
    
    try:
        album = Album.objects.get(slug=album_slug)
    except Album.DoesNotExist:
        album = None
    
    if album is None:
        return redirect('/music_notes/')
    
    shown = True
    if len(AlbumReview.objects.filter(album=album, user=request.user)) != 0:
        shown = False

    if request.method == "POST":
        
        album_form = AddAlbumReview(request.POST)
        review = request.POST["review"]
        rating = request.POST["rating"]
        
        user = UserProfile.objects.get_or_create(user=request.user)
        review = AlbumReview(album=album, user=request.user, review=review, rating=rating)
        if len(AlbumReview.objects.filter(album=album, user=request.user)) == 0:
            review.save()
            average = AlbumReview.objects.filter(album=album).aggregate(Avg('rating'))
            album.averageRating=average['rating__avg']
            print(average)
            return redirect(("music_notes:index"))
        else :
            user_review = AlbumReview.objects.filter(album=album, user=request.user)
            user_review[0].rating = rating
            user_review[0].review = review
            user_review[0].save()
            shown = False

    return render(request, 'music_notes/album_detail.html', {
        'album': album,
        'songs': songs,
        'artist': artist,
        'reviews': reviews,
        'total_reviews': paginator.count,
        'shown' : shown,
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
    
    average = SongReview.objects.filter(song=song).aggregate(Avg('rating'))
    print(average)
    song.averageRating = average['rating__avg']
    song.save()
    
    shown = True
    if len(SongReview.objects.filter(song=song, user=request.user)) != 0:
        shown = False
        
    if request.method == "POST":
        
        album_form = AddSongReview(request.POST)
        review = request.POST["review"]
        rating = request.POST["rating"]
        
        user = UserProfile.objects.get_or_create(user=request.user)
        review = SongReview(song=song, user=request.user, review=review, rating=rating)
        
        if len(SongReview.objects.filter(song=song, user=request.user)) == 0:
            review.save()
            average = SongReview.objects.filter(song=song).aggregate(Avg('rating'))
            song.averageRating=average['rating__avg']
            print(average)
            return redirect(("music_notes:index"))
        else :
            user_review = SongReview.objects.filter(song=song, user=request.user)
            user_review[0].rating = rating
            user_review[0].review = review
            shown = False

    return render(request, 'music_notes/song_detail.html', {
        'song': song,
        'album': song.album,
        'artist': song.album.artist,
        'reviews': reviews,
        'total_reviews': paginator.count,
        'shown' : shown,
    })
