from django.urls import path
from . import views

app_name = "challenges"

urlpatterns = [
    path("", views.ChallengeView.as_view(), name="challenge_list"),
    path('<int:challenge_id>/', views.ChallengeDetailView.as_view(), name='challenge_detail'),
    path('personal/', views.UserChallengeView.as_view(), name='user_challenge_list_view')
]
