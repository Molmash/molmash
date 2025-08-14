from django.core.validators import RegexValidator
from rest_framework import serializers
from mol import models

from mol.constants import PHONE_REGEX, NAME_SERVICE_REGEX


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
    )

    class Meta:
        model = models.Account
        fields = ["login", "password"]


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Blog
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = "__all__"


class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mail
        fields = "__all__"


class RequestNoteSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=16,
        validators=[
            RegexValidator(
                regex=PHONE_REGEX,
                message="Телефон должен быть в международном формате без дефисов и скобок, например +123456789."
            )
        ]
    )
    name = serializers.CharField(
        max_length=100,
        help_text="Имя клиента",
        validators=[
            RegexValidator(
                regex=NAME_SERVICE_REGEX,
                message="Имя может содержать только русские и английские буквы и пробелы."
            )
        ]
    )
    email = serializers.EmailField(
        max_length=200,
        help_text="Email",
        error_messages={'invalid': 'Некорректный email адрес'}
    )
