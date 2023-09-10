from django.utils import timezone
from django.db.models import Q
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework import serializers, fields
from rest_framework.exceptions import ValidationError
from ..models import (
    Assignment,
    FTQuestion,
    FTQuestionAnswer,
    FTQuestion,
    MemberAssignmentFTQuestion,
    MemberTakeAssignment,
)
from courses.models import MemberShip
from accounts.apis.serializers import UserSerializerBaseInfo


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = (
            "id",
            "session",
            "description",
            "assignment_number",
            "start_at",
            "end_at",
        )


class AssignmentFTQuestionUpdateSerializer(serializers.ModelSerializer):
    title = fields.CharField(required=False)
    text = fields.CharField(required=False)
    file = fields.FileField(required=False)
    start_at = fields.DateTimeField(required=False)
    end_at = fields.DateTimeField(required=False)

    class Meta:
        model = FTQuestion
        fields = (
            "title",
            "text",
            "file",
            "start_at",
            "end_at",
        )


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = (
            "id",
            "session",
            "title",
            "description",
            "assignment_number",
            "created_at",
            "start_at",
            "end_at",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)

        return response


class AssignmentRequestUpdateSerializer(serializers.ModelSerializer):
    title = fields.CharField(required=False)
    description = fields.CharField(required=False)
    start_at = fields.DateTimeField(required=False)
    end_at = fields.DateTimeField(required=False)

    class Meta:
        model = Assignment
        fields = (
            "title",
            "description",
            "start_at",
            "end_at",
        )


class AssignmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = (
            "title",
            "description",
            "start_at",
            "end_at",
        )

    def create(self, validated_data):
        assignment_number = Assignment.objects.filter(
            session=validated_data["session"]
        ).count()
        # abount validated_data["session"]
        # save method has **kwargs that will destruct in validated_data
        # so in view we can pass session=self.session to save methos and access it in validated_data
        assignment = Assignment.objects.create(
            session=validated_data["session"],
            title=validated_data["title"],
            assignment_number=assignment_number,
            description=validated_data.get("description"),
            start_at=validated_data["start_at"],
            end_at=validated_data["end_at"],
        )
        return assignment


class AssignmentFTQuestionAnswerUpdateSerializer(serializers.ModelSerializer):
    answer_text = fields.CharField(required=False)
    answer_file = fields.FileField(required=False)
    accessing_at = fields.DateTimeField(required=False)

    class Meta:
        model = FTQuestionAnswer
        fields = ("answer_text", "answer_file", "accessing_at")


class AssignmentFTQuestionAnswerSerializer(serializers.ModelSerializer):
    id = fields.IntegerField(required=False)

    class Meta:
        model = FTQuestionAnswer
        fields = ("id", "answer_text", "answer_file", "accessing_at")

    def validate(self, attrs):
        answer_text = attrs.get("answer_text")
        answer_file = attrs.get("answer_file")
        if answer_file is None and answer_text is None:
            raise ValidationError(detail="either file or text must be given")
        return attrs

    def create(self, validated_data):
        ft_question_answer = FTQuestionAnswer.objects.create(
            ft_question=validated_data["assignment_ftquestion"],
            answer_text=validated_data.get("answer_text"),
            answer_file=validated_data.get("answer_file"),
            accessing_at=validated_data.get("accessing_at"),
        )
        return ft_question_answer


class AssignmentFTQuestionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FTQuestion
        fields = (
            "title",
            "text",
            "file",
            "start_at",
            "end_at",
        )

    def validate(self, attrs):
        file = attrs.get("file")
        text = attrs.get("text")
        if file is None and text is None:
            raise ValidationError(detail="either file or text must be given")
        return attrs


class AssignmentFTQuestionSerializer(serializers.ModelSerializer):
    id = fields.IntegerField(required=False)
    ftquestion_answers = AssignmentFTQuestionAnswerSerializer(many=True)

    class Meta:
        model = FTQuestion
        fields = (
            "id",
            "title",
            "text",
            "file",
            "start_at",
            "end_at",
            "ftquestion_answers",
        )

    def validate(self, attrs):
        file = attrs.get("file")
        text = attrs.get("text")
        if file is None and text is None:
            raise ValidationError(detail="either file or text must be given")
        return attrs


class AssignmentResponseSerializer(serializers.ModelSerializer):
    ftquestions = AssignmentFTQuestionSerializer(many=True)

    class Meta:
        model = Assignment
        fields = (
            "id",
            "session",
            "title",
            "description",
            "assignment_number",
            "created_at",
            "start_at",
            "end_at",
            "ftquestions",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)

        return response


class FTQuestionSerializer(serializers.ModelSerializer):
    ftquestion_answers = AssignmentFTQuestionAnswerSerializer

    class Meta:
        model = FTQuestion
        fields = (
            "assignment",
            "title",
            "text",
            "file",
            "start_at",
            "end_at",
            "ftquestion_answers",
        )

    def create(self, validated_data):
        ft_question_answer = Assignment.objects.create(
            ft_question=validated_data["assignment_ftquestion"],
            start_at=validated_data["answer_text"],
            end_at=validated_data["answer_file"],
        )
        return ft_question_answer


class MemberAssignmentFTQuestionScoreSerializer(serializers.Serializer):
    score = fields.IntegerField()


class MemberAssignmentFTQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberAssignmentFTQuestion
        fields = (
            "id",
            "score",
            "answered_text",
            "answered_file",
            "created_at",
            "updated_at",
        )


class MemberTakeAssignmentSerilizer(serializers.ModelSerializer):
    member_take_assignment_ftquestions = MemberAssignmentFTQuestionSerializer()

    class Meta:
        model = MemberTakeAssignment
        fields = (
            "id",
            "last_visit",
            "finish_at",
            "score",
            "member_take_assignment_ftquestions",
        )


class StudentOutOfTimeAssignmentFtQuestionSerilizer(serializers.ModelSerializer):
    class Meta:
        model = FTQuestion
        fields = (
            "title",
            "start_at",
            "end_at",
        )


class StudentMemberAssignmentFTQuestionRequestSerilizer(serializers.ModelSerializer):
    class Meta:
        model = MemberAssignmentFTQuestion
        fields = ("answered_text", "answered_file")


class StudentMemberAssignmentFTQuestionResponseSerilizer(serializers.ModelSerializer):
    class Meta:
        model = MemberAssignmentFTQuestion
        fields = (
            "id",
            "score",
            "answered_text",
            "answered_file",
            "created_at",
            "updated_at",
        )


class StudentAssignmentFtQuestionRersponseSerilizer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        self.member_take_assignment = kwargs.pop("member_take_assignment")
        self.member_assignment_ftquestions = MemberAssignmentFTQuestion.objects.filter(
            member_take_assignment=self.member_take_assignment,
            ft_question__in=[ins.id for ins in instance],
        ).all()
        super().__init__(instance=instance, data=data, **kwargs)

    class Meta:
        model = FTQuestion
        fields = (
            "id",
            "title",
            "text",
            "file",
            "start_at",
            "end_at",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        member_assignment_ftquestion = [
            member_assignment_ftquestion
            for member_assignment_ftquestion in self.member_assignment_ftquestions
            if member_assignment_ftquestion.ft_question == instance
        ]
        if member_assignment_ftquestion:
            member_assignment_ftquestion = member_assignment_ftquestion[0]
            representation["student_answer"] = {
                "id": member_assignment_ftquestion.id,
                "answered_text": member_assignment_ftquestion.answered_text,
                "answered_file": member_assignment_ftquestion.answered_file.url
                if member_assignment_ftquestion.answered_file
                else None,
                "score": member_assignment_ftquestion.score,
                "created_at": member_assignment_ftquestion.created_at,
                "updated_at": member_assignment_ftquestion.updated_at,
            }
        else:
            representation["student_answer"] = None
        return representation


class StudentAssignmentFtQuestionWithAnswerRersponseSerilizer(
    StudentAssignmentFtQuestionRersponseSerilizer
):
    def __init__(self, instance=None, data=empty, **kwargs):
        self.ftquestions_answers = FTQuestionAnswer.objects.filter(
            Q(ft_question__in=[ins.id for ins in instance])
            & Q(Q(accessing_at__isnull=True) | Q(accessing_at__lte=timezone.now()))
        ).all()
        super().__init__(instance=instance, data=data, **kwargs)

    class Meta:
        model = FTQuestion
        fields = (
            "id",
            "title",
            "text",
            "file",
            "start_at",
            "end_at",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ftquestions_answers = [
            ftqa for ftqa in self.ftquestions_answers if ftqa.ft_question == instance
        ]
        representation["answers"] = [
            {
                "answer_text": ftquestions_answer.answer_text,
                "answer_file": ftquestions_answer.answer_file.url
                if ftquestions_answer.answer_file
                else None,
            }
            for ftquestions_answer in ftquestions_answers
        ]
        return representation


class MemberShipSerializer(serializers.ModelSerializer):
    user = UserSerializerBaseInfo()

    class Meta:
        model = MemberShip
        fields = ("role", "user")


class MemberTakeAssignmentSerializer(serializers.ModelSerializer):
    member = MemberShipSerializer()

    class Meta:
        model = MemberTakeAssignment
        fields = ["member"]


class AssignmentMeberAnswerForSimilaritySerializer(serializers.ModelSerializer):
    member_take_assignment = MemberTakeAssignmentSerializer()

    class Meta:
        model = MemberAssignmentFTQuestion
        fields = (
            "id",
            "answered_text",
            "answered_file",
            "score",
            "member_take_assignment",
        )


class MemberAssignmentFTQuestionSerilizer(serializers.ModelSerializer):
    class Meta:
        model = MemberAssignmentFTQuestion
        fields = (
            "id",
            "answered_text",
            "answered_file",
            "score",
        )


class AssignmentFTQuestionUpdateSerializer(serializers.ModelSerializer):
    member_answers = MemberAssignmentFTQuestionSerilizer(many=True)

    class Meta:
        model = FTQuestion
        fields = ("id", "title", "text", "file", "start_at", "end_at", "member_answers")


class AssignemntForGetMemberList(serializers.ModelSerializer):
    ftquestions = AssignmentFTQuestionUpdateSerializer(many=True)

    class Meta:
        model = Assignment
        fields = (
            "id",
            "session",
            "description",
            "ftquestions",
            "assignment_number",
            "start_at",
            "end_at",
        )
