
from django.db import models

class NiftyExpiry(models.Model):
    expiry_date = models.DateField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.expiry_date)


class NiftyOptionSnapshot(models.Model):
    expiry = models.ForeignKey(NiftyExpiry, on_delete=models.CASCADE, related_name='snapshots')
    fetch_date = models.DateField()

    strike = models.FloatField()
    option_type = models.CharField(max_length=10)  # CE or PE
    sequence = models.PositiveIntegerField(default=0)  # preserve NSE JSON order

    open_price = models.FloatField(null=True, blank=True)
    high_price = models.FloatField(null=True, blank=True)
    low_price = models.FloatField(null=True, blank=True)
    close_price = models.FloatField(null=True, blank=True)
    last_price = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)
    open_interest = models.FloatField(null=True, blank=True)
    iv = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('expiry', 'strike', 'option_type', 'fetch_date')
        ordering = ['sequence']  # default ordering when querying

    def __str__(self):
        return f"{self.expiry.expiry_date} | {self.option_type} | {self.strike} | {self.fetch_date}"
