from rest_framework import serializers, fields
from contents.models import Content, MemberVisitContent


class ContentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = (
            "title",
            "description",
            "file",
            "accessing_at",
        )

    def create(self, validated_data):
        content_count = Content.objects.filter(
            session=validated_data["session"]
        ).count()
        return Content.objects.create(
            session=validated_data["session"],
            content_number=content_count + 1,
            title=validated_data["title"],
            description=validated_data.get("description"),
            file=validated_data["file"],
            accessing_at=validated_data.get("accessing_at"),
        )


class ContentUpdateSerializer(serializers.ModelSerializer):
    title = fields.CharField(required=False)
    description = fields.CharField(required=False)
    file = fields.FileField(required=False)
    accessing_at = fields.DateTimeField(required=False)

    class Meta:
        model = Content
        fields = (
            "title",
            "description",
            "file",
            "accessing_at",
        )


class MemberVisitContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberVisitContent
        fields = ("id", "content", "member", "last_visit", "created_at")


class ContentResponseSerializer(serializers.ModelSerializer):
    member_contents = MemberVisitContentSerializer(many=True)

    class Meta:
        model = Content
        fields = (
            "id",
            "session",
            "content_number",
            "title",
            "description",
            "file",
            "accessing_at",
            "member_contents",
        )
