import django_filters

from invoices.models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    invoice_date__gte = django_filters.DateFilter(
        field_name="invoice_date",
        lookup_expr="date__gte",
    )

    invoice_date__lte = django_filters.DateFilter(
        field_name="invoice_date",
        lookup_expr="date__lte",
    )

    active = django_filters.BooleanFilter()

    class Meta:
        model = Invoice
        fields = [
            "invoice_date__gte",
            "invoice_date__lte",
            "active",
        ]
