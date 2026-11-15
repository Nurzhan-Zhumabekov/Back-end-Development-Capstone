from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Concert, ConcertAttending


class BandSiteTests(TestCase):
    def setUp(self):
        self.concert = Concert.objects.create(
            concert_name="Neon Nights", duration=2, city="Astana", date=date(2026, 12, 6)
        )
        self.user = get_user_model().objects.create_user("listener", password="stage-door-67!")

    def test_home_and_protected_concerts(self):
        self.assertContains(self.client.get(reverse("index")), "Djirection")
        self.assertRedirects(
            self.client.get(reverse("concerts")), f'{reverse("login")}?next=/concerts/'
        )
        self.client.force_login(self.user)
        self.assertContains(self.client.get(reverse("concerts")), "Neon Nights")

    def test_signup_and_login_use_django_auth(self):
        data = {
            "username": "newfan", "password1": "live-show-M8!", "password2": "live-show-M8!"
        }
        self.assertRedirects(self.client.post(reverse("signup"), data), reverse("concerts"))
        self.assertTrue(get_user_model().objects.get(username="newfan").check_password(data["password1"]))
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("logout")), reverse("index"))
        self.assertRedirects(
            self.client.post(reverse("login"), {"username": "newfan", "password": data["password1"]}),
            reverse("concerts"),
        )

    def test_rsvp_creates_updates_and_rejects_unknown_choice(self):
        path = reverse("concert_attendee")
        fields = {"concert_id": self.concert.pk, "attendee_choice": "Attending"}
        self.assertEqual(self.client.post(path, fields).status_code, 302)
        self.assertEqual(ConcertAttending.objects.count(), 0)
        self.client.force_login(self.user)
        self.assertRedirects(self.client.post(path, fields), reverse("concerts"))
        self.assertRedirects(self.client.post(
            path, {**fields, "attendee_choice": "Not Attending"}
        ), reverse("concerts"))
        self.assertEqual(ConcertAttending.objects.get().attending, "Not Attending")
        self.assertEqual(self.client.post(path, {**fields, "attendee_choice": "Other"}).status_code, 400)
        self.assertEqual(self.client.get(path).status_code, 405)
        self.assertEqual(self.client.post(path, {**fields, "concert_id": 9999}).status_code, 404)

    @patch("concert.views.req.get")
    def test_microservice_catalogs_render(self, get):
        get.return_value.json.return_value = {
            "songs": [{"id": 1, "title": "Night bus", "lyrics": "The last ride"}]
        }
        self.assertContains(self.client.get(reverse("songs")), "Night bus")
        self.assertContains(self.client.get(reverse("songs")), "The last ride")
        get.return_value.json.return_value = [
            {"id": 7, "pic_url": "https://example.org/pic.jpg",
             "event_city": "Astana", "event_state": "", "event_date": "2026-11-15"}
        ]
        self.assertContains(self.client.get(reverse("photos")), "Astana")
        self.assertContains(self.client.get(reverse("photos")), "https://example.org/pic.jpg")

    @patch("concert.views.req.get")
    def test_microservice_unavailable_is_reported(self, get):
        from requests import ConnectionError
        get.side_effect = ConnectionError
        self.assertContains(
            self.client.get(reverse("songs")), "temporarily unavailable", status_code=503
        )
