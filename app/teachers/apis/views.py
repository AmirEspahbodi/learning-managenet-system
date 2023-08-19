from datetime import timedelta

from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.generics import GenericAPIView

from .serialisers import FinancialAidsResultSerializer
from courses.models import Session, Course, MemberShip, MemberShipRoles
from courses.apis.serializers import SessionSerializer, CourseSerializer
from courses.permissions import IsTeacher, IsRelativeTeacherMixin
from students.models import Student, FinancialAids
from students.apis.serializers import ShowFinancialAids
from exams.apis.serializers import (
    ExamRequestSerializer,
    ExamSerializer,
    ExamFTQuestionSerializer,
    ExamResponseSerializer,
    ExamFTQuestionAnswerSerializer,
    ExamFTQuestionSerializer,
    MemberExamFTQuestionSerializer,
    MemberExamFTQuestionScoreSerializer,
)
from exams.models import FTQuestion, MemberExamFTQuestion, MemberTakeExam
from assignments.apis.serializers import (
    AssignmentRequestSerializer,
    AssignmentSerializer,
    AssignmentFTQuestionSerializer,
    AssignmentResponseSerializer,
    AssignmentFTQuestionAnswerSerializer,
    AssignmentFTQuestionSerializer,
    MemberAssignmentFTQuestionSerializer,
    MemberAssignmentFTQuestionScoreSerializer,
)
from assignments.models import (
    FTQuestion,
    MemberAssignmentFTQuestion,
    MemberTakeAssignment,
)

User = get_user_model()


