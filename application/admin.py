# from django.contrib import admin
# from .models import User, Wrapped, TopSong4, TopSong6, TopSong12, TopArtist4, TopArtist6, TopArtist12, Genre4, Genre6, Genre12
#
# class TopSong4Inline(admin.TabularInline):
#     """
#     Inline model for managing the relationship between Wrapped instances
#     and their top songs for the last 6 months.
#
#     Attributes:
#         model (Model): Specifies the intermediary model linking Wrapped and TopSong6.
#         extra (int): Number of empty inline forms to display by default.
#         verbose_name (str): Singular label for the related model.
#         verbose_name_plural (str): Plural label for the related model.
#     """
#     model = Wrapped.top_songs_4.through
#     extra = 1
#     verbose_name = "Top Song"
#     verbose_name_plural = "Top Songs for Last 4 Weeks"
#
# class TopSong6Inline(admin.TabularInline):
#     """
#     Inline model for managing the relationship between Wrapped instances
#     and their top songs for the last 6 months.
#
#     Attributes:
#         model (Model): Specifies the intermediary model linking Wrapped and TopSong6.
#         extra (int): Number of empty inline forms to display by default.
#         verbose_name (str): Singular label for the related model.
#         verbose_name_plural (str): Plural label for the related model.
#     """
#     model = Wrapped.top_songs_6.through
#     extra = 1
#     verbose_name = "Top Song"
#     verbose_name_plural = "Top Songs for Last 6 Months"
#
# class TopSong12Inline(admin.TabularInline):
#     """
#     Inline model for managing the relationship between Wrapped instances
#     and their top songs for the last 6 months.
#
#     Attributes:
#         model (Model): Specifies the intermediary model linking Wrapped and TopSong6.
#         extra (int): Number of empty inline forms to display by default.
#         verbose_name (str): Singular label for the related model.
#         verbose_name_plural (str): Plural label for the related model.
#     """
#     model = Wrapped.top_songs_12.through
#     extra = 1
#     verbose_name = "Top Song"
#     verbose_name_plural = "Top Songs for Last 12 Months"
#
# class TopArtist4Inline(admin.TabularInline):
#     """
#     Inline model for managing the relationship between Wrapped instances
#     and their top artists for the last 6 months.
#
#     Attributes:
#         model (Model): Specifies the intermediary model linking Wrapped and TopArtist6.
#         extra (int): Number of empty inline forms to display by default.
#         verbose_name (str): Singular label for the related model.
#         verbose_name_plural (str): Plural label for the related model.
#     """
#     model = Wrapped.top_artists_6.through
#     extra = 1
#     verbose_name = "Top Artist"
#     verbose_name_plural = "Top Artists for Last 4 Weeks"
#
# class TopArtist6Inline(admin.TabularInline):
#     """
#     Inline model for managing the relationship between Wrapped instances
#     and their top artists for the last 6 months.
#
#     Attributes:
#         model (Model): Specifies the intermediary model linking Wrapped and TopArtist6.
#         extra (int): Number of empty inline forms to display by default.
#         verbose_name (str): Singular label for the related model.
#         verbose_name_plural (str): Plural label for the related model.
#     """
#     model = Wrapped.top_artists_6.through
#     extra = 1
#     verbose_name = "Top Artist"
#     verbose_name_plural = "Top Artists for Last 6 Months"
#
# class TopArtist12Inline(admin.TabularInline):
#     """
#     Inline model for managing the relationship between Wrapped instances
#     and their top artists for the last 6 months.
#
#     Attributes:
#         model (Model): Specifies the intermediary model linking Wrapped and TopArtist6.
#         extra (int): Number of empty inline forms to display by default.
#         verbose_name (str): Singular label for the related model.
#         verbose_name_plural (str): Plural label for the related model.
#     """
#     model = Wrapped.top_artists_12.through
#     extra = 1
#     verbose_name = "Top Artist"
#     verbose_name_plural = "Top Artists for Last 12 Months"
#
# class Genre6Inline(admin.TabularInline):
#     """
#     Inline model for managing the relationship between Wrapped instances
#     and their top genres for the last 6 months.
#
#     Attributes:
#         model (Model): Specifies the intermediary model linking Wrapped and Genre6.
#         extra (int): Number of empty inline forms to display by default.
#         verbose_name (str): Singular label for the related model.
#         verbose_name_plural (str): Plural label for the related model.
#     """
#     model = Wrapped.genres_6.through
#     extra = 1
#     verbose_name = "Top Genre"
#     verbose_name_plural = "Top Genres for Last 6 Months"
#
# @admin.register(Wrapped)
# class WrappedAdmin(admin.ModelAdmin):
#     """
#     Custom admin class for managing Wrapped instances in the Django admin interface.
#
#     Attributes:
#         list_display (tuple): Fields to display in the admin list view for Wrapped instances.
#         list_filter (tuple): Fields to use for filtering Wrapped instances in the admin interface.
#         inlines (list): List of inline admin classes for related models.
#     """
#     list_display = (
#         'user',
#         'created_at',
#         'spotify_id',
#         'recent_tracks_preview',
#         'rising_artists_preview',
#         'ghosted_artists_preview',
#         'top_unfollowed_artists_preview',
#     )
#     list_filter = ('created_at','user')
#     inlines = [
#         TopSong4Inline,
#         TopSong6Inline,
#         TopSong12Inline,
#         TopArtist4Inline,
#         TopArtist6Inline,
#         TopArtist12Inline,
#         Genre6Inline,
#     ]
#
#     def recent_tracks_preview(self, obj):
#         return obj.recent_tracks[:3] if obj.recent_tracks else "No recent tracks"
#     recent_tracks_preview.short_description = "Recent Tracks"
#
#     def rising_artists_preview(self, obj):
#         return obj.rising_artists[:3] if obj.rising_artists else "No rising artists"
#     rising_artists_preview.short_description = "Rising Artists"
#
#     def ghosted_artists_preview(self, obj):
#         return obj.ghosted_artists[:3] if obj.ghosted_artists else "No ghosted artists"
#     ghosted_artists_preview.short_description = "Ghosted Artists"
#
#     def top_unfollowed_artists_preview(self, obj):
#         return obj.top_unfollowed_artists[:3] if obj.top_unfollowed_artists else "No top unfollowed artists"
#     top_unfollowed_artists_preview.short_description = "Top Unfollowed Artists"
#
# # Register the User model in the admin site.
# admin.site.register(User)
#
# # Uncomment these lines to register the individual models in the admin site if needed.
# # admin.site.register(TopSong6)
# # admin.site.register(TopArtist6)
# # admin.site.register(Genre6)

from django.contrib import admin
from .models import Wrapped

admin.site.register(Wrapped)