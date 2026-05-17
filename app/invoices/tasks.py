import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
from django.db.models.functions import TruncDate

from invoices.models import Invoice

logger = logging.getLogger(__name__)


@shared_task
def send_top_sales_days_email():
    top_days = (
        Invoice.objects
        .filter(active=True)
        .annotate(day=TruncDate("invoice_date"))
        .values("day")
        .annotate(total_sales=Sum("total"))
        .order_by("-total_sales")[:10]
    )

    lines = ["Top 10 días con mayores ventas:\n"]

    for index, item in enumerate(top_days, start=1):
        lines.append(
            f"{index}.- {item['day']} - ${item['total_sales']}."
        )

    message = "\n".join(lines)

    send_mail(
        subject="Reporte del Top 10 de días con más ventas.",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.REPORT_RECIPIENT_EMAIL],
        fail_silently=False,
    )

    logger.info("Email enviado satisfactoriamente.")
