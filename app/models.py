from django.db import models

class Agents_Details_Model(models.Model):
    SNO=models.AutoField(primary_key=True)
    ID=models.IntegerField(unique=True)
    NAME=models.CharField(max_length=100)
    ADDRESS=models.CharField(max_length=200)
    CITY=models.CharField(max_length=100)
    ZIPCODE=models.IntegerField()
    STATE=models.CharField(max_length=100)

