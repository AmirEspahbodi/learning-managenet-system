# Generated by Django 4.2.4 on 2023-08-26 10:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Assignment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("title", models.CharField(blank=True, max_length=255, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "assignment_number",
                    models.PositiveSmallIntegerField(
                        blank=True, editable=False, null=True
                    ),
                ),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField()),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignments",
                        to="courses.session",
                    ),
                ),
            ],
            options={
                "db_table_comment": "assignment for each session of course",
            },
        ),
        migrations.CreateModel(
            name="FTQuestion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("title", models.CharField(blank=True, max_length=255, null=True)),
                ("text", models.TextField(blank=True, null=True)),
                (
                    "file",
                    models.FileField(
                        blank=True, null=True, upload_to="assignment/questions/"
                    ),
                ),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField()),
                (
                    "assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ftquestions",
                        to="assignments.assignment",
                    ),
                ),
            ],
            options={
                "db_table": "assignments_ftquestion",
                "db_table_comment": "Each assignment can have several file/text type questions. This table stores questions of this type for each assignment",
            },
        ),
        migrations.CreateModel(
            name="MemberTakeAssignment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("last_visit", models.DateTimeField(auto_now_add=True)),
                ("finish_at", models.DateTimeField(auto_now=True)),
                (
                    "score",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                (
                    "assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignment_members",
                        to="assignments.assignment",
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="courses.membership",
                    ),
                ),
            ],
            options={
                "db_table": "assignments_member_take_assignment",
                "db_table_comment": "a table betwen student takes and assignment. It shows that the student participated in the assignment",
            },
        ),
        migrations.CreateModel(
            name="MemberAssignmentFTQuestion",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("answered_text", models.TextField(blank=True, null=True)),
                (
                    "answered_file",
                    models.FileField(
                        blank=True, null=True, upload_to="assignment/students/answers/"
                    ),
                ),
                (
                    "score",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=6, null=True
                    ),
                ),
                (
                    "ft_question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="assignments.ftquestion",
                    ),
                ),
                (
                    "member_take_assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="member_take_assignment_ftquestions",
                        to="assignments.membertakeassignment",
                    ),
                ),
            ],
            options={
                "db_table": "assignments_member_assignment_fttquestion",
                "db_table_comment": "This table stores the student's answer to the assignment file/text question",
            },
        ),
        migrations.CreateModel(
            name="FTQuestionAnswer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("answer_text", models.TextField(blank=True, null=True)),
                (
                    "answer_file",
                    models.FileField(
                        blank=True, null=True, upload_to="assignment/teacher/answers/"
                    ),
                ),
                ("accessing_at", models.DateTimeField(blank=True, null=True)),
                (
                    "ft_question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ftquestion_answers",
                        to="assignments.ftquestion",
                    ),
                ),
            ],
            options={
                "db_table": "assignments_ftquestion_answer",
                "db_table_comment": "answer of the file/text type questions",
            },
        ),
        migrations.AddConstraint(
            model_name="membertakeassignment",
            constraint=models.UniqueConstraint(
                fields=("assignment", "member"),
                name="unique_assignments_member_take_assignment",
            ),
        ),
        migrations.AddConstraint(
            model_name="memberassignmentftquestion",
            constraint=models.UniqueConstraint(
                fields=("member_take_assignment", "ft_question"),
                name="unique_member_assignment_studen_assignment_fttquestion",
            ),
        ),
    ]