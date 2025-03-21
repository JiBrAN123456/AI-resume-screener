# Generated by Django 5.1.7 on 2025-03-17 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_user_managers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("admin", "Admin"), ("hr", "HR"), ("CANDIDATE", "Candidate")],
                default="CANDIDATE",
                max_length=20,
            ),
        ),
    ]
