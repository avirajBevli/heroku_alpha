from django.db import models

# Create your models here.
class Asset(models.Model):
	security_id = models.CharField(max_length=100, default='') 
	ticker_name = models.CharField(max_length=100, null=True, blank=True) 
	# the way we have our data(in the CSV file), we may not know the ticker_name for each stock
	exp_return = models.FloatField(null=True, blank=True)
	exp_risk = models.FloatField(null=True, blank=True)
	def __str__(self):
		return self.security_id