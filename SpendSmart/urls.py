from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

# Consolidated imports
from users.views import CookieTokenObtainPairView, LogoutAPIView, RegisterAPIView, current_user_api
from transactions.views import (
    transaction_api, 
    api_get_categories, 
    transaction_detail_api,
    budget_api,
    budget_detail_api,
    budget_status_api,
    export_transactions_csv  # <-- Add this!
)

# Wrap the HTML views in never_cache()
users_patterns = ([
    path('login/', never_cache(TemplateView.as_view(template_name='users/login.html')), name='login'),
    path('register/', never_cache(TemplateView.as_view(template_name='users/register.html')), name='register'),
], 'users')

transactions_patterns = ([
    path('', never_cache(TemplateView.as_view(template_name='transactions/dashboard.html')), name='dashboard'),
    path('add/', never_cache(TemplateView.as_view(template_name='transactions/transaction_form.html')), name='add_transaction'),
], 'transactions')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- YOUR SECURE API ENGINE ---
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', CookieTokenObtainPairView.as_view(), name='api_login'),
    path('api/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('api/me/', current_user_api, name='api_me'),
    
    # Transactions & Categories
    path('api/transactions/', transaction_api, name='transaction_api'),
    path('api/transactions/<int:pk>/', transaction_detail_api, name='transaction_detail_api'),
    path('api/categories/', api_get_categories, name='api_categories'),
    path('api/export/csv/', export_transactions_csv, name='export_csv'), # <-- Add this!
    
    # Budgets
    path('api/budgets/', budget_api, name='budget_api'),
    path('api/budgets/<int:pk>/', budget_detail_api, name='budget_detail_api'),
    path('api/budgets/status/', budget_status_api, name='budget_status_api'),
    
    # --- YOUR VANILLA JS FRONTEND ---
    path('users/', include(users_patterns)),
    path('', include(transactions_patterns)),
]