from django import forms
from music_notes.models import Page, Category, UserProfile, AlbumReview, Song, SongReview, Album
from django.contrib.auth.models import User


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=Category.NAME_MAX_LENGTH,
                           help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput, initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ("name",)

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=Page.TITLE_MAX_LENGTH,
                            help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=Page.URL_MAX_LENGTH,
                         help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput, initial=0)

    class Meta:
        model = Page
        exclude = ("category",)

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get("url")

        if url and not url.startswith("http://"):
            url = f"http://{url}"
            cleaned_data["url"] = url

        return cleaned_data
    
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("username","email","password",)
        
class AddForm(forms.ModelForm):
    title = forms.CharField(max_length=255)
    artist = forms.CharField(widget=forms.HiddenInput(), initial=0)
    cover = forms.ImageField()
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ("title","artist","cover")


class AddSongForm(forms.ModelForm):
    title = forms.CharField(max_length=255)
    duration = forms.DurationField()
    
    class Meta:
        model = Song
        exclude = ("artist", "album",)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("picture",)
        
class AddAlbumReview(forms.ModelForm):
    
    rating = forms.IntegerField()
    review = forms.CharField()
    
    class Meta:
        model = AlbumReview
        exclude = ("album", "user",)

class AddSongReview(forms.ModelForm):
    rating = forms.IntegerField()
    review = forms.CharField()
    
    class Meta:
        model = SongReview
        exclude = ("song", "user",)

class EditAccountForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ["username", "email"]

    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data.get("profile_picture"):
            user.userprofile.picture = self.cleaned_data["profile_picture"]
            user.userprofile.save()

        if commit:
            user.save()
            return user
        return user