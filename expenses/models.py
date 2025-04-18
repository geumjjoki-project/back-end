from django.db import models
from django.conf import settings

# Create your models here.
class ExpenseCategory(models.Model):
    expense_category_id = models.AutoField(primary_key=True)
    expense_category_name = models.CharField(max_length=100)
    
class ExpenseSubCategory(models.Model):
    expense_sub_category_id = models.AutoField(primary_key=True)
    expense_sub_category_name = models.CharField(max_length=100)
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    
class Expense(models.Model):
    expense_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expense_description = models.TextField()
    expense_cost = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateTimeField()
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    expense_sub_category = models.ForeignKey(ExpenseSubCategory, on_delete=models.CASCADE, null=True, blank=True)