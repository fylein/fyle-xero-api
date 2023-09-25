from django.urls import path

from apps.tasks.views import TasksView

urlpatterns = [path("all/", TasksView.as_view())]
