from django.http import HttpRequest

from apps.users.models import User


class AuthenticatedHttpRequest(HttpRequest):
    user: User
