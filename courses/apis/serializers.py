from rest_framework.serializers import ModelSerializer
from courses.models import Course, Session, CourseTitle

class StudentCourseSerializer1(ModelSerializer):
    class Meta:
        model = Course
        fields = ('group_course_number', 'id')



class SessionSerializer1(ModelSerializer):
    class Meta:
        model = Session
        fields = ('id', 'session_number', 'get_jalali_date')
 
        
class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'group_course_number',
                  'get_jalali_start_date', 'get_jalali_end_date', 'tuition', 'percentage_required_for_tuition')

class CourseSerializer(ModelSerializer):
    class Meta:
        model = CourseTitle
        fields = ('title',)