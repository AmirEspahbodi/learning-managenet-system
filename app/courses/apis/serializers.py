from django.db.models import Q
from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer
from courses.models import Course, Session, CourseTitle, CourseTime, MemberShip, MemberShipRoles
from trs.apis.serializers import TimeSlotSerializer, SemesterSerializer
from teachers.apis.serialisers import TeacherSerializer
from assignments.apis.serializers import AssignmentSerializer
from exams.apis.serializers import ExamSerializer
from students.models import StudentEnroll
from django.contrib.auth import get_user_model
User = get_user_model()

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


class MemberShipSerializer(ModelSerializer):
    
    class Meta:
        model = MemberShip
        fields = ('role', 'user')
        
class CourseSerializer(ModelSerializer):
    course_title = CourseTitleSerializer()
    semester = SemesterSerializer()
    course_times = CourseTimeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ('id', 'course_title','course_times', 
                  'group_course_number', 'semester')


class CourseSerializerSlim(ModelSerializer):
    course_title = CourseTitleSerializer()
    semester = SemesterSerializer()
    
    class Meta:
        model = Course
        fields = ('id', 'course_title',
                  'group_course_number', 'semester')


class CourseDetailSerializer(CourseSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        kwargs
        super().__init__(instance=instance, data=data, **kwargs)

    class Meta:
        model = Course
        fields = ('id', 'course_title', 'group_course_number',
                  'semester', 'start_date', "end_date", 'course_times')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        course_id = self.context['course_id']
        members:list[MemberShip] = MemberShip.objects.filter(Q(course=course_id) & (Q(role=MemberShipRoles.TEACHER) | Q(role=MemberShipRoles.TEACHING_ASSISTANT) | Q(role=MemberShipRoles.INSTRUCTOR))).values()
        students_count = MemberShip.objects.filter(Q(course=course_id) & Q(role=MemberShipRoles.STUDENT)).count()
        representation['enrolled_cout'] = students_count
        representation['is_member'] = False if self.context['is_student'] is not None else MemberShip.objects.filter(Q(course=course_id) & Q(user=self.context.get('user_id'))).exists()
        teacher_ids = [obj['user_id'] for obj in filter(lambda x: x['role'] == MemberShipRoles.TEACHER ,members)]
        instructors_ids = [obj['user_id'] for obj in filter(lambda x: x['role'] == MemberShipRoles.INSTRUCTOR,members)]
        teaching_assistants_ids = [obj['user_id'] for obj in filter(lambda x: x['role'] == MemberShipRoles.TEACHING_ASSISTANT ,members)]
        non_student_members = User.objects.filter(id__in=[*teacher_ids,*instructors_ids,*teaching_assistants_ids]).values('id', 'first_name', 'last_name')
        representation['teachers'] = [member for member in non_student_members if member['id'] in teacher_ids]
        representation['instructors'] = [member for member in non_student_members if member['id'] in instructors_ids]
        representation['teaching_assistants'] = [member for member in non_student_members if member['id'] in teaching_assistants_ids]
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
