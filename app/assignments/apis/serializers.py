from rest_framework import serializers
from ..models import Assignment


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = (
            "id",
            "session",
            "description",
            "assignment_number",
            "statrt_at",
            "end_at",
        )


from rest_framework import serializers, fields
from rest_framework.exceptions import ValidationError
from ..models import (
    Assignment,
    FTQuestion,
    FTQuestionAnswer,
    FTQuestion,
    MemberAssignmentFTQuestion,
)


class AssignmentFTQuestionSerializer(serializers.ModelSerializer):
    id = fields.IntegerField(required=False)

    class Meta:
        model = FTQuestion
        fields = (
            "id",
            "title",
            "text",
            "file",
            "statrt_at",
            "end_at",
        )

    def validate(self, attrs):
        file = attrs.get("file")
        text = attrs.get("text")
        if file is None and text is None:
            raise ValidationError(detail="either file or text must be given")
        return attrs

    def create(self, validated_data):
        assignment = Assignment.objects.create(
            assignment=validated_data["assignment"],
            title=validated_data["title"],
            text=validated_data.get("text"),
            file=validated_data.get("file"),
            statrt_at=validated_data["statrt_at"],
            end_at=validated_data["end_at"],
        )
        return assignment


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
            "statrt_at",
            "end_at",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)

        return response


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
            "statrt_at",
            "end_at",
            "ftquestions",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)

        return response


class AssignmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = (
            "title",
            "description",
            "statrt_at",
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
            statrt_at=validated_data["statrt_at"],
            end_at=validated_data["end_at"],
        )
        return assignment


class AssignmentFTQuestionAnswerSerializer(serializers.ModelSerializer):
    id = fields.IntegerField(required=False)

    class Meta:
        model = FTQuestionAnswer
        fields = (
            "id",
            "answer_text",
            "answer_file",
        )

    def create(self, validated_data):
        ft_question_answer = Assignment.objects.create(
            ft_question=validated_data["ftquestion"],
            statrt_at=validated_data["answer_text"],
            end_at=validated_data["answer_file"],
        )
        return ft_question_answer


class FTQuestionSerializer(serializers.ModelSerializer):
    ftquestion_answers = FTQuestionAnswerSerializer

    class Meta:
        model = FTQuestion
        fields = (
            "assignment",
            "title",
            "text",
            "file",
            "statrt_at",
            "end_at",
            "ftquestion_answers",
        )

    def create(self, validated_data):
        ft_question_answer = Assignment.objects.create(
            ft_question=validated_data["ftquestion"],
            statrt_at=validated_data["answer_text"],
            end_at=validated_data["answer_file"],
        )
        return ft_question_answer


class MemberAssignmentFTQuestionScoreSerializer(serializers.Serializer):
    score = fields.IntegerField()


class MemberAssignmentFTQuestionSerializer(serializers.ModelSerializer):
    class Config:
        model = MemberAssignmentFTQuestion
        fields = (
            "score",
            "answered_text",
            "answered_file",
            "created_at",
            "updated_at",
        )
