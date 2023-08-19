from rest_framework import serializers, fields
from rest_framework.exceptions import ValidationError
from ..models import (
    Exam,
    FTQuestion,
    FTQuestionAnswer,
    FTQuestion,
    MemberExamFTQuestion,
)


class ExamFTQuestionSerializer(serializers.ModelSerializer):
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
        exam = Exam.objects.create(
            exam=validated_data["exam"],
            title=validated_data["title"],
            text=validated_data.get("text"),
            file=validated_data.get("file"),
            statrt_at=validated_data["statrt_at"],
            end_at=validated_data["end_at"],
        )
        return exam


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = (
            "id",
            "session",
            "title",
            "description",
            "exam_number",
            "created_at",
            "statrt_at",
            "end_at",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)

        return response


class ExamResponseSerializer(serializers.ModelSerializer):
    ftquestions = ExamFTQuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = (
            "id",
            "session",
            "title",
            "description",
            "exam_number",
            "created_at",
            "statrt_at",
            "end_at",
            "ftquestions",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)

        return response


class ExamRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = (
            "title",
            "description",
            "statrt_at",
            "end_at",
        )

    def create(self, validated_data):
        exam_number = Exam.objects.filter(session=validated_data["session"]).count()
        # abount validated_data["session"]
        # save method has **kwargs that will destruct in validated_data
        # so in view we can pass session=self.session to save methos and access it in validated_data
        exam = Exam.objects.create(
            session=validated_data["session"],
            title=validated_data["title"],
            exam_number=exam_number,
            description=validated_data.get("description"),
            statrt_at=validated_data["statrt_at"],
            end_at=validated_data["end_at"],
        )
        return exam


class ExamFTQuestionAnswerSerializer(serializers.ModelSerializer):
    id = fields.IntegerField(required=False)

    class Meta:
        model = FTQuestionAnswer
        fields = (
            "id",
            "answer_text",
            "answer_file",
        )

    def create(self, validated_data):
        ft_question_answer = Exam.objects.create(
            ft_question=validated_data["ftquestion"],
            statrt_at=validated_data["answer_text"],
            end_at=validated_data["answer_file"],
        )
        return ft_question_answer


class ExamFTQuestionSerializer(serializers.ModelSerializer):
    ftquestion_answers = ExamFTQuestionAnswerSerializer

    class Meta:
        model = FTQuestion
        fields = (
            "exam",
            "title",
            "text",
            "file",
            "statrt_at",
            "end_at",
            "ftquestion_answers",
        )

    def create(self, validated_data):
        ft_question_answer = Exam.objects.create(
            ft_question=validated_data["ftquestion"],
            statrt_at=validated_data["answer_text"],
            end_at=validated_data["answer_file"],
        )
        return ft_question_answer


class MemberExamFTQuestionScoreSerializer(serializers.Serializer):
    score = fields.IntegerField()


class MemberExamFTQuestionSerializer(serializers.ModelSerializer):
    class Config:
        model = MemberExamFTQuestion
        fields = (
            "score",
            "answered_text",
            "answered_file",
            "created_at",
            "updated_at",
        )
