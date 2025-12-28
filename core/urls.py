from django.contrib import admin
from django.urls import path, include
from expenses.views import home, api_info, health

urlpatterns = [
    path('', home, name='home'),
    path('api/', api_info, name='api_info'),
    path('health/', health, name='health'),
    path('admin/', admin.site.urls),
    path('expenses/', include('expenses.urls')),
]
