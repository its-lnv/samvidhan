from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SurveyResponse(models.Model):
	GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
	COURSE_CHOICES = [
		('Commerce', 'Commerce'),
		('Engineering / Tech', 'Engineering / Tech'),
		('Science', 'Science'),
		('Other', 'Other'),
	]
	YEAR_CHOICES = [
		('1st Year', '1st Year'), ('2nd Year', '2nd Year'),
		('3rd Year', '3rd Year'), ('4th Year', '4th Year'),
		('5th Year', '5th Year'), ('PG / Masters', 'PG / Masters'),
		('PhD', 'PhD'), ('Pass out / Working', 'Pass out / Working'),
	]

	name = models.CharField(max_length=150, blank=True)
	age = models.PositiveSmallIntegerField(
		blank=True, null=True, validators=[MinValueValidator(10), MaxValueValidator(99)]
	)
	gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
	email = models.EmailField()
	course = models.CharField(max_length=40, choices=COURSE_CHOICES)
	college = models.CharField(max_length=200, blank=True)
	year = models.CharField(max_length=30, choices=YEAR_CHOICES)

	q8 = models.CharField(max_length=120, blank=True)
	q9 = models.CharField(max_length=120, blank=True)
	q10 = models.TextField(blank=True)
	q11 = models.CharField(max_length=180, blank=True)
	q12 = models.CharField(max_length=180, blank=True)
	q13 = models.CharField(max_length=180, blank=True)
	q14 = models.TextField(blank=True)
	q21 = models.CharField(max_length=120, blank=True)
	q22 = models.CharField(max_length=120, blank=True)
	q23 = models.CharField(max_length=180, blank=True)
	q24 = models.CharField(max_length=180, blank=True)
	q25 = models.CharField(max_length=120, blank=True)
	q26 = models.TextField(blank=True)
	q27 = models.CharField(max_length=120, blank=True)
	q28 = models.CharField(max_length=180, blank=True)
	q29 = models.CharField(max_length=120, blank=True)
	q30 = models.CharField(max_length=180, blank=True)
	q31 = models.PositiveSmallIntegerField(
		blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
	)
	q37 = models.CharField(max_length=150, blank=True)
	q38 = models.CharField(max_length=150, blank=True)
	q39 = models.CharField(max_length=180, blank=True)
	q40 = models.PositiveSmallIntegerField(
		blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
	)
	q41 = models.CharField(max_length=180, blank=True)
	q42 = models.PositiveSmallIntegerField(
		blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
	)
	q43 = models.TextField(blank=True)
	q44 = models.TextField(blank=True)
	q45 = models.TextField(blank=True)
	survey_rating = models.PositiveSmallIntegerField(
		blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
	)
	audio_url = models.URLField(blank=True)
	audio_blob = models.BinaryField(blank=True, null=True)
	audio_mime_type = models.CharField(max_length=100, blank=True)
	audio_status = models.CharField(max_length=120, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.name or "Anonymous"} - {self.created_at:%Y-%m-%d %H:%M}'
