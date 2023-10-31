from django.db import models

class Carrier(models.Model):
    logo = models.ImageField(default='carrier_logos/default_logo.png',upload_to='carrier_logos/', null=True)
    name = models.CharField(max_length=255)
    api_base_url = models.URLField()
    api_key = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

class CarrierStateConversion(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    carrier_state = models.CharField(max_length=255)
    company_website_state = models.CharField(max_length=255)



