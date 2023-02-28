from django.db import connections
from django.db import models

class users(models.Model):
    Type = models.CharField(max_length=50)
    First_Name = models.CharField(max_length=50)
    Last_Name = models.CharField(max_length=50)
    EmployeeID = models.IntegerField()

    class Meta:
        db_table = 'users'
