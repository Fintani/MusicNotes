from django.urls import path
from music_notes import views

app_name = 'music_notes'

urlpatterns = [
    path('',views.index,name='index'),
    path("about/",views.about,name="about"),
    path("register/",views.register,name="register"),
    path("login/", views.user_login, name="login"),
    path("restricted/", views.restricted, name="restricted"),
    path("logout/", views.user_logout, name="logout"),
    path('browse/', views.browse, name='browse'),
    path('search/', views.search, name='search'),
    path('account/', views.account, name='account'),
    path("add/",views.add,name="add"),
    path('account/edit/', views.edit_account, name='edit_account'),
    path('<slug:artist_slug>/', views.artist_detail, name='artist_detail'),
    path('<slug:artist_slug>/<slug:album_slug>/', views.album_detail, name='album_detail'),
    path('<slug:artist_slug>/<slug:album_slug>/add_song/', views.add_song, name='add_song'),
    path('<slug:artist_slug>/<slug:album_slug>/<slug:song_slug>/', views.song_detail, name='song_detail'),
    ]