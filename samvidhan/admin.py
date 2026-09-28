from django.contrib import admin

from .models import SurveyResponse


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
	list_display = ('created_at', 'name', 'email', 'gender', 'course', 'college', 'survey_rating')
	list_filter = ('gender', 'course', 'year', 'created_at')
	search_fields = ('name', 'email', 'college', 'q10', 'q43', 'q44', 'q45')
	ordering = ('-created_at',)
	readonly_fields = ('created_at',)
