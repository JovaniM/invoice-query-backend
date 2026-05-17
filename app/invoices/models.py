from django.db import models


class Invoice(models.Model):
    id = models.IntegerField(primary_key=True)
    invoice_number = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=20, decimal_places=2)
    invoice_date = models.DateTimeField()
    status = models.CharField(max_length=100)
    active = models.BooleanField()

    class Meta:
        managed = False
        db_table = "invoices"
