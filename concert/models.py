from django.conf import settings
from django.db import models


class Concert(models.Model):
    concert_name = models.CharField(max_length=200)
    duration = models.PositiveSmallIntegerField()
    city = models.CharField(max_length=100)
    date = models.DateField()

    class Meta:
        ordering = ["date", "pk"]

    def __str__(self):
        return self.concert_name


class ConcertAttending(models.Model):
    class AttendingChoices(models.TextChoices):
        NOTHING = "-", "-"
        NOT_ATTENDING = "Not Attending", "Not Attending"
        ATTENDING = "Attending", "Attending"

    concert = models.ForeignKey(Concert, on_delete=models.CASCADE, related_name="attendee")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    attending = models.CharField(
        max_length=20, choices=AttendingChoices.choices, default=AttendingChoices.NOTHING
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["concert", "user"], name="one_rsvp_per_concert_user")
        ]

    def __str__(self):
        return self.attending


class Photo(models.Model):
    pic_url = models.URLField(max_length=500)
    event_country = models.CharField(max_length=100, blank=True)
    event_state = models.CharField(max_length=100, blank=True)
    event_city = models.CharField(max_length=100)
    event_date = models.CharField(max_length=40)

    class Meta:
        managed = False


class Song(models.Model):
    title = models.CharField(max_length=200)
    lyrics = models.TextField()

    class Meta:
        managed = False
