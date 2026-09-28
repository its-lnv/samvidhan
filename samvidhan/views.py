import base64
import binascii
import json
import secrets
import time
from collections import Counter
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, Q
from django.http import Http404, HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import slugify

from .forms import RegistrationForm, SurveyResponseForm
from .models import SurveyResponse


staff_required = user_passes_test(
    lambda user: user.is_active and user.is_staff,
    login_url='/admin/login/',
)


PAGE_FILES = {
    'home': 'index.html', 'about': 'about.html', 'rights': 'rights.html',
    'articles': 'articles.html', 'cases': 'cases.html', 'crimes': 'crimes.html',
    'freedom': 'freedom.html', 'helpline': 'helpline.html', 'quiz': 'quiz.html',
    'sovereignty': 'sovereignty.html', 'secularism': 'secularism.html',
    'socialism': 'socialism.html', 'democracy': 'democracy.html',
    'republic': 'republic.html', 'justice': 'justice.html', 'liberty': 'liberty.html',
    'equality': 'equality.html', 'fraternity': 'fraternity.html',
    'dignity': 'dignity.html', 'unity': 'unity.html',
}


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    next_url = request.POST.get('next') or request.GET.get('next', '')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        login_url = reverse('login')
        query = {'registered': '1'}
        if next_url:
            query['next'] = next_url
        return redirect(f'{login_url}?{urlencode(query)}')
    return render(request, 'accounts/register.html', {
        'form': form,
        'next': next_url,
        'google_login_enabled': bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
    })


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    next_url = request.POST.get('next') or request.GET.get('next', '')
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        username = identifier
        if '@' in identifier:
            user = get_user_model().objects.filter(email__iexact=identifier).first()
            username = user.get_username() if user else identifier
        user = authenticate(request, username=username, password=request.POST.get('password', ''))
        if user is not None:
            login(request, user)
            if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect('home')
        messages.error(request, 'The username/email or password was incorrect.')
    return render(request, 'accounts/login.html', {
        'next': next_url,
        'registered': request.GET.get('registered') == '1',
        'google_login_enabled': bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
    })


def user_logout(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')


def google_login(request):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        messages.error(request, 'Google sign-in is not configured yet. Please use your username and password.')
        return redirect('login')
    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state
    request.session['google_oauth_next'] = request.GET.get('next', '')
    redirect_uri = settings.GOOGLE_REDIRECT_URI or request.build_absolute_uri(reverse('google_callback'))
    query = urlencode({
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'prompt': 'select_account',
    })
    return redirect(f'https://accounts.google.com/o/oauth2/v2/auth?{query}')


def google_callback(request):
    expected_state = request.session.pop('google_oauth_state', None)
    supplied_state = request.GET.get('state', '')
    if not expected_state or not secrets.compare_digest(expected_state, supplied_state):
        messages.error(request, 'Google sign-in expired. Please try again.')
        return redirect('login')
    if request.GET.get('error') or not request.GET.get('code'):
        messages.error(request, 'Google sign-in was cancelled or could not be completed.')
        return redirect('login')

    redirect_uri = settings.GOOGLE_REDIRECT_URI or request.build_absolute_uri(reverse('google_callback'))
    token_request = Request(
        'https://oauth2.googleapis.com/token',
        data=urlencode({
            'code': request.GET['code'],
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }).encode(),
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )
    try:
        with urlopen(token_request, timeout=10) as response:
            access_token = json.loads(response.read()).get('access_token')
        if not access_token:
            raise ValueError('Google did not return an access token.')
        profile_request = Request(
            'https://openidconnect.googleapis.com/v1/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
        )
        with urlopen(profile_request, timeout=10) as response:
            profile = json.loads(response.read())
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        messages.error(request, 'Could not verify your Google account. Please try again.')
        return redirect('login')

    email = (profile.get('email') or '').strip().lower()
    if not email or not profile.get('email_verified'):
        messages.error(request, 'Google did not provide a verified email address.')
        return redirect('login')

    user_model = get_user_model()
    user = user_model.objects.filter(email__iexact=email).first()
    if user is None:
        base_username = slugify(email.split('@', 1)[0]) or 'google-user'
        username, suffix = base_username, 1
        while user_model.objects.filter(username=username).exists():
            suffix += 1
            username = f'{base_username}-{suffix}'
        user = user_model.objects.create_user(
            username=username,
            email=email,
            first_name=profile.get('given_name', '')[:150],
            last_name=profile.get('family_name', '')[:150],
        )
    if not user.is_active:
        messages.error(request, 'This account is inactive. Please contact the site administrator.')
        return redirect('login')
    login(request, user)
    next_url = request.session.pop('google_oauth_next', '')
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    return redirect('home')


def legacy_page(request, page_name):
    return render(request, PAGE_FILES[page_name])


def legacy_file(request, page_name):
    return render(request, PAGE_FILES[page_name])


@login_required
def survey(request):
    if request.method == 'POST':
        form = SurveyResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            audio_data = request.POST.get('audio_data', '')
            if audio_data:
                try:
                    header, encoded_audio = audio_data.split(',', 1)
                    response.audio_mime_type = header.split(':', 1)[1].split(';', 1)[0]
                    response.audio_blob = base64.b64decode(encoded_audio, validate=True)
                    if len(response.audio_blob) > 8 * 1024 * 1024:
                        raise ValueError('Audio recording must be smaller than 8 MB.')
                except (ValueError, IndexError, binascii.Error):
                    form.add_error(None, 'The audio recording could not be saved. Please record it again.')
                    return render(request, 'survey.html', {'form': form})
            response.save()
            request.session['survey_response_id'] = response.pk
            return redirect('survey_thank_you')
    else:
        form = SurveyResponseForm()
    return render(request, 'survey.html', {'form': form})


def survey_thank_you(request):
    return render(request, 'pages/survey_thank_you.html')


@login_required
def quiz(request):
    return render(request, 'quiz.html')


QUIZ_QUESTION_SCHEMA = {
    'type': 'OBJECT',
    'properties': {
        'questions': {
            'type': 'ARRAY',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'category': {'type': 'STRING'},
                    'question': {'type': 'STRING'},
                    'options': {'type': 'ARRAY', 'items': {'type': 'STRING'}},
                    'answer_index': {'type': 'INTEGER'},
                    'explanation': {'type': 'STRING'},
                },
                'required': ['category', 'question', 'options', 'answer_index', 'explanation'],
            },
        },
    },
    'required': ['questions'],
}

