from django.db import models
import datetime 
# Create your models here.

class Product(models.Model):
    category = models.CharField(max_length=100, null=False, blank=False)
    num_of_products = models.IntegerField()
    time = datetime.datetime.now()

    def __str__(self):
        return f'{self.category} - {self.num_of_products}-{self.time}'
        
