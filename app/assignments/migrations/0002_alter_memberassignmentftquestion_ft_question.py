# Generated by Django 4.2.4 on 2023-09-10 08:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("assignments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="memberassignmentftquestion",
            name="ft_question",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="member_answers",
                to="assignments.ftquestion",
            ),
        ),
    ]