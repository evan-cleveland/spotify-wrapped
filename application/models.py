from django.db import models
from django.utils import timezone


class User(models.Model):
    spotify_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)  # Adjust based on requirements
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        """
            Return string representation of user.
            """
        return self.username if self.username else "Unnamed User"

class TopArtist6(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='top_artists_6')
    artist_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    genres = models.JSONField()  # Store as JSON array

    def __str__(self):
        """
            Return string representation top artist over six months.
            """
        return self.name
    class Meta:
        verbose_name = "Top Artist"
        verbose_name_plural = "Top Artists for Last 6 Months"

class Wrapped(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)  # Default to current time

    # JSON fields for storing complex data
    top_artists_6_months = models.JSONField(default=list)
    top_tracks_6_months = models.JSONField(default=list)
    genres_6_months = models.JSONField(default=list)
    recent_tracks = models.JSONField(default=list)
    rising_artists = models.JSONField(default=list)
    ghosted_artists = models.JSONField(default=list)
    top_unfollowed_artists = models.JSONField(default=list)

    all_time_top_artists = models.JSONField(default=list)
    all_time_top_tracks = models.JSONField(default=list)
    all_time_genres = models.JSONField(default=list)


    def __str__(self):
        """
            Return string representation of a wrapped.
            """
        return f"Wrapped for {self.user.username} on {self.timestamp or 'Unknown Time'}"
