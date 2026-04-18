from rest_framework import serializers
from .models import Transaction, Category, Budget
from django.utils.html import strip_tags

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'user']
        read_only_fields = ['user']

    def validate_name(self, value):
        if value:
            return strip_tags(value).strip()
        return value

class TransactionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'transaction_type', 'date', 'notes', 'category', 'category_id']

    def validate_notes(self, value):
        if value:
            return strip_tags(value).strip()
        return value

# --- NEW BUDGET SERIALIZER ---
class BudgetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Budget
        fields = ['id', 'user', 'category', 'category_id', 'limit_amount', 'month', 'year']
        read_only_fields = ['user']

    def validate_limit_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget limit must be greater than zero.")
        return value

    def validate_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value