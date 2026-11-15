from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import ConcertAttending


class StyledForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class LoginForm(StyledForm, AuthenticationForm):
    pass


class SignUpForm(StyledForm, UserCreationForm):
    pass


class RSVPForm(forms.Form):
    concert_id = forms.IntegerField(min_value=1)
    attendee_choice = forms.ChoiceField(choices=ConcertAttending.AttendingChoices.choices)
