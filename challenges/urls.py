from django.urls import path
from . import views

app_name = "challenges"

urlpatterns = [
    path("", views.challenge_list, name="challenge_list"),
    path('<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('personal', views.user_challenge_list_view, name='user_challenge_list_view')
]
