# Generated by Django 4.2.4 on 2023-08-27 18:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0002_remove_course_unique_course_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="course",
            old_name="percentage_required_for_tuition",
            new_name="tuition_percentage",
        ),
    ]