from accounts.models import User, Roles
from trs.models import Room, Semester, TimeSlot, Semseters,Days_Of_Week
from courses.models import CourseTitle, Course, CourseTime
from teachers.models import Teacher

def run():
    superuser = User.objects.create_superuser(
            'amir',
            email='amir@amir.amir',
            password='amir8731',
            first_name="amir",
            last_name='espahbodi',
            phone_number='+989013971301',
        )
    print(f"superuser {superuser} created!\n\n")

    users: list[User] = [
        User.objects.create_user(
            'amir1',
            email='amir1@amir.amir',
            password='Abcd_1234',
            first_name="amir1",
            last_name='espahbodi1',
            phone_number='+989013971302',
            role=Roles.NOT_DEFINED
        ),
        User.objects.create_user(
            'amir2',
            email='amir2@amir.amir',
            password='Abcd_1234',
            first_name="amir2",
            last_name='espahbodi2',
            phone_number='+989013971303',
            role=Roles.NOT_DEFINED
        ),
        User.objects.create_user(
            'amir3',
            email='amir3@amir.amir',
            password='Abcd_1234',
            first_name="amir3",
            last_name='espahbodi3',
            phone_number='+989013971304',
            role=Roles.NOT_DEFINED
        ),
        User.objects.create_user(
            'amir4',
            email='amir4@amir.amir',
            password='Abcd_1234',
            first_name="amir4",
            last_name='espahbodi4',
            phone_number='+989013971305',
            role=Roles.NOT_DEFINED
        ),
        User.objects.create_user(
            'amir5',
            email='amir5@amir.amir',
            password='Abcd_1234',
            first_name="amir5",
            last_name='espahbodi5',
            phone_number='+989013971306',
            role=Roles.NOT_DEFINED
        ),
    ]
    print(f"users {users} created!\n\n")

    rooms: list[Room] = [
        Room.objects.create(
            room_title = "room 1",
            capacity = 45
        ),
        Room.objects.create(
            room_title = "room 2",
            capacity = 50
        )
    ]
    print(f"rooms {rooms} created!\n\n")

    semesters: list[Semester] = [
        Semester.objects.create(
            year = '1402-1403',
            semester = Semseters.FIRST_SEMESTER
        ),
        Semester.objects.create(
            year = '1402-1403',
            semester = Semseters.SECOND_SEMESTER
        )
    ]
    print(f"semesters {semesters} created!\n\n")

    timeslots:list[TimeSlot] = [
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.MONDAY,
            start='08:00:00',
            end='09:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.MONDAY,
            start='10:00:00',
            end='11:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.MONDAY,
            start='14:00:00',
            end='15:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.MONDAY,
            start='08:00:00',
            end='09:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.MONDAY,
            start='10:00:00',
            end='11:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.MONDAY,
            start='14:00:00',
            end='15:30:00'
        ),
        # ------------------------------------
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.TUESDAY,
            start='08:00:00',
            end='09:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.TUESDAY,
            start='10:00:00',
            end='11:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.TUESDAY,
            start='14:00:00',
            end='15:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.TUESDAY,
            start='08:00:00',
            end='09:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.TUESDAY,
            start='10:00:00',
            end='11:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.TUESDAY,
            start='14:00:00',
            end='15:30:00'
        ),
        # ------------------------------------
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.THURSDAY,
            start='08:00:00',
            end='09:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.THURSDAY,
            start='10:00:00',
            end='11:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.THURSDAY,
            start='14:00:00',
            end='15:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.THURSDAY,
            start='08:00:00',
            end='09:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.THURSDAY,
            start='10:00:00',
            end='11:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.THURSDAY,
            start='14:00:00',
            end='15:30:00'
        ),
        # ------------------------------------
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.SUNDAY,
            start='08:00:00',
            end='09:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.SUNDAY,
            start='10:00:00',
            end='11:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[0],
            day=Days_Of_Week.SUNDAY,
            start='14:00:00',
            end='15:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.SUNDAY,
            start='08:00:00',
            end='09:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.SUNDAY,
            start='10:00:00',
            end='11:30:00'
        ),
        TimeSlot.objects.create(
            room_number=rooms[1],
            day=Days_Of_Week.SUNDAY,
            start='14:00:00',
            end='15:30:00'
        ),
        # ------------------------------------
    ]
    print(f"timeslots {timeslots} created!\n\n")

    
    teachers: list[Teacher] = [
        Teacher.objects.create(
            user=users[0],
            experience=20,
        ),
        Teacher.objects.create(
            user=users[1],
            experience=25
        ),
        Teacher.objects.create(
            user=users[2],
            experience=30
        ),
    ]
    print(f"teachers {teachers} created!\n\n")

        
    coursetitles:list[CourseTitle] = [
        CourseTitle.objects.create(
            title='math'
        ),
        CourseTitle.objects.create(
            title='physic'
        ),
        CourseTitle.objects.create(
            title='algebra'
        )
    ]
    print(f"coursetitles {coursetitles} created!\n\n")

    courses: list[Course] = [
        Course.objects.create(
            group_course_number=1,
            course_title=coursetitles[0],
            semester=semesters[0],
            teacher=teachers[0],
            start_date='2023-9-1',
            end_date='2023-12-29',
            tuition=10000000,
            percentage_required_for_tuition=27.5
        ),
        Course.objects.create(
            group_course_number=2,
            course_title=coursetitles[0],
            semester=semesters[0],
            teacher=teachers[0],
            start_date='2023-9-1',
            end_date='2023-12-29',
            tuition=10000000,
            percentage_required_for_tuition=27.5
        ),
        Course.objects.create(
            group_course_number=3,
            course_title=coursetitles[0],
            semester=semesters[0],
            teacher=teachers[0],
            start_date='2023-9-1',
            end_date='2023-12-29',
            tuition=10000000,
            percentage_required_for_tuition=27.5
        ),
        Course.objects.create(
            group_course_number=1,
            course_title=coursetitles[1],
            semester=semesters[0],
            teacher=teachers[1],
            start_date='2023-9-1',
            end_date='2023-12-29',
            tuition=10000000,
            percentage_required_for_tuition=27.5
        ),
        Course.objects.create(
            group_course_number=2,
            course_title=coursetitles[1],
            semester=semesters[0],
            teacher=teachers[1],
            start_date='2023-9-1',
            end_date='2023-12-29',
            tuition=10000000,
            percentage_required_for_tuition=27.5
        ),
        Course.objects.create(
            group_course_number=3,
            course_title=coursetitles[1],
            semester=semesters[0],
            teacher=teachers[1],
            start_date='2023-9-1',
            end_date='2023-12-29',
            tuition=10000000,
            percentage_required_for_tuition=27.5
        ),        
        Course.objects.create(
            group_course_number=1,
            course_title=coursetitles[2],
            semester=semesters[0],
            teacher=teachers[2],
            start_date='2023-9-1',
            end_date='2023-12-29',
            tuition=10000000,
            percentage_required_for_tuition=27.5
        ),
        Course.objects.create(
            group_course_number=2,
            course_title=coursetitles[2],
            semester=semesters[0],
            teacher=teachers[2],
            start_date='2023-9-1',
            end_date='2023-12-29',
            tuition=10000000,
            percentage_required_for_tuition=27.5
        ),
        Course.objects.create(
            group_course_number=3,
            course_title=coursetitles[2],
            semester=semesters[0],
            teacher=teachers[2],
            start_date='2023-9-1',
            end_date='2023-12-29',
            tuition=10000000,
            percentage_required_for_tuition=27.5
        ),
    ]
    print(f"courses {courses} created!\n\n")

    course_time: list[CourseTime]=[]
    for index in range(len(timeslots)):
        course_time.append(
            CourseTime.objects.create(
                course=courses[index % len(courses)],
                semester=courses[index % len(courses)].semester,
                time_slot=timeslots[index]
            )
        )
    print(f"course_time {course_time} created!\n\n")
    