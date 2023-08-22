from datetime import timedelta, datetime
import pytz
from django.utils import timezone

from django.utils import timezone
from django.conf import global_settings
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.generics import GenericAPIView

from courses.models import Session, Course, MemberShip, MemberShipRoles
from courses.apis.serializers import SessionSerializer, CourseSerializer
from courses.permissions import IsStudent, IsRelativeStudentMixin
from students.apis.serializers import StudentFinancialAids
from exams.models import (
    Exam,
    FTQuestion as ExamFTQuestion,
    FTQuestionAnswer as ExamFTQuestionAnswer,
    MemberTakeExam,
    MemberExamFTQuestion,
)
from exams.apis.serializers import (
    StudentOutOfTimeExamFtQuestionSerilizer,
    StudentExamFtQuestionRersponseSerilizer,
    ExamSerializer,
    StudentMemberExamFTQuestionRequestSerilizer,
    StudentMemberExamFTQuestionResponseSerilizer,
    StudentExamFtQuestionWithAnswerRersponseSerilizer,
)
from assignments.models import (
    Assignment,
    FTQuestion as AssignmentFTQuestion,
    FTQuestionAnswer as AssignmentFTQuestionAnswer,
    MemberTakeAssignment,
    MemberAssignmentFTQuestion,
)
from assignments.apis.serializers import (
    StudentOutOfTimeAssignmentFtQuestionSerilizer,
    StudentAssignmentFtQuestionRersponseSerilizer,
    AssignmentSerializer,
    StudentMemberAssignmentFTQuestionRequestSerilizer,
    StudentMemberAssignmentFTQuestionResponseSerilizer,
    StudentAssignmentFtQuestionWithAnswerRersponseSerilizer,
)
from contents.apis.serializers import StudentContentResponseSerializer
from contents.models import MemberVisitContent


class StudentHomeAPIView(GenericAPIView):
    permission_classes = [IsStudent]
    serializer_class = None

    def get(self, request, *args, **kwargs):
        now = timezone.now().date()
        day_next_week = (timezone.now() + timedelta(days=7)).date()
        st_memberships = MemberShip.objects.filter(
            user=request.user, role=MemberShipRoles.STUDENT
        ).select_related("course")
        courses = [st_membership.course for st_membership in st_memberships]
        week_sessions = Session.objects.filter(
            Q(date__gte=now) & Q(date__lte=day_next_week) & Q(course__in=courses)
        )
        return Response(
            {
                "courses": CourseSerializer(courses, many=True).data,
                "sessions": SessionSerializer(week_sessions, many=True).data,
                "now": now,
            },
            status=status.HTTP_200_OK,
        )


