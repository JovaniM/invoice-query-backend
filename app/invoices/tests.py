from datetime import datetime
from django.db import connection
from django.test import override_settings, TransactionTestCase
from rest_framework.test import APIClient
from unittest.mock import patch

from invoices.models import Invoice
from invoices.tasks import send_top_sales_days_email


class InvoiceTestDatabaseMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            try:
                schema_editor.create_model(Invoice)
            except Exception:
                pass

    @classmethod
    def tearDownClass(cls):
        try:
            with connection.schema_editor() as schema_editor:
                schema_editor.delete_model(Invoice)
        except Exception:
            pass
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        Invoice.objects.all().delete()


class InvoiceAPITestCase(InvoiceTestDatabaseMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

        Invoice.objects.create(
            id=1,
            invoice_number="C30471",
            total=14.45,
            invoice_date=datetime(2024, 1, 1, 10, 0, 0),
            status="Vigente",
            active=True,
        )
        Invoice.objects.create(
            id=2,
            invoice_number="C30565",
            total=19.29,
            invoice_date=datetime(2024, 1, 2, 10, 0, 0),
            status="Vencido",
            active=False,
        )

    def test_list_invoices(self):
        response = self.client.get("/api/v1/invoices/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_filter_active_invoices(self):
        response = self.client.get("/api/v1/invoices/?active=true")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertTrue(response.data["results"][0]["active"])

    def test_filter_invoice_date_gte(self):
        response = self.client.get("/api/v1/invoices/?invoice_date__gte=2024-01-02")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["invoice_number"], "C30565")

    def test_filter_invoice_date_lte(self):
        response = self.client.get("/api/v1/invoices/?invoice_date__lte=2024-01-01")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["invoice_number"], "C30471")

    def test_filter_invoice_date_range(self):
        response = self.client.get("/api/v1/invoices/?invoice_date__gte=2024-01-01&invoice_date__lte=2024-01-02")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["invoice_number"], "C30471")
        self.assertEqual(response.data["results"][1]["invoice_number"], "C30565")

    def test_pagination_limit(self):
        response = self.client.get("/api/v1/invoices/?limit=1&offset=0")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)


@override_settings(
    DEFAULT_FROM_EMAIL="test@example.com",
    REPORT_RECIPIENT_EMAIL="recipient@example.com",
)
class SendTopSalesDaysEmailTaskTestCase(InvoiceTestDatabaseMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        Invoice.objects.create(
            id=1,
            invoice_number="C30723",
            total=1000,
            invoice_date=datetime(2024, 1, 1, 10, 0, 0),
            status="Vigente",
            active=True,
        )
        Invoice.objects.create(
            id=2,
            invoice_number="C30676",
            total=2000.1,
            invoice_date=datetime(2024, 1, 1, 12, 0, 0),
            status="Vigente",
            active=True,
        )
        Invoice.objects.create(
            id=3,
            invoice_number="C30565",
            total=9999,
            invoice_date=datetime(2024, 1, 3, 12, 0, 0),
            status="Vigente",
            active=False,
        )

    @patch("invoices.tasks.send_mail")
    def test_send_top_sales_days_email(self, mock_send_mail):
        send_top_sales_days_email()

        mock_send_mail.assert_called_once()

        _, kwargs = mock_send_mail.call_args

        self.assertEqual(kwargs["subject"], "Reporte del Top 10 de días con más ventas.")
        self.assertEqual(kwargs["from_email"], "test@example.com")
        self.assertEqual(kwargs["recipient_list"], ["recipient@example.com"])
        self.assertIn("2024-01-01", kwargs["message"])
        self.assertIn("3000.10", kwargs["message"])
        self.assertNotIn("2024-01-03", kwargs["message"])
        self.assertNotIn("9999", kwargs["message"])
