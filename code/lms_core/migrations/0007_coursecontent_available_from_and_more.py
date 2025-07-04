# Generated by Django 5.1.6 on 2025-06-26 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms_core', '0006_coursecontent_release_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursecontent',
            name='available_from',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Tersedia Mulai'),
        ),
        migrations.AddField(
            model_name='coursecontent',
            name='available_to',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Tersedia Sampai'),
        ),
    ]
