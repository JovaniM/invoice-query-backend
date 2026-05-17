from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics
from .filters import InvoiceFilter
from .models import Invoice
from .serializers import InvoiceSerializer


@method_decorator(cache_page(60 * 5), name="dispatch")
class InvoiceListView(generics.ListAPIView):
    queryset = Invoice.objects.all().order_by("invoice_date")
    serializer_class = InvoiceSerializer
    filterset_class = InvoiceFilter
