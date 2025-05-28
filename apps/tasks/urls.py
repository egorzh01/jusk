from django.urls import path

from apps.tasks.views import index

urlpatterns = [
    path("", index, name="index"),
]
