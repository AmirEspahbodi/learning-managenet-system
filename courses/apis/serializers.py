from rest_framework.serializers import ModelSerializer
from courses.models import Course, Session, CourseTitle, CourseTime
from trs.apis.serializers import TimeSlotSerializer, SemesterSerializer
from teachers.apis.serialisers import TeacherSerializer
from assignments.apis.serializers import AssignmentSerializer
from exams.apis.serializers import ExamSerializer

class CourseTimeSerializer(ModelSerializer):
    semester = SemesterSerializer()
    time_slot = TimeSlotSerializer()
    class Meta:
        model = CourseTime
        fields = ('semester', 'time_slot')

class CourseTitleSerializer(ModelSerializer):
    class Meta:
        model = CourseTitle
        fields = ('title',)

class CourseSerializer(ModelSerializer):
    course_title = CourseTitleSerializer()
    semester = SemesterSerializer()
    teacher = TeacherSerializer()
    class Meta:
        model = Course
        fields = ('id', 'course_title', 'teacher', 'group_course_number', 'semester')


class CourseDetailSerializer(CourseSerializer):
    course_times = CourseTimeSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = ('id', 'course_title', 'teacher', 'group_course_number', 'semester', 'start_date', "end_date", 'course_times')

class SessionSerializer(ModelSerializer):
    time_slot = TimeSlotSerializer(read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)
    exams = ExamSerializer(many=True, read_only=True)
    class Meta:
        model = Session
        fields = ('id', 'course', 'session_number', 'date', 'time_slot', 'description', 'assignments', 'exams')
