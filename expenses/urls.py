from django.urls import path, include
from . import views

app_name = "expenses"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:expense_id>/", views.detail, name='detail'),
    path("summary/", views.summary, name="summary"),
]
