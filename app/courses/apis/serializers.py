from collections import OrderedDict
from django.db.models import Q
from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer
from courses.models import (
    Course,
    Session,
    CourseTitle,
    CourseTime,
    MemberShip,
    MemberShipRoles,
)
from trs.apis.serializers import TimeSlotSerializer, SemesterSerializer
from assignments.apis.serializers import AssignmentSerializer
from exams.apis.serializers import ExamSerializer
from django.contrib.auth import get_user_model
from accounts.apis.serializers import UserSerializerBaseInfo
from contents.apis.serializers import ContentSerializer

User = get_user_model()


class CourseTimeSerializer(ModelSerializer):
    semester = SemesterSerializer()
    time_slot = TimeSlotSerializer()

    class Meta:
        model = CourseTime
        fields = ("semester", "time_slot")


class CourseTitleSerializer(ModelSerializer):
    class Meta:
        model = CourseTitle
        fields = ("title",)


class MemberShipSerializer(ModelSerializer):
    user = UserSerializerBaseInfo()

    class Meta:
        model = MemberShip
        fields = ("role", "user")


class CourseSerializer(ModelSerializer):
    course_title = CourseTitleSerializer()
    semester = SemesterSerializer()
    course_times = CourseTimeSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "course_title",
            "course_times",
            "group_course_number",
            "semester",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        teacher_members: list[MemberShip] = MemberShip.objects.filter(
            Q(id=representation["id"])
            & (Q(role=MemberShipRoles.TEACHER) | Q(role=MemberShipRoles.INSTRUCTOR))
        ).select_related("user")
        representation["teachers"] = [
            {
                "username": teacher_member.user.username,
                "first_name": teacher_member.user.first_name,
                "last_name": teacher_member.user.last_name,
            }
            for teacher_member in teacher_members
            if teacher_member.role == MemberShipRoles.TEACHER
        ]
        representation["instructors"] = [
            {
                "username": teacher_member.user.username,
                "first_name": teacher_member.user.first_name,
                "last_name": teacher_member.user.last_name,
            }
            for teacher_member in teacher_members
            if teacher_member.role == MemberShipRoles.INSTRUCTOR
        ]
        return representation


class CourseSerializerSlim(ModelSerializer):
    course_title = CourseTitleSerializer()
    semester = SemesterSerializer()

    class Meta:
        model = Course
        fields = ("id", "course_title", "group_course_number", "semester")


class CourseDetailSerializer(CourseSerializer):
    course_title = CourseTitleSerializer()
    semester = SemesterSerializer()
    course_times = CourseTimeSerializer(many=True, read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance=instance, data=data, **kwargs)

    class Meta:
        model = Course
        fields = (
            "id",
            "course_title",
            "group_course_number",
            "semester",
            "start_date",
            "end_date",
            "course_times",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["teachers"] = []
        representation["instructors"] = []
        representation["teaching_assistants"] = []

        def append_to_list(li: list, member):
            li.append(
                {
                    "username": member.user.username,
                    "first_name": member.user.first_name,
                    "last_name": member.user.last_name,
                }
            )

        representation["enrolled_count"] = 0
        representation["is_member"] = False

        course_id = self.context["course_id"]
        user_id = self.context.get("user_id")
        members: list[MemberShip] = MemberShip.objects.filter(
            Q(course=course_id)
            & (
                Q(role=MemberShipRoles.TEACHER)
                | Q(role=MemberShipRoles.TEACHING_ASSISTANT)
                | Q(role=MemberShipRoles.INSTRUCTOR)
            )
        ).select_related("user")
        for member in members:
            if user_id == member.user.id:
                representation["is_member"] = True
            if member.is_student():
                representation["enrolled_count"] += 1
            if member.is_teacher():
                append_to_list(representation["teachers"], member)
            if member.is_instructor():
                append_to_list(representation["instructors"], member)
            if member.is_teaching_assistant():
                append_to_list(representation["teaching_assistants"], member)
            pass
        return representation


class SessionSerializer(ModelSerializer):
    time_slot = TimeSlotSerializer(read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)
    exams = ExamSerializer(many=True, read_only=True)
    contents = ContentSerializer(many=True, read_only=True)
    course = CourseSerializerSlim()

    class Meta:
        model = Session
        fields = (
            "id",
            "session_number",
            "date",
            "course",
            "time_slot",
            "description",
            "assignments",
            "exams",
            "contents",
        )
