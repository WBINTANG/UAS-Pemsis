# Generated by Django 5.1.6 on 2025-06-26 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms_core', '0004_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_moderated',
            field=models.BooleanField(default=False, verbose_name='Sudah Dimoderasi'),
        ),
    ]
