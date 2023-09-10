from datetime import timedelta

from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.generics import GenericAPIView

from .serialisers import FinancialAidsResultSerializer
from courses.models import Session, MemberShip, MemberShipRoles
from courses.apis.serializers import SessionSerializer, CourseSerializer
from courses.permissions import IsTeacher, IsRelativeTeacherMixin
from students.models import FinancialAids
from students.apis.serializers import ShowFinancialAids
from exams.apis.serializers import (
    ExamRequestSerializer,
    ExamRequestUpdateSerializer,
    ExamSerializer,
    ExamResponseSerializer,
    ExamFTQuestionAnswerSerializer,
    ExamFTQuestionAnswerUpdateSerializer,
    ExamFTQuestionSerializer,
    ExamFTQuestionUpdateSerializer,
    ExamFTQuestionRequestSerializer,
    MemberExamFTQuestionSerializer,
    MemberExamFTQuestionScoreSerializer,
    MemberTakeExamSerilizer,
    AssignemntForGetMemberList,
    ExamMeberAnswerForSimilaritySerializer,
)
from exams.models import (
    MemberExamFTQuestion,
    MemberTakeExam,
)
from assignments.apis.serializers import (
    AssignmentRequestSerializer,
    AssignmentRequestUpdateSerializer,
    AssignmentSerializer,
    AssignmentFTQuestionSerializer,
    AssignmentFTQuestionUpdateSerializer,
    AssignmentResponseSerializer,
    AssignmentFTQuestionAnswerSerializer,
    AssignmentFTQuestionSerializer,
    MemberAssignmentFTQuestionSerializer,
    MemberAssignmentFTQuestionScoreSerializer,
    AssignmentFTQuestionRequestSerializer,
    MemberTakeAssignmentSerilizer,
    AssignmentFTQuestionAnswerUpdateSerializer,
    AssignmentMeberAnswerForSimilaritySerializer,
    AssignemntForGetMemberList,
)
from assignments.models import (
    MemberAssignmentFTQuestion,
    MemberTakeAssignment,
)
from contents.apis.serializers import (
    ContentRequestSerializer,
    ContentResponseSerializer,
    ContentUpdateSerializer,
)
from scripts.tf_idf_document_similarity import find_cheeters

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
        print("\n\n")
        print(data)
        print("\n\n")
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


class TeacherExamFindSimilarAnswersAPIView(IsRelativeTeacherMixin, GenericAPIView):
    def get(self, *args, **kwargs):
        exam_ftquestions = self.exam.ftquestions.all()
        response = {
            "id": self.exam.id,
            "title": self.exam.title,
            "description": self.exam.description,
            "ftquestions": [],
        }
        for ftquestion in exam_ftquestions:
            similar_answers = []
            member_ftquestion_answers = ftquestion.member_answers.all()
            member_ftquestion_answers_texts = [
                member_ftquestion_answer.answered_text
                for member_ftquestion_answer in member_ftquestion_answers
            ]
            result = find_cheeters(member_ftquestion_answers_texts)
            full_result = [
                {
                    "answer1": ExamMeberAnswerForSimilaritySerializer(
                        member_ftquestion_answers[i]
                    ).data,
                    "answer2": ExamMeberAnswerForSimilaritySerializer(
                        member_ftquestion_answers[result[i][0]]
                    ).data,
                    "similarity": result[i][1],
                }
                for i in range(len(result) - 1)
                if len(result[i]) != 0
            ]
            response["ftquestions"].append(
                {
                    "id": ftquestion.id,
                    "text": ftquestion.text,
                    "similar_answers": full_result,
                }
            )
        return Response(data=response, status=status.HTTP_200_OK)


########## EXAM


class TeacherExamAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = ExamRequestSerializer

    def get(self, request, *args, **kwargs) -> ExamSerializer:
        if "exam_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        return Response(
            data=ExamResponseSerializer(self.exam).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs) -> ExamSerializer:
        if "session_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(session=self.session)
            return Response(
                data=ExamSerializer(instance).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        if "exam_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serializer = ExamRequestUpdateSerializer(data=request.data, instance=self.exam)
        if serializer.is_valid():
            new_instance = serializer.save()
            return Response(
                data=self.serializer_class(new_instance).data, status=status.HTTP_200_OK
            )
        else:
            raise exceptions.APIException(
                detail=serializer.errors, code=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        if "exam_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.exam.delete()
        return Response(data={"message": "OK"}, status=status.HTTP_200_OK)


class TeacherExamQuestionAPIView(IsRelativeTeacherMixin, GenericAPIView):
    serializer_class = ExamFTQuestionRequestSerializer
    permission_classes = [IsTeacher]

    def post(self, request, *args, **kwargs) -> ExamFTQuestionSerializer:
        if "exam_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            instance = serializer.save(exam=self.exam)
            return Response(
                data=ExamFTQuestionSerializer(instance).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            raise exceptions.ValidationError(detail=serializer.errors)

    def get(self, request, *args, **kwargs):
        if "exam_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        return Response(
            data=ExamFTQuestionSerializer(self.exam_ftquestion).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        if "exam_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serilizer = ExamFTQuestionUpdateSerializer(
            instance=self.exam_ftquestion, data=request.data
        )
        if serilizer.is_valid():
            new_instance = serilizer.save()
            return Response(
                data=ExamFTQuestionSerializer(new_instance).data,
                status=status.HTTP_200_OK,
            )
        else:
            return exceptions.ValidationError(detail=serilizer.errors)

    def delete(self, request, *args, **kwargs):
        if "exam_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.exam_ftquestion.delete()
        return Response(
            data={"message": "deleted"},
            status=status.HTTP_200_OK,
        )


class TeacherExamFtQuestionAnswerAPIView(IsRelativeTeacherMixin, GenericAPIView):
    serializer_class = ExamFTQuestionAnswerSerializer
    permission_classes = [IsTeacher]

    def post(self, request, *args, **kwargs):
        if "exam_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(exam_ftquestion=self.exam_ftquestion)
            return Response(
                data=self.serializer_class(instance).data, status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, *args, **kwargs):
        if "exam_ftquestion_answer_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        return Response(
            data=ExamFTQuestionAnswerSerializer(self.exam_ftquestionanswer).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        if "exam_ftquestion_answer_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serilizer = ExamFTQuestionAnswerUpdateSerializer(
            self.exam_ftquestionanswer, data=request.data
        )
        if serilizer.is_valid():
            new_instance = serilizer.save()
            return Response(
                data=ExamFTQuestionAnswerSerializer(new_instance).data,
                status=status.HTTP_200_OK,
            )
        else:
            raise exceptions.ValidationError(detail=serilizer.errors)

    def delete(self, request, *args, **kwargs):
        if "exam_ftquestion_answer_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.exam_ftquestionanswer.delete()
        return Response(data={"message": "deleted"}, status=status.HTTP_200_OK)


class TeacherListMemberExamAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]

    def get(self, request, *args, **kwargs):
        return Response(
            data=AssignemntForGetMemberList(self.exam).data,
            status=status.HTTP_200_OK,
        )


class TeacherGetMemberExamAPIView(GenericAPIView):
    permission_classes = [IsTeacher]

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
        try:
            member_exam = MemberTakeExam.objects.get(id=member_exam_id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound()
        return Response(
            data=MemberTakeExamSerilizer(member_exam).data,
            status=status.HTTP_200_OK,
        )


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


class TeacherExamFindCheetersAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]

    def get(self, request, *args, **kwargs):
        pass


########## ASSIGNMENTS


class TeacherAssignmentAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]
    serializer_class = AssignmentRequestSerializer

    def get(self, request, *args, **kwargs) -> AssignmentSerializer:
        if "assignment_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        return Response(
            data=AssignmentResponseSerializer(self.assignment).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs) -> AssignmentSerializer:
        if "session_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(session=self.session)
            return Response(
                data=AssignmentSerializer(instance).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        if "assignment_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serilizer = AssignmentRequestUpdateSerializer(
            instance=self.assignment, data=request.data
        )
        if serilizer.is_valid():
            new_instance = serilizer.save()
            return Response(
                data=self.serializer_class(new_instance).data, status=status.HTTP_200_OK
            )
        else:
            raise exceptions.ValidationError(detail=serilizer.errors)

    def delete(self, request, *args, **kwargs):
        if "assignment_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.assignment.delete()
        return Response(data={"message": "OK"}, status=status.HTTP_200_OK)


class TeacherAssignmentQuestionAPIView(IsRelativeTeacherMixin, GenericAPIView):
    serializer_class = AssignmentFTQuestionRequestSerializer
    permission_classes = [IsTeacher]

    def post(self, request, *args, **kwargs) -> AssignmentFTQuestionSerializer:
        if "assignment_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(assignment=self.assignment)
            return Response(
                data=AssignmentFTQuestionSerializer(instance).data,
                status=status.HTTP_201_CREATED,
            )
        else:
            raise exceptions.ValidationError(detail=serializer.errors)

    def get(self, request, *args, **kwargs):
        if "assignment_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        return Response(
            data=AssignmentFTQuestionSerializer(self.assignment_ftquestion).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        if "assignment_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serializer = AssignmentFTQuestionUpdateSerializer(
            instance=self.assignment_ftquestion, data=request.data
        )
        if serializer.is_valid():
            new_instance = serializer.save()
            return Response(
                data=AssignmentFTQuestionSerializer(new_instance).data,
                status=status.HTTP_200_OK,
            )
        else:
            raise exceptions.ValidationError(detail=serializer.errors)

    def delete(self, request, *args, **kwargs):
        if "assignment_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.assignment_ftquestion.delete()
        return Response(
            data={"message": "OK"},
            status=status.HTTP_200_OK,
        )


