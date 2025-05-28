from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "title": "Главная страница",
        "message": "Добро пожаловать на мой блог!",
    }
    return render(
        request=request,
        template_name="base.html",
        context=context,
    )
