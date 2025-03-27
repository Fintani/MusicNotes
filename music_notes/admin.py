from django.contrib import admin
from music_notes.models import Category,Page
from music_notes.models import UserProfile
from .models import Artist, Album, Song, AlbumReview, SongReview

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug":("name",)}

class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "url")

class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name",)

# Register Album
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist')  # Columns shown in admin
    search_fields = ('title', 'artist')  # Enable search by title & artist

# Register Song
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist','album')  # Columns shown in admin
    search_fields = ('title', 'album__title')  # Enable search by song title & album

# Register AlbumReview
class AlbumReviewAdmin(admin.ModelAdmin):
    list_display = ('album', 'user', 'rating')
    search_fields = ('album__title', 'user__username')

# Register SongReview
class SongReviewAdmin(admin.ModelAdmin):
    list_display = ('song', 'user', 'rating')
    search_fields = ('song__title', 'user__username')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(AlbumReview, AlbumReviewAdmin)
admin.site.register(SongReview, SongReviewAdmin)
admin.site.register(UserProfile)


