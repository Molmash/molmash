from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from mol.managers import AccountManager
from mol.utils import generate_uuid, LowercaseEmailField
from mol.validators import validate_login, validate_name, validate_phone

from storages.backends.ftp import FTPStorage
from django.conf import settings


fs = FTPStorage(location=settings.FTP_STORAGE_LOCATION)


class Account(AbstractUser):
    USERNAME_FIELD = "login"
    REQUIRED_FIELDS = []
    username = None

    id = models.CharField(
        default=generate_uuid, primary_key=True, editable=False, max_length=40, verbose_name="GUID аккаунта"
    )
    first_name = models.CharField(max_length=50, verbose_name="Имя", help_text="Имя", validators=[validate_name])
    last_name = models.CharField(max_length=50, verbose_name="Фамилия", help_text="Фамилия", validators=[validate_name])
    middleName = models.CharField(
        verbose_name="Отчество",
        help_text="Отчество",
        max_length=50,
        blank=True,
        null=True,
        validators=[validate_name]
    )
    login = models.CharField(
        verbose_name="Логин",
        max_length=30,
        db_index=True,
        unique=True,
        error_messages={"unique": "Значение логина должно быть уникальным."},
        validators=[validate_login]
    )
    email = LowercaseEmailField(
        verbose_name="Email",
        unique=True,
        error_messages={"unique": "Значение почты должно быть уникальным."},
    )
    phone = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        verbose_name="Телефон",
        validators=[validate_phone]
    )

    objects = AccountManager()

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middleName}"

    @property
    def access_token(self) -> str:
        return str(RefreshToken.for_user(self).access_token)

    @property
    def refresh_token(self) -> str:
        return str(RefreshToken.for_user(self))

    def __str__(self):
        return self.login

    def __repr__(self):
        return f"{self.__class__.__name__} (ID: {self.pk})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("login",)


class Blog(models.Model):
    id = models.CharField(
        default=generate_uuid, primary_key=True, editable=False, max_length=40, verbose_name="GUID блога"
    )
    title = models.CharField(
        max_length=500,
        verbose_name="Заголовок",
        help_text="Заголовок"
    )
    subject = models.CharField(
        verbose_name="Блог/новости",
        help_text="Блог/новости",
        max_length=100,
    )
    category = models.CharField(
        max_length=250,
        verbose_name="Бизнес, продукт",
        help_text="Бизнес, продукт"
    )
    image = models.ImageField(
        storage=fs,
        upload_to="media/blogs/",
        help_text="Изображение",
        verbose_name="Изображение",
        blank=True,
        null=True
    )
    text = models.TextField(
        verbose_name="Текст",
        help_text="Текст"
    )

    class Meta:
        verbose_name = "Блоги"
        verbose_name_plural = "Блог"


class Project(models.Model):
    id = models.CharField(
        default=generate_uuid, primary_key=True, editable=False, max_length=40, verbose_name="GUID проекта"
    )
    title = models.CharField(
        max_length=500,
        verbose_name="Заголовок",
        help_text="Заголовок"
    )
    image = models.ImageField(
        storage=fs,
        upload_to="media/projects/",
        help_text="Изображение",
        verbose_name="Изображение",
        blank=True,
        null=True
    )
    text = models.TextField(
        verbose_name="Текст",
        help_text="Текст"
    )

    class Meta:
        verbose_name = "Проекты"
        verbose_name_plural = "Проект"


class Mail(models.Model):
    id = models.CharField(
        default=generate_uuid, primary_key=True, editable=False, max_length=40, verbose_name="GUID рассылки"
    )
    email = LowercaseEmailField(
        verbose_name="Email",
        unique=True,
        error_messages={"unique": "Значение почты должно быть уникальным."},
    )

    class Meta:
        verbose_name = "Подписки на рассылку"
        verbose_name_plural = "Подписка на рассылку"
