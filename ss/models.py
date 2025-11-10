from django.db import models

class NiftyData(models.Model):
    date = models.DateField(primary_key=True)
    previousClose = models.FloatField(null=True, blank=True)
    open = models.FloatField(null=True, blank=True)
    dayHigh = models.FloatField(null=True, blank=True)
    dayLow = models.FloatField(null=True, blank=True)
    lastPrice = models.FloatField(null=True, blank=True)
    High = models.FloatField(null=True, blank=True)
    Low = models.FloatField(null=True, blank=True)
    Range = models.FloatField(null=True, blank=True)
    Gap = models.FloatField(null=True, blank=True)
    Change = models.FloatField(null=True, blank=True)
    Timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "nifty_data"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} - {self.lastPrice}"



