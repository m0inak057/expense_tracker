from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_expense),
    path("list/<str:user_id>/", views.list_expenses),
    path("scan-receipt/", views.scan_receipt),
]
