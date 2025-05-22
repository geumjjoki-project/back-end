from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Expense

@receiver(post_save, sender=Expense)
def update_user_challenge_total_expense_on_save(sender, instance, **kwargs):
    if instance.user_challenge:
        from django.db.models import Sum
        uc = instance.user_challenge
        total = Expense.objects.filter(
            user_challenge=uc,
            date__gte=uc.start_date.date(),
            date__lte=uc.end_date.date()
        ).aggregate(total=Sum("amount"))["total"] or 0
        uc.total_expense = total
        uc.save(update_fields=["total_expense"])

@receiver(post_delete, sender=Expense)
def update_user_challenge_total_expense_on_delete(sender, instance, **kwargs):
    if instance.user_challenge:
        from django.db.models import Sum
        uc = instance.user_challenge
        total = Expense.objects.filter(
            user_challenge=uc,
            date__gte=uc.start_date.date(),
            date__lte=uc.end_date.date()
        ).aggregate(total=Sum("amount"))["total"] or 0
        uc.total_expense = total
        uc.save(update_fields=["total_expense"])