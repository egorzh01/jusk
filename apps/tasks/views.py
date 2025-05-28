from typing import Any

from django.views.generic import TemplateView

from apps.tasks.models import Task


class HomeView(TemplateView):
    http_method_names = ["get"]
    template_name = "tasks/home.html"
    extra_context = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tasks = Task.objects.filter(executor=self.request.user).order_by("updated_at")  # type: ignore
        context["tasks"] = tasks
        return context
