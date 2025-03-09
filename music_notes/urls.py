from django.urls import path
from music_notes import views

app_name = 'music_notes'

urlpatterns = [
    path('',views.index,name='index'),
    path("about/",views.about,name="about"),
    path("category/<slug:category_name_slug>/",
        views.show_category, name="show_category"),
    path("add_category/", views.add_category, name="add_category"),
    path("category/<category_name_slug>/add_page/", views.add_page, name="add_page"),
    path("register/",views.register,name="register"),
    path("login/", views.user_login, name="login"),
    path("restricted/", views.restricted, name="restricted"),
    path("logout/", views.user_logout, name="logout"),
    path('browse/', views.browse, name='browse'),
    path('search/', views.search, name='search'),
    path('account/', views.account, name='account'),
    path('account/edit/', views.edit_account, name='edit_account'),
    ]