from django.urls import path

from . import views

app_name = "line_qa_with_gpt"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
]
