from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import SurveyResponse


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

class SurveyResponseForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        exclude = ['created_at', 'audio_blob', 'audio_mime_type']

    REQUIRED_FIELDS = {
        'gender', 'email', 'course', 'year',
        'q8', 'q9', 'q11', 'q12', 'q13',
        'q21', 'q22', 'q23', 'q24', 'q25',
        'q27', 'q28', 'q29', 'q30', 'q31',
        'q37', 'q38', 'q39', 'q40', 'q41', 'q42',
        'survey_rating',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.REQUIRED_FIELDS:
            self.fields[name].required = True

    def clean(self):
        cleaned = super().clean()
        for name in ('age', 'q31', 'q40', 'q42', 'survey_rating'):
            if cleaned.get(name) in ('', 'Not answered'):
                cleaned[name] = None
        return cleaned
