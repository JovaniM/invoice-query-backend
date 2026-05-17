from django.urls import path

from . import views

app_name = "invoices"

urlpatterns = [
    path('invoices/', views.InvoiceListView.as_view(), name='invoices'),
]
