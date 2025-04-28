from rest_framework import serializers
from .models import Expense, ExpenseAnalysis, Category
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


# 에러 응답 정의
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="에러 응답 예시",
            value={
                "status": "error",
                "message": "시작일 형식이 잘못되었습니다",
                "error_code": "INVALID_START_DATE",
            },
        )
    ]
)
class ErrorResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
    error_code = serializers.CharField()


# 카테고리를 재귀적으로 반환
class RecursiveCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "children"]

    def get_children(self, obj):
        children = obj.child_category.all()
        if children.exists():
            return RecursiveCategorySerializer(children, many=True).data
        return []


# 지출내역에 들어가는 카테고리 목록
class InlineCategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="category_id")
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "parent"]

    def get_parent(self, obj):
        return obj.parent_category.name if obj.parent_category else None


# 전체지출내역
class ExpenseSerializer(serializers.ModelSerializer):
    category = InlineCategorySerializer()
    amount = serializers.SerializerMethodField()

    def get_amount(self, obj):
        return int(obj.amount)

    class Meta:
        model = Expense
        fields = (
            "expense_id",
            "date",
            "amount",
            "category",
            "description",
        )
