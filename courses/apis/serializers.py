from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer
from courses.models import Course, Session, CourseTitle, CourseTime
from trs.apis.serializers import TimeSlotSerializer, SemesterSerializer
from teachers.apis.serialisers import TeacherSerializer
from assignments.apis.serializers import AssignmentSerializer
from exams.apis.serializers import ExamSerializer
from students.models import StudentEnroll


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
        fields = ('id', 'course_title', 'teacher',
                  'group_course_number', 'semester')


class CourseSerializerSlim(ModelSerializer):
    course_title = CourseTitleSerializer()
    semester = SemesterSerializer()

    class Meta:
        model = Course
        fields = ('id', 'course_title',
                  'group_course_number', 'semester')


class CourseDetailSerializer(CourseSerializer):
    course_times = CourseTimeSerializer(many=True, read_only=True)

    # def __init__(self, instance=None, student=None,  data=..., **kwargs):
    #     self.studentsEnroll = StudentEnroll.objects.filter(course=instance)
    #     self.student = student
    #     super().__init__(instance, data, **kwargs)

    class Meta:
        model = Course
        fields = ('id', 'course_title', 'teacher', 'group_course_number',
                  'semester', 'start_date', "end_date", 'course_times')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        students_enrolle = StudentEnroll.objects.filter(course=instance).all()
        representation['enrolled_cout'] = students_enrolle.count()
        representation['is_enrolled'] = filter(
            lambda student_enroll: student_enroll.student == self.context['student'], students_enrolle) is not None
        return representation


class SessionSerializer(ModelSerializer):
    time_slot = TimeSlotSerializer(read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)
    exams = ExamSerializer(many=True, read_only=True)
    course = CourseSerializerSlim()

    class Meta:
        model = Session
        fields = ('id', 'course', 'session_number', 'date',
                  'time_slot', 'description', 'assignments', 'exams')
