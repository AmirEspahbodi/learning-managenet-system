from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.generics import GenericAPIView

from courses.models import MemberShip, MemberShipRoles
from courses.permissions import IsTeacher, IsRelativeTeacherMixin
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

# Create your views here.
