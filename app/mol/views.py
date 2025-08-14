from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, parsers
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from mol import serializers as auth_serializers
from mol import models
from mol.permissions import CustomDjangoModelPermission



@extend_schema_view(
    post=extend_schema(
        description="Авторизоваться с помощью логина и пароля.",
        tags=["Авторизация"],
        summary="Авторизоваться с помощью логина и пароля.",
    ),
)
class Login(APIView):
    permission_classes = (AllowAny,)
    serializer_class = auth_serializers.LoginSerializer

    def post(self, request):
        data = request.data
        login = data.get("login")
        password = data.get("password")

        if not login:
            raise ValidationError("Введите логин", code=status.HTTP_400_BAD_REQUEST)

        if not password:
            raise ValidationError("Введите пароль", code=status.HTTP_400_BAD_REQUEST)

        user = authenticate(login=login, password=password)
        if not user:
            raise ValidationError("Такого пользователя не существует.", code=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        description="Выйти из системы.",
        tags=["Авторизация"],
        summary="Выйти из системы.",
    ),
)
class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)

        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)


# region
@extend_schema_view(
    create=extend_schema(
        summary="Подписаться на рассылку.",
        tags=["Рассылка"],
    ),
)
# endregion
class MailViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny, CustomDjangoModelPermission,)
    queryset = models.Mail.objects.all()
    serializer_class = auth_serializers.MailSerializer
    http_method_names = ['post']



# region
@extend_schema_view(
    list=extend_schema(
        summary="Получить список проектов.",
        tags=["Проекты"],
    ),
    retrieve=extend_schema(
        summary="Получить информацию о проекте по ID.",
        tags=["Проекты"],
    ),
    create=extend_schema(
        summary="Добавить проект.",
        tags=["Проекты"],
    ),
    update=extend_schema(
        summary="Обновить информацию о проекте по ID.",
        tags=["Проекты"],
    ),
    partial_update=extend_schema(
        summary="Частичное обновить информацию о проекте по ID.",
        tags=["Проекты"],
    ),
    destroy=extend_schema(
        summary="Удалить проект по ID.",
        tags=["Проекты"],
    ),
)
# endregion
class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, CustomDjangoModelPermission,)
    queryset = models.Project.objects.all()
    serializer_class = auth_serializers.ProjectSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = (AllowAny, )

        return super(self.__class__, self).get_permissions()


# region
@extend_schema_view(
    list=extend_schema(
        summary="Получить список всех блогов.",
        tags=["Блоги"],
    ),
    retrieve=extend_schema(
        summary="Получить информацию о блоге по ID.",
        tags=["Блоги"],
    ),
    create=extend_schema(
        summary="Добавить новый блог.",
        tags=["Блоги"],
    ),
    update=extend_schema(
        summary="Обновить информацию о блоге по ID.",
        tags=["Блоги"],
    ),
    partial_update=extend_schema(
        summary="Частичное обновить информацию о блоге по ID.",
        tags=["Блоги"],
    ),
    destroy=extend_schema(
        summary="Удалить блог по ID.",
        tags=["Блоги"],
    ),
)
# endregion
class BlogViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, CustomDjangoModelPermission,)
    queryset = models.Blog.objects.all()
    serializer_class = auth_serializers.BlogSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    parser_classes = (parsers.MultiPartParser, JSONParser)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = (AllowAny, )

        return super(self.__class__, self).get_permissions()


@extend_schema_view(
    post=extend_schema(
        description="Оставить клиентскую заявку.",
        tags=["Заявки"],
        summary="Оставить клиентскую заявку.",
        request=auth_serializers.RequestNoteSerializer,
        responses={200: OpenApiResponse(description="Успешный ответ с сообщением")},
    ),
)
class RequestNote(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = auth_serializers.RequestNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        name = serializer.validated_data['name']
        email = serializer.validated_data['email']

        email_to = settings.EMAIL_TO
        if not email_to:
            return Response(
                {"error": "Email получателя не настроен."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


        context = {
            'name': name,
            'phone': phone,
            'request_time': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
            'email': email,
        }

        html_content = render_to_string('emails/request_note.html', context)

        email = EmailMessage(
            subject=f'Новая заявка',
            body=html_content,
            from_email=f'noreply@mail.ru',
            to=[email_to],
        )
        email.content_subtype = 'html'
        email.send()

        return Response(
            {"successMessage": "Ваша заявка успешно принята."},
            status=status.HTTP_200_OK
        )
