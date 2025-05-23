from django.urls import path, include
from . import views

app_name = "rewards"

urlpatterns = [
    path("", views.RewardListView.as_view(), name="reward_index"),
    path("<int:reward_id>/", views.RewardDetailView.as_view(), name="reward_detail"),
    path(
        "list/<int:reward_transaction_id>/",
        views.RewardTransactionDetailView.as_view(),
        name="reward_transaction_detail",
    ),
    path("list/", views.RewardTransactionListView.as_view(), name="reward_transaction_list"),
    path("purchase/", views.RewardTransactionCreateView.as_view(), name="reward_transaction_create"),
]
