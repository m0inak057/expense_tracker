from django.contrib import admin
from .models import Expense, Receipt


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'date', 'amount', 'category', 'created_at']
    list_filter = ['category', 'date', 'created_at']
    search_fields = ['user_id', 'description', 'category']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['expense', 'file_url', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
