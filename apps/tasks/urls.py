from django.urls import path

from apps.tasks.views import HomeView

app_name = "tasks"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]
