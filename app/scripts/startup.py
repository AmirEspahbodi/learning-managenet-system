from random import randint
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Q
from accounts.models import User, Roles, VerificationStatus
from trs.models import Room, Semester, TimeSlot, Semseters, Days_Of_Week
from courses.models import (
    CourseTitle,
    Course,
    CourseTime,
    MemberShip,
    MemberShipRoles,
    Session,
)
from assignments.models import (
    Assignment,
    FTQuestion as AssignmentFTQuestion,
    FTQuestionAnswer as AssignmentFTQuestionAnswer,
)
from exams.models import (
    Exam,
    FTQuestion as ExamFTQuestion,
    FTQuestionAnswer as ExamFTQuestionAnswer,
)
from teachers.models import Teacher
from students.models import Student


def run():
    superuser = User.objects.create_superuser(
        "admin",
        email="admin@admin.admin",
        password="Abcd_1234",
        first_name="admin",
        last_name="espahbodi",
        phone_number="+989013971301",
    )
    print(f"superuser {superuser} created!\n\n")
    superuser.role = Roles.TEACHER * superuser.role
    superuser.save()
    users: list[User] = [
        User.objects.create_user(
            f"teacher{i}" if i < 3 else f"student{i-3}",
            email=f"teacher{i}@teacher.teacher"
            if i < 3
            else f"student{i-3}@student.student",
            password=f"Abcd_1234",
            first_name=f"teacher{i}" if i < 3 else f"student{i-3}",
            last_name=f"teacher" if i < 3 else f"student",
            phone_number=f"+98901397140{i}" if i < 3 else f"+98901397150{i-3}",
            role=Roles.NOT_DEFINED,
            verification_status=VerificationStatus.BOTH,
        )
        for i in range(10)
    ]
    print(f"users {users} created!\n\n")

    student: list[Student] = [
        Student.objects.create(user=users[i], school="some", degree=1, field="some")
        for i in range(3, 10)
    ]
    print(f"student {student} created!\n\n")

    teachers: list[Teacher] = [
        Teacher.objects.create(user=users[i], experience=30) for i in range(3)
    ]
    print(f"teachers {teachers} created!\n\n")

    rooms: list[Room] = [
        Room.objects.create(room_title="room 1", capacity=45),
        Room.objects.create(room_title="room 2", capacity=50),
    ]
    print(f"rooms {rooms} created!\n\n")

    semesters: list[Semester] = [
        Semester.objects.create(year="1402-1403", semester=Semseters.FIRST_SEMESTER),
        Semester.objects.create(year="1402-1403", semester=Semseters.SECOND_SEMESTER),
    ]
    print(f"semesters {semesters} created!\n\n")

    times = [
        {"start": "08:00:00", "end": "09:30:00"},
        {"start": "10:00:00", "end": "11:30:00"},
        {"start": "14:00:00", "end": "15:30:00"},
    ]
    timeslots: list[TimeSlot] = [
        TimeSlot.objects.create(
            room_number=rooms[i], day=day_of_week, start=time["start"], end=time["end"]
        )
        for time in times
        for i in range(0, 2)
        for day_of_week in [
            Days_Of_Week.MONDAY,
            Days_Of_Week.THURSDAY,
            Days_Of_Week.TUESDAY,
            Days_Of_Week.SUNDAY,
        ]
    ]
    print(f"timeslots {timeslots} created!\n\n")

    coursetitles: list[CourseTitle] = [
        CourseTitle.objects.create(title="math"),
        CourseTitle.objects.create(title="physic"),
        CourseTitle.objects.create(title="algebra"),
    ]
    print(f"coursetitles {coursetitles} created!\n\n")

    courses: list[Course] = [
        Course.objects.create(
            group_course_number=j,
            course_title=coursetitles[i],
            semester=semesters[0],
            start_date=date(year=2023, month=6, day=1),
            end_date=date(year=2023, month=9, day=1),
            tuition=10000000,
            percentage_required_for_tuition=27.5,
        )
        for j in range(1, 4)
        for i in range(0, 3)
    ]
    print(f"courses {courses} created!\n\n")

    student_membership: list[MemberShip] = [
        MemberShip.objects.create(
            user=student[j].user, course=courses[i], role=MemberShipRoles.STUDENT
        )
        for j in range(0, len(student))
        for i in range(0, len(courses))
        if (i + j < len(student))
    ]
    print(f"student_membership {student_membership} created!\n\n")

    teacher_membership: list[MemberShip] = [
        MemberShip.objects.create(
            user=teachers[i].user, course=courses[i], role=MemberShipRoles.TEACHER
        )
        for i in range(min(len(teachers), len(courses)))
    ]
    print(f"student_membership {teacher_membership} created!\n\n")

    course_time: list[CourseTime] = [
        CourseTime.objects.create(
            course=courses[index % len(courses)],
            semester=courses[index % len(courses)].semester,
            time_slot=timeslots[index],
        )
        for index in range(len(timeslots))
    ]
    print(f"course_time {course_time} created!\n\n")
    sessions = Session.objects.filter(
        Q(session_number=0) | Q(session_number=1) | Q(session_number=2)
    ).all()
    current_time = timezone.now()
    two_week_later = current_time + timedelta(weeks=2)
    for session in sessions:
        exam = Exam.objects.create(
            session=session,
            title="exam",
            description=f"simple exam for {session}",
            exam_number=0,
            start_at=current_time,
            end_at=two_week_later,
        )
        exam_questions = []
        for i in range(randint(3, 5)):
            exam_questions.append(
                ExamFTQuestion(
                    exam=exam,
                    title="simple question",
                    text="simple question {i} for exam {exam}",
                    start_at=current_time,
                    end_at=two_week_later,
                )
            )
        exam_questions = ExamFTQuestion.objects.bulk_create(exam_questions)
        exam_question_answers = []
        for exam_question in exam_questions:
            exam_question_answers.append(
                ExamFTQuestionAnswer(
                    ft_question=exam_question,
                    answer_text=f"simple answer for {exam_question}",
                    accessing_at=two_week_later,
                )
            )
        ExamFTQuestionAnswer.objects.bulk_create(exam_question_answers)
        assignment = Assignment.objects.create(
            session=session,
            title="assignment",
            description=f"simple assignment for {session}",
            assignment_number=0,
            start_at=current_time,
            end_at=two_week_later,
        )
        assignment_questions = []
        for i in range(randint(3, 5)):
            assignment_questions.append(
                AssignmentFTQuestion(
                    assignment=assignment,
                    title="simple question",
                    text="simple question {i} for assignment {assignment}",
                    start_at=current_time,
                    end_at=two_week_later,
                )
            )
        assignment_questions = AssignmentFTQuestion.objects.bulk_create(
            assignment_questions
        )
        assignment_question_answers = []
        for assignment_question in assignment_questions:
            assignment_question_answers.append(
                AssignmentFTQuestionAnswer(
                    ft_question=assignment_question,
                    answer_text=f"simple answer for {assignment_question}",
                    accessing_at=two_week_later,
                )
            )
        AssignmentFTQuestionAnswer.objects.bulk_create(assignment_question_answers)
    print(f"for sessions {sessions} exam ans assignment created")
