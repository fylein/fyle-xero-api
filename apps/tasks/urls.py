from django.urls import path

from .views import TasksView

urlpatterns = [path("all/", TasksView.as_view())]
    