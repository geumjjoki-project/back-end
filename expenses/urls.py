from django.urls import path, include
from . import views

app_name = "expenses"

urlpatterns = [
    path("", views.ExpenseListView.as_view(), name="index"),
    path("<int:expense_id>/", views.ExpenseDetailView.as_view(), name='detail'),
    path("summary/", views.ExpenseSummaryView.as_view(), name="summary"),
    path("categories/roots/", views.RootCategoryListView.as_view(), name="root_categories"),
]