QUIZ_SCORE_SCHEMA = {
    'type': 'OBJECT',
    'properties': {
        'score': {'type': 'INTEGER'},
        'results': {
            'type': 'ARRAY',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'correct': {'type': 'BOOLEAN'},
                    'explanation': {'type': 'STRING'},
                },
                'required': ['correct', 'explanation'],
            },
        },
    },
    'required': ['score', 'results'],
}


def _gemini_json(prompt, schema):
    """Call Gemini from the server and return its structured JSON response."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError('Gemini is not configured. Add GEMINI_API_KEY to the project .env file.')
    endpoint = (
        f'https://generativelanguage.googleapis.com/v1beta/models/'
        f'{settings.GEMINI_MODEL}:generateContent'
    )
    payload = {
        'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
        'generationConfig': {
            'responseMimeType': 'application/json',
            'responseSchema': schema,
            'temperature': 0.9,
        },
    }
    response_data = None
    for attempt in range(3):
        req = Request(
            endpoint,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'x-goog-api-key': settings.GEMINI_API_KEY},
            method='POST',
        )
        try:
            with urlopen(req, timeout=45) as response:
                response_data = json.loads(response.read().decode('utf-8'))
            break
        except HTTPError as error:
            if error.code != 503 or attempt == 2:
                raise
            time.sleep(attempt + 1)
    text = response_data['candidates'][0]['content']['parts'][0]['text']
    return json.loads(text)


def _gemini_error_response(error):
    if isinstance(error, RuntimeError):
        return JsonResponse({'error': str(error)}, status=503)
    if isinstance(error, HTTPError):
        # Keep provider details and credentials out of the response shown to users.
        if error.code == 404:
            message = 'The configured Gemini model is unavailable. Check GEMINI_MODEL in .env.'
        elif error.code == 429:
            message = 'Gemini request quota is temporarily unavailable. Check your API quota and retry.'
        elif error.code == 503:
            message = 'Gemini is temporarily busy. Please retry in a moment.'
        else:
            message = 'Gemini could not complete the request. Check the API key and project configuration.'
        return JsonResponse({'error': message}, status=502)
    return JsonResponse({'error': 'Gemini is temporarily unavailable. Please try again.'}, status=502)


@login_required
def generate_quiz(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Use POST to generate a quiz.'}, status=405)
    recent = request.session.get('recent_quiz_questions', [])
    recent_text = '\n'.join(f'- {item}' for item in recent[-25:]) or '(none)'
    prompt = (
        'Create a fresh quiz of exactly 10 multiple-choice questions about the Constitution of India. '
        'Use accurate, unambiguous facts across varied topics and difficulty. Every question must have '
        'exactly four distinct options and exactly one correct option. answer_index is zero-based. '
        'Include a concise factual explanation. Avoid repeating these recent questions:\n'
        f'{recent_text}\nReturn only data matching the requested JSON schema.'
    )
    try:
        generated = _gemini_json(prompt, QUIZ_QUESTION_SCHEMA)
        questions = generated.get('questions')
        if not isinstance(questions, list) or len(questions) != 10:
            raise ValueError('Invalid question count')
        normalized = []
        for item in questions:
            options = item.get('options')
            answer_index = item.get('answer_index')
            if (not isinstance(item.get('question'), str) or not item['question'].strip()
                    or not isinstance(item.get('category'), str)
                    or not isinstance(options, list) or len(options) != 4
                    or any(not isinstance(option, str) or not option.strip() for option in options)
                    or len({option.strip().casefold() for option in options}) != 4
                    or type(answer_index) is not int or answer_index not in range(4)
                    or not isinstance(item.get('explanation'), str)):
                raise ValueError('Invalid question format')
            normalized.append({
                'category': item['category'].strip(),
                'question': item['question'].strip(),
                'options': [option.strip() for option in options],
                'answer_index': answer_index,
                'explanation': item['explanation'].strip(),
            })
        request.session['active_quiz'] = normalized
        request.session['recent_quiz_questions'] = (recent + [q['question'] for q in normalized])[-25:]
        request.session.modified = True
        # Keep the correct answers and explanations on the server until scoring.
        public_questions = [
            {key: question[key] for key in ('category', 'question', 'options')}
            for question in normalized
        ]
        return JsonResponse({'questions': public_questions})
    except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError, KeyError,
            IndexError, TypeError, json.JSONDecodeError) as error:
        if isinstance(error, (RuntimeError, HTTPError)):
            return _gemini_error_response(error)
        return JsonResponse({'error': 'Gemini returned an invalid quiz. Please generate a new one.'}, status=502)


@login_required
def score_quiz(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Use POST to submit answers.'}, status=405)
    quiz_data = request.session.get('active_quiz')
    if not quiz_data:
        return JsonResponse({'error': 'Your quiz expired. Generate a new quiz and try again.'}, status=409)
    try:
        submitted = json.loads(request.body.decode('utf-8')).get('answers')
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'The submitted answers were not valid.'}, status=400)
    if (not isinstance(submitted, list) or len(submitted) != len(quiz_data)
            or any(type(answer) is not int or answer not in range(4) for answer in submitted)):
        return JsonResponse({'error': 'Please answer every question before submitting.'}, status=400)
    evaluation_input = [
        {
            'question': q['question'],
            'options': q['options'],
            'correct_option': q['options'][q['answer_index']],
            'selected_option': q['options'][answer],
            'explanation': q['explanation'],
        }
        for q, answer in zip(quiz_data, submitted)
    ]
    prompt = (
        'Score this completed multiple-choice quiz using the supplied correct_option for each item. '
        'Return one result per question in order, mark correct true only when selected_option equals '
        'correct_option, and calculate score as the number correct. Do not change or reinterpret the key. '
        f'Quiz data: {json.dumps(evaluation_input, ensure_ascii=False)}'
    )
    try:
        evaluation = _gemini_json(prompt, QUIZ_SCORE_SCHEMA)
        results = evaluation.get('results')
        if not isinstance(results, list) or len(results) != len(quiz_data):
            raise ValueError('Invalid result count')
        verified = [answer == question['answer_index'] for answer, question in zip(submitted, quiz_data)]
        verified_score = sum(verified)
        # Verify Gemini's calculation against the server-held answer key before showing it.
        if type(evaluation.get('score')) is not int or evaluation['score'] != verified_score:
            raise ValueError('Score did not match answer key')
        results = [
            {
                'correct': is_correct,
                'explanation': question['explanation'],
                'question': question['question'],
                'selected_option': question['options'][answer],
                'correct_option': question['options'][question['answer_index']],
            }
            for question, answer, is_correct in zip(quiz_data, submitted, verified)
        ]
        request.session.pop('active_quiz', None)
        return JsonResponse({'score': evaluation['score'], 'results': results})
    except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError, KeyError,
            IndexError, TypeError, json.JSONDecodeError) as error:
        if isinstance(error, (RuntimeError, HTTPError)):
            return _gemini_error_response(error)
        return JsonResponse({'error': 'Gemini could not score this quiz. Please retry.'}, status=502)


@staff_required
def response_audio(request, response_id):
    response = get_object_or_404(SurveyResponse, pk=response_id)
    if not response.audio_blob:
        raise Http404('No database audio is attached to this response.')
    audio = HttpResponse(response.audio_blob, content_type=response.audio_mime_type or 'audio/webm')
    audio['Content-Disposition'] = 'inline'
    audio['X-Content-Type-Options'] = 'nosniff'
    return audio


@staff_required
def results(request):
    responses = SurveyResponse.objects.all()
    response_id = request.session.get('survey_response_id')
    response = responses.filter(pk=response_id).first() if response_id else responses.first()
    aggregate = SurveyResponse.objects.aggregate(
        total=Count('id'),
        average_rating=Avg('survey_rating'),
        average_importance=Avg('q42'),
    )
    awareness_fields = [
        ('q8', 'Knows Constitution?'), ('q9', 'Studied constitutional values'),
        ('q10', 'Constitution in own words'), ('q11', 'Constitution effective date'),
        ('q12', 'Father of Constitution'), ('q13', 'Number of articles'),
        ('q14', 'Film / audio response'),
    ]
    duties_fields = [
        ('q21', 'Awareness of duties'), ('q22', 'Follows duties'),
        ('q23', 'Most important duty'), ('q24', 'National anthem conduct'),
        ('q25', 'Littering / property'), ('q26', 'Best / worst duties'),
        ('q27', 'Equal opportunities?'), ('q28', 'Discrimination experienced?'),
        ('q29', 'Fair laws?'), ('q30', 'Reservation opinion'), ('q31', "Women's voting pride (1–5)"),
    ]
    opinions_fields = [
        ('q37', "Indians' constitutional awareness (general)"), ('q38', 'Teach more in schools?'),
        ('q39', 'Best improvement method'), ('q40', 'Constitution interesting? /5'),
        ('q41', 'Too politicized?'), ('q42', 'Importance in daily life /5'),
        ('survey_rating', 'Survey rating'), ('q43', 'Suggestions to promote awareness'),
        ('q44', 'Personal takeaway'), ('q45', 'Proposed article'), ('audio_status', 'Audio response'),
    ]
    def fields_for(item, definitions):
        return [{'label': label, 'value': getattr(item, key)} for key, label in definitions]

    context = {
        'response': response,
        'responses': responses,
        'total_responses': aggregate['total'] or 0,
        'average_rating': aggregate['average_rating'],
        'average_importance': aggregate['average_importance'],
        'respondent_count': responses.count(),
        'institution_count': responses.exclude(college='').values('college').distinct().count(),
        'aware_count': responses.filter(q8__iexact='Yes').count(),
        'education_count': responses.filter(q27__icontains='yes').count(),
        'audio_count': responses.filter(Q(audio_blob__isnull=False) | ~Q(audio_url='')).count(),
        'city_count': None,
        'duty_awareness_count': responses.filter(q21__iexact='yes').count(),
        'discrimination_count': responses.filter(q28__iexact='yes').count(),
        'common_method': Counter(
            value for value in responses.exclude(q39='').values_list('q39', flat=True)
        ).most_common(1),
        'response_details': [
            {'item': item, 'awareness': fields_for(item, awareness_fields),
             'duties': fields_for(item, duties_fields), 'opinions': fields_for(item, opinions_fields),
             'has_audio': bool(item.audio_blob or item.audio_url),
             'initials': ''.join(part[0] for part in (item.name or 'Anonymous').split()[:2]).upper(),
             'aware': item.q8 and item.q8.lower() == 'yes'}
            for item in responses
        ],
        'notable_quotes': [
            item for item in responses.exclude(q10='').order_by('-created_at')[:6]
        ],
    }
    return render(request, 'pages/results.html', context)
