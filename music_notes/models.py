from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Category(models.Model):
    NAME_MAX_LENGTH = 128

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)
    

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args,**kwargs)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    
class Page(models.Model):
    TITLE_MAX_LENGTH = 128
    URL_MAX_LENGTH = 200

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    url = models.URLField()
    views = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website = models.URLField(blank=True, null=True)
    picture = models.ImageField(upload_to="profile_images", blank=True, null=True, default="profile_images/default_profile.jpg")

    def __str__(self):
        return self.user.username 
    
class Artist(models.Model):
    name = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to="artists/", blank=True, null=True)

    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="albums")
    release_date = models.DateField()
    cover_image = models.ImageField(upload_to="albums/", blank=True, null=True)

    def __str__(self):
        return self.title

class Song(models.Model):
    def default_artist():
        return Artist.objects.get_or_create(name="Unknown Artist")[0].id
    
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, default=default_artist, related_name="songs")
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="songs")
    duration = models.DurationField()

    def __str__(self):
        return self.title
    
    

def validate_review_length(value):
    words = value.split()
    if len(words) > 100:  #word limit of 100
        raise ValidationError(f"Review cannot exceed 100 words. Currently {len(words)} words.")

class AlbumReview(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="album_reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField(validators=[validate_review_length]) # Review with a word limit of 100
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating from 1-5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.album.title} review by {self.user.username} - {self.rating}"

class SongReview(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="song_reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField(validators=[validate_review_length]) # Review with a word limit of 100
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating from 1-5
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.song.title} review by {self.user.username} - {self.rating}"
