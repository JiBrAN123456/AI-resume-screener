# Generated by Django 5.1.7 on 2025-03-22 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resumes", "0003_rename_uplaoded_at_resume_uploaded_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resume",
            name="phone",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
