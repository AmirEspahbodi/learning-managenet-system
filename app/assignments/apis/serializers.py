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
            "start_at",
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
    MemberTakeAssignment,
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

    class Meta:
        model = FTQuestionAnswer
        fields = (
            "answer_text",
            "answer_file",
        )


class AssignmentFTQuestionAnswerSerializer(serializers.ModelSerializer):
    id = fields.IntegerField(required=False)

    class Meta:
        model = FTQuestionAnswer
        fields = (
            "id",
            "answer_text",
            "answer_file",
        )

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
    class Config:
        model = MemberAssignmentFTQuestion
        fields = (
            "score",
            "answered_text",
            "answered_file",
            "created_at",
            "updated_at",
        )


class MemberTakeAssignmentSerilizer(serializers.ModelSerializer):
    member_take_exam_ftquestions = MemberAssignmentFTQuestionSerializer()

    class Config:
        model = MemberTakeAssignment
        fields = ("last_visit", "finish_at", "score", "member_take_exam_ftquestions")
