from django.urls import path

from . import views

app_name = "line_qa_with_gpt"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("line_webhook/", views.LineWebHookView.as_view(), name="line_webhook"),
]
