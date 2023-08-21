from rest_framework import serializers, fields
from rest_framework.exceptions import ValidationError
from ..models import (
    Exam,
    FTQuestion,
    FTQuestionAnswer,
    FTQuestion,
    MemberExamFTQuestion,
    MemberTakeExam,
)


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
            "start_at",
            "end_at",
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
            "start_at",
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
            start_at=validated_data["start_at"],
            end_at=validated_data["end_at"],
        )
        return exam


class ExamRequestUpdateSerializer(serializers.ModelSerializer):
    title = fields.CharField(required=False)
    description = fields.CharField(required=False)
    start_at = fields.DateTimeField(required=False)
    end_at = fields.DateTimeField(required=False)

    class Meta:
        model = Exam
        fields = (
            "title",
            "description",
            "start_at",
            "end_at",
        )


class ExamFTQuestionAnswerSerializer(serializers.ModelSerializer):
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
            ft_question=validated_data["exam_ftquestion"],
            answer_text=validated_data.get("answer_text"),
            answer_file=validated_data.get("answer_file"),
        )
        return ft_question_answer


class ExamFTQuestionAnswerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FTQuestionAnswer
        fields = (
            "answer_text",
            "answer_file",
        )


class ExamFTQuestionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FTQuestion
        fields = (
            "title",
            "text",
            "file",
            "start_at",
            "end_at",
        )


class ExamFTQuestionSerializer(serializers.ModelSerializer):
    ftquestion_answers = ExamFTQuestionAnswerSerializer(many=True)

    class Meta:
        model = FTQuestion
        fields = (
            "id",
            "exam",
            "title",
            "text",
            "file",
            "start_at",
            "end_at",
            "ftquestion_answers",
        )

    def create(self, validated_data):
        ft_question_answer = Exam.objects.create(
            ft_question=validated_data["exam_ftquestion"],
            start_at=validated_data["answer_text"],
            end_at=validated_data["answer_file"],
        )
        return ft_question_answer


class ExamFTQuestionUpdateSerializer(serializers.ModelSerializer):
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


class MemberTakeExamSerilizer(serializers.ModelSerializer):
    member_take_exam_ftquestions = MemberExamFTQuestionSerializer()

    class Config:
        model = MemberTakeExam
        fields = ("last_visit", "finish_at", "score", "member_take_exam_ftquestions")


class ExamFTQuestionSerializer(serializers.ModelSerializer):
    id = fields.IntegerField(required=False)
    ftquestion_answers = ExamFTQuestionAnswerSerializer(many=True)

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

    def create(self, validated_data):
        exam = Exam.objects.create(
            exam=validated_data["exam"],
            title=validated_data["title"],
            text=validated_data.get("text"),
            file=validated_data.get("file"),
            start_at=validated_data["start_at"],
            end_at=validated_data["end_at"],
        )
        return exam


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
            "start_at",
            "end_at",
            "ftquestions",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)

        return response
