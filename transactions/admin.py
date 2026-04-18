from django.contrib import admin
from .models import Category, Transaction, Budget

# This tells Django to show these tables in the Admin Dashboard
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Budget)