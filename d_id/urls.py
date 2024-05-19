from django.urls import path

from . import views

app_name = "d_id"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
]
