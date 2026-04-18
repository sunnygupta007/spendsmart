import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Transaction, Category, Budget
from .serializers import TransactionSerializer, CategorySerializer, BudgetSerializer
from django.db.models import Sum
from django.http import HttpResponse
import csv
from django.db.models import Q, Sum, F  # Added F for chart data aggregation
from django.shortcuts import get_object_or_404  # Added for detail views

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def transaction_api(request):
    if request.method == 'GET':
        month = request.GET.get('month')
        year = request.GET.get('year')
        page = int(request.GET.get('page', 1))
        limit = 10  # Load 10 transactions at a time

        transactions = Transaction.objects.filter(user=request.user)
        if month and year:
            transactions = transactions.filter(date__year=year, date__month=month)

        # --- 1. GENERATE CHART DATA (Total for the whole month) ---
        expenses = transactions.filter(transaction_type='EXPENSE')
        chart_data_qs = expenses.annotate(cat_name=F('category__name')).values('cat_name').annotate(total=Sum('amount'))
        
        chart_data = {}
        for item in chart_data_qs:
            name = item['cat_name'] if item['cat_name'] else 'Uncategorized'
            chart_data[name] = float(item['total']) # Convert to float for JSON

        # --- 2. PAGINATE THE TRANSACTION LIST ---
        transactions = transactions.order_by('-date')
        total_count = transactions.count()
        start = (page - 1) * limit
        end = start + limit
        paginated_transactions = transactions[start:end]
        has_next = total_count > end

        serializer = TransactionSerializer(paginated_transactions, many=True)
        
        # Return the new paginated structure
        return Response({
            "results": serializer.data,
            "has_next": has_next,
            "chart_data": chart_data
        })
        
    elif request.method == 'POST':
        # --- DYNAMIC VALIDATION: Locked to Current Month only ---
        date_str = request.data.get('date')
        if date_str:
            try:
                tx_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                today = datetime.date.today()
                if tx_date.month != today.month or tx_date.year != today.year:
                    current_period = today.strftime('%B %Y')
                    return Response(
                        {"error": f"You can only add transactions for the current month ({current_period})."}, 
                        status=400
                    )
            except ValueError:
                return Response({"error": "Invalid date format."}, status=400)

        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# ... (rest of your existing views remain the same)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_get_categories(request):
    if request.method == 'GET':
        categories = Category.objects.filter(Q(user__isnull=True) | Q(user=request.user))
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def transaction_detail_api(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'DELETE':
        transaction.delete()
        return Response({"message": "Transaction deleted successfully"}, status=204)
        
    elif request.method == 'PUT':
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# ==========================================
# BUDGET API ENDPOINTS
# ==========================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def budget_api(request):
    if request.method == 'GET':
        # Default to current month/year if not provided in query params
        today = datetime.date.today()
        month = request.GET.get('month', today.month)
        year = request.GET.get('year', today.year)
        
        budgets = Budget.objects.filter(user=request.user, month=month, year=year)
        serializer = BudgetSerializer(budgets, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BudgetSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure a user can't create two budgets for the same category in the same month
            category_id = request.data.get('category_id')
            month = request.data.get('month')
            year = request.data.get('year')
            if Budget.objects.filter(user=request.user, category_id=category_id, month=month, year=year).exists():
                return Response({"error": "A budget for this category already exists for this month."}, status=400)
            
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def budget_detail_api(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)

    if request.method == 'DELETE':
        budget.delete()
        return Response(status=204)
        
    elif request.method == 'PUT':
        serializer = BudgetSerializer(budget, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_status_api(request):
    """
    The 'Budget Engine' calculation endpoint.
    Compares the budget limit against actual EXPENSES for the requested month.
    """
    today = datetime.date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    budgets = Budget.objects.filter(user=request.user, month=month, year=year)
    status_list = []

    for budget in budgets:
        # Calculate total spent in this category for this specific month/year
        total_spent = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            transaction_type='EXPENSE',
            date__year=year,
            date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0

        spent = float(total_spent)
        limit = float(budget.limit_amount)
        percentage = (spent / limit * 100) if limit > 0 else 0

        status_list.append({
            'budget_id': budget.id,
            'category_id': budget.category.id,
            'category_name': budget.category.name,
            'limit_amount': limit,
            'spent': spent,
            'remaining': limit - spent,
            'percentage_used': round(percentage, 2)
        })

    return Response(status_list)

# ==========================================
# REPORT EXPORT ENDPOINTS
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_transactions_csv(request):
    """
    Exports the authenticated user's transactions as a downloadable CSV file.
    """
    # Create the HTTP response with the correct CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="spendsmart_transactions.csv"'

    writer = csv.writer(response)
    
    # Write the header row for the CSV
    writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Notes'])

    # Fetch ONLY the secure data belonging to this specific user
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # Loop through the data and write each row
    for tx in transactions:
        category_name = tx.category.name if tx.category else "Uncategorized"
        notes = tx.notes if tx.notes else ""
        writer.writerow([tx.date, tx.transaction_type, category_name, tx.amount, notes])

    return response