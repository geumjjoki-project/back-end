from django.urls import path, include
from . import views

app_name = "expenses"

urlpatterns = [
    path("", views.index, name="index"),
]
