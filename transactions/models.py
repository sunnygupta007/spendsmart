from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. CATEGORY MODEL
# ==========================================
class Category(models.Model):
    name = models.CharField(max_length=50)
    # If the user is blank, it means it's a default category (like 'Groceries' or 'Rent')
    # If linked to a user, it's a custom category they created.
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

# ==========================================
# 2. TRANSACTION MODEL
# ==========================================
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} | {self.transaction_type}: ₹{self.amount} on {self.date}"

# ==========================================
# 3. BUDGET LIMIT MODEL
# ==========================================
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    limit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField() 
    year = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.category.name} Budget: ₹{self.limit_amount}"