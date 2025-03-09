from django.contrib import admin
from music_notes.models import Category,Page
from music_notes.models import UserProfile

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug":("name",)}

class PageAdmin(admin.ModelAdmin):

    list_display = ("title", "category", "url")

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)

