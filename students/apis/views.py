# from rest_framework.response import Response
# from rest_framework.views import APIView

# from trs.models import Semester
# from students.models import StudentTakes
# from courses.models import Session
# from django.db.models import Q
# from trs.apis.serializers import TimeSlotSerializer, SemesterSerializer
# from courses.apis.serializers import StudentCourseSerializer1, SessionSerializer1, CourseSerializer
# from practices.models import Practice
# from exams.models import Exam
# from exams.serializers import StudentExamSerializer1
# from practices.serializers import StudentPracticeSerializer1

# import pytz
# from datetime import date, timedelta, datetime

# class StudentHomeAPIView(APIView):
#     def get(self, request, *arg, **kwarg):
#         semester = Semester.objects.last()
#         studentTakes = StudentTakes.objects.filter(
#             Q(student=request.user.student_user) & Q(group_course__semester=semester))
        
#         student_group_courses = studentTakes.values('group_course')
#         student_group_courses_sessions = Session.objects.filter(group_course__in=student_group_courses)
        
        
#         current_datetime = pytz.UTC.localize(datetime.utcnow())
#         current_date = date.today()
#         next_week_date = current_date+timedelta(days=7)

#         closest_student_group_course_sessions = [  
#             {
#                 "group_course": {
#                     "course":CourseSerializer(session.group_course.course).data,
#                     **StudentGroupCourseSerializer1(session.group_course).data
#                 },
#                 **SessionSerializer1(session).data,
#                 "time_slot": TimeSlotSerializer(session.time_slot).data
#             }
#             for session in
#             student_group_courses_sessions.filter(
#                 Q(Q(date=current_date) & Q(time_slot__start__lte=current_datetime)) |
#                 Q(Q(date__gt=current_date) & Q(date__lte=next_week_date))
#             ).order_by('date', 'time_slot__start').iterator()
#         ]

#         student_started_exams = [
#             {
#                 **StudentExamSerializer1(instance=exam).data,
#                 'remaining_time':exam.end_datetime-current_datetime, 
#                 'group_course': {
#                     'course': CourseSerializer(exam.session.group_course.course).data,
#                     **StudentGroupCourseSerializer1(exam.session.group_course).data
#                 }
#             } 
#             for exam in Exam.objects.filter(
#             Q(session__in=student_group_courses_sessions) &
#             Q(end_datetime__gte=current_datetime)&
#             Q(start_datetime__lte=current_datetime)).iterator()
#         ]
        
#         student_practices = [
#             {
#                 **StudentPracticeSerializer1(instance=practice).data,
#                 'remaining_time':practice.end_datetime-current_datetime,
#                 'group_course': {
#                     'course': CourseSerializer(practice.session.group_course.course).data,
#                     **StudentGroupCourseSerializer1(practice.session.group_course).data,
#                 }
#             } 
#             for practice in  Practice.objects.filter(
#             Q(session__in=student_group_courses_sessions) &
#             Q(end_datetime__gte=current_datetime) &
#             Q(start_datetime__lte=current_datetime)).iterator()
#         ]
        
#         group_courses = [
#             {
#                 ** StudentGroupCourseSerializer1(st_take.group_course).data,
#                 "semester": SemesterSerializer(st_take.group_course.semester).data,
#                 'course': CourseSerializer(st_take.group_course.course).data,
#             }
#             for st_take in studentTakes
#         ]

#         context = {}
#         context['group_courses'] = group_courses
#         context['practices'] = student_practices
#         context['closest_student_group_course_sessions'] = closest_student_group_course_sessions
#         context['started_exams'] = student_started_exams
#         return Response(data=context)
