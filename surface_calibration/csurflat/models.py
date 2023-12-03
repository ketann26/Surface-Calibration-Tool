from django.db import models

# Create your models here.

class WorkOrder(models.Model):

    # Customer Details
    customer = models.CharField(max_length=255)
    work_order_number = models.CharField(max_length=50)
    date_created = models.DateField(auto_now_add=True)
    ref = models.CharField(max_length=100, null=True, blank=True)
    
    # Surface plate details
    surface_plate_id = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    surface_plate_type = models.CharField(max_length=50)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    grade = models.CharField(max_length=50)

    # Measurement Details
    num_rows = models.IntegerField()
    num_cols = models.IntegerField()
    bridge_length = models.IntegerField()
    start_temp = models.DecimalField(max_digits=5, decimal_places=2)
    end_temp = models.DecimalField(max_digits=5, decimal_places=2)


    # JSON fields for 5x8 table
    along_rows = models.JSONField(default=None)
    across_rows = models.JSONField(default=None)
    flatness = models.JSONField(null=True, blank=True, default=None)

    def __str__(self):
        return "{}:{}".format(self.customer,self.work_order_number)