class TeacherHomeAPIView(GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = None

    def get(self, request, *args, **kwargs):
        now = timezone.now().date()
        day_next_week = (timezone.now() + timedelta(days=7)).date()
        memberships = MemberShip.objects.filter(
            user=request.user, role=MemberShipRoles.TEACHER
        ).select_related("course")
        courses = [membership.course for membership in memberships]
        week_sessions = Session.objects.filter(
            Q(date__gte=now) & Q(date__lt=day_next_week) & Q(course__in=courses)
        )
        print([week_session.date for week_session in week_sessions])
        return Response(
            {
                "courses": CourseSerializer(courses, many=True).data,
                "sessions": SessionSerializer(week_sessions, many=True).data,
                "now": now,
            },
            status=status.HTTP_200_OK,
        )


class TeacherCourseDetailAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = SessionSerializer

    def get(self, request, *args, **kwargs):
        sessions = Session.objects.filter(course=self.course).order_by("date")
        return Response(
            {"sessions": SessionSerializer(sessions, many=True).data},
            status=status.HTTP_200_OK,
        )


class TeacherSessionDetailAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = SessionSerializer

    def get(self, request, *args, **kwargs):
        return Response(
            data=SessionSerializer(self.session).data, status=status.HTTP_200_OK
        )


class TeacherFinancialAidsAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = ShowFinancialAids

    def get(self, request, *args, **kwargs):
        course_id = kwargs.get("course_id")
        financial_aids = (
            FinancialAids.objects.filter(course=course_id)
            .select_related("student")
            .select_related("student__user")
        )
        return Response(
            data=ShowFinancialAids(financial_aids, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        serializer = FinancialAidsResultSerializer(data=request.data)
        serializer.is_valid()
        data = serializer.data
        try:
            user = User.objects.get(id=data["user_id"])
        except ObjectDoesNotExist:
            return Response(
                data={"detail": "student does not exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        FinancialAids.objects.filter(id=data["financial_id"]).update(
            result=data["result"],
            is_accepted=data["is_accepted"],
            reviewed=True,
        )
        if data["is_accepted"]:
            if not (
                MemberShip.objects.filter(Q(course=self.course), Q(user=user))
            ).exists():
                MemberShip.objects.create(
                    course=self.course, user=user, role=MemberShipRoles.STUDENT
                )
            else:
                return Response(
                    data={"detail": "student is already member of course"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(data={"message": "OK"}, status=status.HTTP_200_OK)


class TeacherExamCreateAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = ExamRequestSerializer

    def get(self, request, *args, **kwargs) -> ExamSerializer:
        if "exam_id" not in kwargs:
            return Response(
                data={"this paramter requered": "exam_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            data=ExamResponseSerializer(instance=self.exam).data,
            status=status.HTTP_201_CREATED,
        )

    def post(self, request, *args, **kwargs) -> ExamSerializer:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(session=self.session)
            return Response(
                data=ExamSerializer(instance).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherExamQuestionAPIView(IsRelativeTeacherMixin, GenericAPIView):
    serializer_class = ExamFTQuestionSerializer
    permission_classes = [IsTeacher]

    def post(self, request, *args, **kwargs) -> ExamFTQuestionSerializer:
        FTQuestions = []
        for question in request.data:
            serializer = self.serializer_class(data=question)
            if serializer.is_valid():
                FTQuestions.append(FTQuestion(exam=self.exam, **serializer.data))
            else:
                return Response(
                    data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        instances = FTQuestion.objects.bulk_create(FTQuestions)
        return Response(
            data=ExamFTQuestionSerializer(instances, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, *args, **kwargs):
        if "exam_ftquestion_id" not in kwargs:
            return Response(
                data={"detail": "not found exam ftquestion id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            data=ExamFTQuestionSerializer(self.ftquestion).data,
            status=status.HTTP_200_OK,
        )


class TeacherExamFtQuestionAnswerAPIView(IsRelativeTeacherMixin, GenericAPIView):
    serializer_class = ExamFTQuestionAnswerSerializer

    def post(self, request, *args, **kwargs):
        if "exam_ftquestion_id" not in kwargs:
            return Response(
                data={"detail": "not found exam ftquestion id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(ft_question=self.ftquestion)
            return Response(
                data=self.serializer_class(instance).data, status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


class TeacherMemberExamAPIView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        member_exam_id = kwargs.get("member_exam_id")
        try:
            member_take_exam = MemberTakeExam.objects.select_related(
                "exam__session"
            ).get(id=member_exam_id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound()
        member_course = member_take_exam.exam.session.course
        if not MemberShip.objects.filter(
            course=member_course,
            user=request.user.teacher_user,
            role=MemberShipRoles.TEACHER,
        ).exists():
            raise exceptions.PermissionDenied()


class TeacherMemberExamFtQuestionAPIView(GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = MemberExamFTQuestionSerializer

    def get(self, request, *args, **kwargs):
        member_exam_ftquestion_id = kwargs.get("member_exam_ftquestion_id")
        try:
            memberexamftquestion = (
                MemberExamFTQuestion.objects.select_related("member_take_exam")
                .select_related("member_take_exam__exam")
                .get(id=member_exam_ftquestion_id)
            )
        except ObjectDoesNotExist:
            raise exceptions.NotFound()
        member_course = memberexamftquestion.member_take_exam.exam.session.course
        if not MemberShip.objects.filter(
            course=member_course,
            user=request.user.teacher_user,
            role=MemberShipRoles.TEACHER,
        ).exists():
            raise exceptions.PermissionDenied()
        return Response(
            data=MemberExamFTQuestionSerializer(memberexamftquestion).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        member_exam_ftquestion_id = kwargs.get("member_exam_ftquestion_id")
        try:
            memberexamftquestion = (
                MemberExamFTQuestion.objects.select_related("member_take_exam")
                .select_related("member_take_exam__exam")
                .get(id=member_exam_ftquestion_id)
            )
        except ObjectDoesNotExist:
            raise exceptions.NotFound()
        member_course = memberexamftquestion.member_take_exam.exam.session.course
        if not MemberShip.objects.filter(
            course=member_course,
            user=request.user.teacher_user,
            role=MemberShipRoles.TEACHER,
        ).exists():
            raise exceptions.PermissionDenied()
        serilizer = MemberExamFTQuestionScoreSerializer(data=request.data)
        if serilizer.is_valid():
            memberexamftquestion.score = serilizer.data["score"]
            memberexamftquestion.save()
        else:
            return Response(data=serilizer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"message": "Ok"}, status=status.HTTP_200_OK)


class TeacherAssignmentCreateAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = AssignmentRequestSerializer

    def get(self, request, *args, **kwargs) -> AssignmentSerializer:
        if "assignment_id" not in kwargs:
            return Response(
                data={"this paramter requered": "assignment_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            data=AssignmentResponseSerializer(instance=self.assignment).data,
            status=status.HTTP_201_CREATED,
        )

    def post(self, request, *args, **kwargs) -> AssignmentSerializer:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(session=self.session)
            return Response(
                data=AssignmentSerializer(instance).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherAssignmentQuestionAPIView(IsRelativeTeacherMixin, GenericAPIView):
    serializer_class = AssignmentFTQuestionSerializer
    permission_classes = [IsTeacher]

    def post(self, request, *args, **kwargs) -> AssignmentFTQuestionSerializer:
        FTQuestions = []
        for question in request.data:
            serializer = self.serializer_class(data=question)
            if serializer.is_valid():
                FTQuestions.append(
                    FTQuestion(assignment=self.assignment, **serializer.data)
                )
            else:
                return Response(
                    data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        instances = FTQuestion.objects.bulk_create(FTQuestions)
        return Response(
            data=AssignmentFTQuestionSerializer(instances, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, *args, **kwargs):
        if "assignment_ftquestion_id" not in kwargs:
            return Response(
                data={"detail": "not found assignment ftquestion id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            data=AssignmentFTQuestionSerializer(self.ftquestion).data,
            status=status.HTTP_200_OK,
        )


class TeacherAssignmentFtQuestionAnswerAPIView(IsRelativeTeacherMixin, GenericAPIView):
    serializer_class = AssignmentFTQuestionAnswerSerializer

    def post(self, request, *args, **kwargs):
        if "assignment_ftquestion_id" not in kwargs:
            return Response(
                data={"detail": "not found assignment ftquestion id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(ft_question=self.ftquestion)
            return Response(
                data=self.serializer_class(instance).data, status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


class TeacherMemberAssignmentAPIView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        member_assignment_id = kwargs.get("member_assignment_id")
        try:
            member_take_assignment = MemberTakeAssignment.objects.select_related(
                "assignment__session"
            ).get(id=member_assignment_id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound()
        member_course = member_take_assignment.assignment.session.course
        if not MemberShip.objects.filter(
            course=member_course,
            user=request.user.teacher_user,
            role=MemberShipRoles.TEACHER,
        ).exists():
            raise exceptions.PermissionDenied()


class TeacherMemberAssignmentFtQuestionAPIView(GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = MemberAssignmentFTQuestionSerializer

    def get(self, request, *args, **kwargs):
        member_assignment_ftquestion_id = kwargs.get("member_assignment_ftquestion_id")
        try:
            memberassignmentftquestion = (
                MemberAssignmentFTQuestion.objects.select_related(
                    "member_take_assignment"
                )
                .select_related("member_take_assignment__assignment")
                .get(id=member_assignment_ftquestion_id)
            )
        except ObjectDoesNotExist:
            raise exceptions.NotFound()
        member_course = (
            memberassignmentftquestion.member_take_assignment.assignment.session.course
        )
        if not MemberShip.objects.filter(
            course=member_course,
            user=request.user.teacher_user,
            role=MemberShipRoles.TEACHER,
        ).exists():
            raise exceptions.PermissionDenied()
        return Response(
            data=MemberAssignmentFTQuestionSerializer(memberassignmentftquestion).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        member_assignment_ftquestion_id = kwargs.get("member_assignment_ftquestion_id")
        try:
            memberassignmentftquestion = (
                MemberAssignmentFTQuestion.objects.select_related(
                    "member_take_assignment"
                )
                .select_related("member_take_assignment__assignment")
                .get(id=member_assignment_ftquestion_id)
            )
        except ObjectDoesNotExist:
            raise exceptions.NotFound()
        member_course = (
            memberassignmentftquestion.member_take_assignment.assignment.session.course
        )
        if not MemberShip.objects.filter(
            course=member_course,
            user=request.user.teacher_user,
            role=MemberShipRoles.TEACHER,
        ).exists():
            raise exceptions.PermissionDenied()
        serilizer = MemberAssignmentFTQuestionScoreSerializer(data=request.data)
        if serilizer.is_valid():
            memberassignmentftquestion.score = serilizer.data["score"]
            memberassignmentftquestion.save()
        else:
            return Response(data=serilizer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"message": "Ok"}, status=status.HTTP_200_OK)
