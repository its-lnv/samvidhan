from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('samvidhan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveyresponse',
            name='audio_blob',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='audio_mime_type',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