class StudentCourseEnroleAPIView(GenericAPIView):
    permission_classes = [IsStudent]

    def post(self, request, *args, **kwargs):
        try:
            course = Course.objects.get(id=kwargs.get("course_id"))
        except ObjectDoesNotExist:
            return Response(
                {"message": "course does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            obj = MemberShip.objects.get(
                Q(course=kwargs.get("course_id")) & Q(user=request.user)
            )
            if obj is not None:
                return Response(
                    {"message": "you are already enrolled"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ObjectDoesNotExist:
            pass
        try:
            MemberShip.objects.create(
                user=request.user, role=MemberShipRoles.STUDENT, course=course
            )
        except BaseException as e:
            return Response(
                data={"message": "do not try again!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(data={"message": "Ok"}, status=status.HTTP_200_OK)


class StudentGetFinancialAidAPIView(GenericAPIView):
    permission_classes = [IsStudent]

    def get(self, request, *args, **kwargs):
        financial_aids = request.user.student_user.financial_aids
        return Response(
            data=StudentFinancialAids(financial_aids, many=True).data,
            status=status.HTTP_200_OK,
        )


class StudentCourseDetailAPIView(IsRelativeStudentMixin, GenericAPIView):
    permission_classes = [IsStudent]

    def get(self, request, *args, **kwargs):
        sessions = Session.objects.filter(course=self.course).order_by("date")
        return Response(
            {"sessions": SessionSerializer(sessions, many=True).data},
            status=status.HTTP_200_OK,
        )


class StudentSessionDetailAPIView(IsRelativeStudentMixin, GenericAPIView):
    serializer_class = SessionSerializer
    permission_classes = [IsStudent]

    def get(self, request, *args, **kwargs):
        return Response(
            {"sessions": SessionSerializer(self.session).data},
            status=status.HTTP_200_OK,
        )


########### EXAMS


class StudentExamAPIView(IsRelativeStudentMixin, GenericAPIView):
    serializer_class = SessionSerializer
    permission_classes = [IsStudent]

    def get(self, request, *args, **kwargs):
        current_time = timezone.now()
        if self.exam.start_at > current_time:
            raise exceptions.NotAcceptable(detail="exam not started")
        if self.exam.end_at < current_time:
            questions = ExamFTQuestion.objects.filter(exam=self.exam)
            [member_take_exam, created] = MemberTakeExam.objects.get_or_create(
                member=self.member, exam=self.exam
            )
            return Response(
                data={
                    **ExamSerializer(self.exam).data,
                    "questions": StudentExamFtQuestionWithAnswerRersponseSerilizer(
                        questions,
                        many=True,
                        member_take_exam=member_take_exam,
                    ).data,
                },
                status=status.HTTP_200_OK,
            )
        [member_take_exam, created] = MemberTakeExam.objects.get_or_create(
            member=self.member, exam=self.exam
        )
        if not created:
            member_take_exam.save()
        questions = ExamFTQuestion.objects.filter(exam=self.exam)
        not_started_questions = []
        started_questions = []
        ended_questions = []

        for question in questions:
            if question.start_at > current_time:
                not_started_questions.append(question)
            elif question.end_at < current_time:
                ended_questions.append(question)
            else:
                started_questions.append(question)
        return Response(
            data={
                **ExamSerializer(self.exam).data,
                "not_started_questions": StudentOutOfTimeExamFtQuestionSerilizer(
                    not_started_questions, many=True
                ).data,
                "started_questions": StudentExamFtQuestionRersponseSerilizer(
                    started_questions, many=True, member_take_exam=member_take_exam
                ).data,
                "ended_questions": StudentExamFtQuestionRersponseSerilizer(
                    ended_questions, many=True, member_take_exam=member_take_exam
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class StudentExamFTQuestionAPIView(IsRelativeStudentMixin, GenericAPIView):
    serializer_class = StudentMemberExamFTQuestionRequestSerilizer
    permission_classes = [IsStudent]

    def check_time(self):
        current_time = timezone.now()
        if self.exam.start_at > current_time:
            raise exceptions.NotAcceptable(detail="exam not started")
        if self.exam.end_at < current_time:
            raise exceptions.PermissionDenied(detail="exam ended")
        if self.exam_ftquestion.start_at > current_time:
            raise exceptions.NotAcceptable(detail="question not started")
        if self.exam_ftquestion.end_at < current_time:
            raise exceptions.NotAcceptable(detail="question ended")

    def post(self, request, *args, **kwargs):
        if "exam_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.check_time()
        [member_take_exam, created] = MemberTakeExam.objects.get_or_create(
            member=self.member, exam=self.exam
        )
        [member_exam_ftquestion, created] = MemberExamFTQuestion.objects.get_or_create(
            member_take_exam=member_take_exam, ft_question=self.exam_ftquestion
        )
        serializer = self.serializer_class(member_exam_ftquestion, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                data=StudentMemberExamFTQuestionResponseSerilizer(instance).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            raise exceptions.ValidationError(serializer.errors)

    def put(self, request, *args, **kwargs):
        if "member_exam_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.check_time()
        serializer = self.serializer_class(
            self.member_exam_ftquestion, data=request.data
        )
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                data=StudentMemberExamFTQuestionResponseSerilizer(instance).data,
                status=status.HTTP_200_OK,
            )
        else:
            raise exceptions.ValidationError(serializer.errors)

    def delete(self, request, *args, **kwargs):
        if "member_exam_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.check_time()
        self.member_exam_ftquestion.delete()
        return Response(data={"message": "OK"}, status=status.HTTP_200_OK)


########### ASIGNMENTS


class StudentAssignmentAPIView(IsRelativeStudentMixin, GenericAPIView):
    serializer_class = SessionSerializer
    permission_classes = [IsStudent]

    def get(self, request, *args, **kwargs):
        current_time = timezone.now()
        if self.assignment.start_at > current_time:
            raise exceptions.NotAcceptable(detail="assignment not started")
        if self.assignment.end_at < current_time:
            questions = AssignmentFTQuestion.objects.filter(assignment=self.assignment)
            [
                member_take_assignment,
                created,
            ] = MemberTakeAssignment.objects.get_or_create(
                member=self.member, assignment=self.assignment
            )
            return Response(
                data={
                    **AssignmentSerializer(self.assignment).data,
                    "questions": StudentAssignmentFtQuestionWithAnswerRersponseSerilizer(
                        questions,
                        many=True,
                        member_take_assignment=member_take_assignment,
                    ).data,
                },
                status=status.HTTP_200_OK,
            )
        [member_take_assignment, created] = MemberTakeAssignment.objects.get_or_create(
            member=self.member, assignment=self.assignment
        )
        if not created:
            member_take_assignment.save()
        questions = AssignmentFTQuestion.objects.filter(assignment=self.assignment)
        not_started_questions = []
        started_questions = []
        ended_questions = []

        for question in questions:
            if question.start_at > current_time:
                not_started_questions.append(question)
            elif question.end_at < current_time:
                ended_questions.append(question)
            else:
                started_questions.append(question)
        return Response(
            data={
                **AssignmentSerializer(self.assignment).data,
                "not_started_questions": StudentOutOfTimeAssignmentFtQuestionSerilizer(
                    not_started_questions, many=True
                ).data,
                "started_questions": StudentAssignmentFtQuestionRersponseSerilizer(
                    started_questions,
                    many=True,
                    member_take_assignment=member_take_assignment,
                ).data,
                "ended_questions": StudentAssignmentFtQuestionRersponseSerilizer(
                    ended_questions,
                    many=True,
                    member_take_assignment=member_take_assignment,
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class StudentAssignmentFTQuestionAPIView(IsRelativeStudentMixin, GenericAPIView):
    serializer_class = StudentMemberAssignmentFTQuestionRequestSerilizer
    permission_classes = [IsStudent]

    def check_time(self):
        current_time = timezone.now()
        if self.assignment.start_at > current_time:
            raise exceptions.NotAcceptable(detail="assignment not started")
        if self.assignment.end_at < current_time:
            raise exceptions.PermissionDenied(detail="assignment ended")
        if self.assignment_ftquestion.start_at > current_time:
            raise exceptions.NotAcceptable(detail="question not started")
        if self.assignment_ftquestion.end_at < current_time:
            raise exceptions.NotAcceptable(detail="question ended")

    def post(self, request, *args, **kwargs):
        if "assignment_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.check_time()
        [member_take_assignment, created] = MemberTakeAssignment.objects.get_or_create(
            member=self.member, assignment=self.assignment
        )
        [
            member_assignment_ftquestion,
            created,
        ] = MemberAssignmentFTQuestion.objects.get_or_create(
            member_take_assignment=member_take_assignment,
            ft_question=self.assignment_ftquestion,
        )
        serializer = self.serializer_class(
            member_assignment_ftquestion, data=request.data
        )
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                data=StudentMemberAssignmentFTQuestionResponseSerilizer(instance).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            raise exceptions.ValidationError(serializer.errors)

    def put(self, request, *args, **kwargs):
        if "member_assignment_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.check_time()
        serializer = self.serializer_class(
            self.member_assignment_ftquestion, data=request.data
        )
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                data=StudentMemberAssignmentFTQuestionResponseSerilizer(instance).data,
                status=status.HTTP_200_OK,
            )
        else:
            raise exceptions.ValidationError(serializer.errors)

    def delete(self, request, *args, **kwargs):
        if "member_assignment_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.check_time()
        self.member_assignment_ftquestion.delete()
        return Response(data={"message": "OK"}, status=status.HTTP_200_OK)


########### CONTENTS


class StudentContentAPIView(IsRelativeStudentMixin, GenericAPIView):
    def get(self, request, *args, **kwargs):
        [member_visit_content, created] = MemberVisitContent.objects.get_or_create(
            member=self.member, content=self.content
        )
        if not created:
            member_visit_content.save()
        return Response(
            data=StudentContentResponseSerializer(self.content).data,
            status=status.HTTP_200_OK,
        )
