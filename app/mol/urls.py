from django.urls import include, path
from rest_framework.routers import DefaultRouter

from mol import views

router = DefaultRouter(trailing_slash=False)

router.register(r"mail", views.MailViewSet, basename="api-mails")
router.register(r"projects", views.ProjectViewSet, basename="api-projects")
router.register(r"blogs", views.BlogViewSet, basename="api-blogs")


urlpatterns = [
    path("login/", views.Login.as_view()),
    path("logout/", views.Logout.as_view()),
    path('request-note/', views.RequestNote.as_view(), name='request-note'),
    path("", include(router.urls)),
]
