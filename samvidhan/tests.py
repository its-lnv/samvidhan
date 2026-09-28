from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import SurveyResponse


class SurveyFlowTests(TestCase):
    payload = {
        'name': 'Test Respondent', 'age': '21', 'gender': 'Male',
        'email': 'test@example.com', 'course': 'Science',
        'college': 'Test College', 'year': '1st Year',
        'q8': 'Yes', 'q9': 'Yes - Properly', 'q10': 'Test response',
        'q11': '26th January, 1950 ✓', 'q12': 'Dr. B.R. Ambedkar',
        'q13': '395 (original)', 'q14': 'Test title', 'q21': 'Yes',
        'q22': 'Always', 'q23': 'Respect the National Flag & Anthem',
        'q24': 'Stand up & sing with full josh!', 'q25': 'Today',
        'q26': 'Test duties', 'q27': 'Yes - Absolutely', 'q28': 'No',
        'q29': 'Yes', 'q30': 'Necessary and should continue', 'q31': '5',
        'q37': 'Yes - Most are aware', 'q38': 'Yes - Definitely',
        'q39': 'Social media campaigns (Reels, Memes!, this Survey)',
        'q40': '5', 'q41': 'No Comment', 'q42': '5',
        'q43': 'Test suggestion', 'q44': 'Test takeaway',
        'q45': 'Test article', 'survey_rating': '5',
        'audio_url': '', 'audio_status': 'No audio recorded',
    }

    def test_submission_is_session_scoped(self):
        response = self.client.post('/survey/', self.payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/results/')
        saved = SurveyResponse.objects.get(pk=self.client.session['survey_response_id'])

        staff = get_user_model().objects.create_user(
            username='test-staff', password='test-password', is_staff=True,
        )
        self.client.force_login(staff)
        results = self.client.get('/results/')
        self.assertContains(results, saved.name)

        other_client = self.client_class()
        other_results = other_client.get('/results/')
        self.assertEqual(other_results.status_code, 302)
        self.assertIn('/admin/login/', other_results.url)
