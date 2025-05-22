from django.urls import path, include
from . import views

app_name = "rewards"

urlpatterns = [
    path("", views.reward_list, name="reward_index"),
    path("<int:reward_id>/", views.reward_detail, name="reward_detail"),
    path(
        "list/<int:reward_transaction_id>/",
        views.reward_transaction_detail,
        name="reward_transaction_detail",
    ),
    path("list/", views.reward_transaction_list, name="reward_transaction_list"),
    path("purchase/", views.reward_transaction_create, name="reward_transaction_create"),
]