class TeacherAssignmentFtQuestionAnswerAPIView(IsRelativeTeacherMixin, GenericAPIView):
    serializer_class = AssignmentFTQuestionAnswerSerializer
    permission_classes = [IsTeacher]

    def post(self, request, *args, **kwargs):
        if "assignment_ftquestion_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(assignment_ftquestion=self.assignment_ftquestion)
            return Response(
                data=self.serializer_class(instance).data, status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, *args, **kwargs):
        if "assignment_ftquestion_answer_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        return Response(
            data=self.serializer_class(self.assignment_ftquestionanswer).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        if "assignment_ftquestion_answer_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serializer = AssignmentFTQuestionAnswerUpdateSerializer(
            instance=self.assignment_ftquestionanswer, data=request.data
        )
        if serializer.is_valid():
            new_instance = serializer.save()
            return Response(
                data=self.serializer_class(new_instance).data, status=status.HTTP_200_OK
            )
        else:
            raise exceptions.ValidationError(detail=serializer.errors)

    def delete(self, request, *args, **kwargs):
        if "assignment_ftquestion_answer_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.assignment_ftquestionanswer.delete()
        return Response(data={"message": "Ok"}, status=status.HTTP_200_OK)


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


class TeacherListMemberAssignmentAPIView(IsRelativeTeacherMixin, GenericAPIView):
    permission_classes = [IsTeacher]

    def get(self, request, *args, **kwargs):
        return Response(
            data=AssignemntForGetMemberList(self.assignment).data,
            status=status.HTTP_200_OK,
        )


class TeacherGetMemberAssignmentAPIView(GenericAPIView):
    permission_classes = [IsTeacher]

    def get(self, request, *args, **kwargs):
        member_exam_id = kwargs.get("member_exam_id")
        try:
            member_take_assignment = MemberTakeAssignment.objects.select_related(
                "assignment__session"
            ).get(id=member_exam_id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound()
        member_course = member_take_assignment.assignment.session.course
        if not MemberShip.objects.filter(
            course=member_course,
            user=request.user.teacher_user,
            role=MemberShipRoles.TEACHER,
        ).exists():
            raise exceptions.PermissionDenied()
        try:
            member_assignment = MemberTakeAssignment.objects.get(id=member_exam_id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound()
        return Response(
            data=MemberTakeAssignmentSerilizer(member_assignment).data,
            status=status.HTTP_200_OK,
        )


class TeacherAssignmentFindSimilarAnswersAPIView(
    IsRelativeTeacherMixin, GenericAPIView
):
    def get(self, *args, **kwargs):
        assignment_ftquestions = self.assignment.ftquestions.all()
        response = {
            "id": self.assignment.id,
            "title": self.assignment.title,
            "description": self.assignment.description,
            "ftquestions": [],
        }
        for ftquestion in assignment_ftquestions:
            similar_answers = []
            member_ftquestion_answers = ftquestion.member_answers.all()
            member_ftquestion_answers_texts = [
                member_ftquestion_answer.answered_text
                for member_ftquestion_answer in member_ftquestion_answers
            ]
            result = find_cheeters(member_ftquestion_answers_texts)
            full_result = [
                {
                    "answer1": AssignmentMeberAnswerForSimilaritySerializer(
                        member_ftquestion_answers[i]
                    ).data,
                    "answer2": AssignmentMeberAnswerForSimilaritySerializer(
                        member_ftquestion_answers[result[i][0]]
                    ).data,
                    "similarity": result[i][1],
                }
                for i in range(len(result) - 1)
                if len(result[i]) != 0
            ]
            response["ftquestions"].append(
                {
                    "id": ftquestion.id,
                    "text": ftquestion.text,
                    "similar_answers": full_result,
                }
            )
        return Response(data=response, status=status.HTTP_200_OK)


##############  CONTENT


class TeacherContentAPIView(IsRelativeTeacherMixin, GenericAPIView):
    serializer_class = ContentRequestSerializer

    def get(self, request, *args, **kwargs):
        if "content_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        return Response(
            ContentResponseSerializer(self.content).data, status=status.HTTP_200_OK
        )

    def post(self, request, *args, **kwargs):
        if "session_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(session=self.session)
            return Response(
                ContentResponseSerializer(instance).data, status=status.HTTP_200_OK
            )
        else:
            raise exceptions.ValidationError(detail=serializer.errors)

    def put(self, request, *args, **kwargs):
        if "content_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        serializer = ContentUpdateSerializer(instance=self.content, data=request.data)
        if serializer.is_valid():
            new_instance = serializer.save()
            return Response(
                ContentResponseSerializer(new_instance).data, status=status.HTTP_200_OK
            )
        else:
            raise exceptions.ValidationError(detail=serializer.errors)

    def delete(self, request, *args, **kwargs):
        if "content_id" not in kwargs:
            raise exceptions.MethodNotAllowed()
        self.content.delete()
        return Response(data={"message": "Ok"}, status=status.HTTP_200_OK)
