import logging

import requests as req
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, RSVPForm, SignUpForm
from .models import Concert, ConcertAttending

logger = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html")


def catalog(request, service_url, endpoint, key, template, envelope=None):
    try:
        response = req.get(f"{service_url.rstrip('/')}/{endpoint}", timeout=(2, 4))
        response.raise_for_status()
        rows = response.json()
        if envelope and isinstance(rows, dict):
            rows = rows.get(envelope)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError("Catalog must be a list of objects")
    except (req.RequestException, ValueError):
        logger.warning("Catalog unavailable: %s", endpoint)
        return render(
            request, template, {"error": f"The {key} catalog is temporarily unavailable."},
            status=503,
        )

    return render(request, template, {key: rows})


def songs(request):
    return catalog(request, settings.SONGS_SERVICE_URL, "song", "songs", "songs.html", "songs")


def photos(request):
    return catalog(request, settings.PICTURES_SERVICE_URL, "picture", "photos", "photos.html")


def signup(request):
    form = SignUpForm(request.POST if request.method == "POST" else None)
    if form.is_valid():
        login(request, form.save())
        return redirect("concerts")
    return render(request, "signup.html", {"form": form})


def login_view(request):
    form = LoginForm(request, data=request.POST if request.method == "POST" else None)
    next_url = request.POST.get("next") or request.GET.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, {request.get_host()}, request.is_secure()):
        next_url = ""
    if form.is_valid():
        login(request, form.get_user())
        return redirect(next_url or reverse("concerts"))
    return render(request, "login.html", {"form": form, "next": next_url})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def concerts(request):
    statuses = dict(
        ConcertAttending.objects.filter(user=request.user).values_list("concert_id", "attending")
    )
    rows = [
        {"concert": concert, "status": statuses.get(concert.pk, ConcertAttending.AttendingChoices.NOTHING)}
        for concert in Concert.objects.all()
    ]
    return render(request, "concerts.html", {"concerts": rows})


@login_required
def concert_detail(request, id):
    concert = get_object_or_404(Concert, pk=id)
    rsvp = ConcertAttending.objects.filter(concert=concert, user=request.user).first()
    choices = ConcertAttending.AttendingChoices
    return render(request, "concert_detail.html", {
        "concert_details": concert,
        "status": rsvp.attending if rsvp else choices.NOTHING,
        "attending_choices": choices.choices,
    })


@require_POST
@login_required
def concert_attendee(request):
    form = RSVPForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Choose a valid RSVP status and concert.")
    concert = get_object_or_404(Concert, pk=form.cleaned_data["concert_id"])
    ConcertAttending.objects.update_or_create(
        user=request.user, concert=concert,
        defaults={"attending": form.cleaned_data["attendee_choice"]},
    )
    return redirect("concerts")


def health(request):
    return JsonResponse({"status": "OK"})
