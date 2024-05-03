from django.urls import path
from . import views

app_name = 'qa_with_src'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]
