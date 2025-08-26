from django.db import models
from django.contrib.auth.models import User


class Repair(models.Model):
    repid = models.AutoField(primary_key=True,blank=False, null=False,auto_created=True)
    Model_Name = models.CharField(max_length=20, blank=True, null=True)
    Model_Year = models.CharField(max_length=4)
    Reg_Plate = models.CharField(max_length=15, blank=True, null=True)
    Vin_Number = models.CharField(max_length=30)
    Millage = models.CharField(max_length=7, default="N/A")
    DashDasplay_Pic = models.ImageField(upload_to="repairs/images", blank=True, null=True)
    Engine_Pic = models.ImageField(upload_to="repairs/images", blank=True, null=True)
    Damage_pic1 =  models.ImageField(upload_to="repairs/images", blank=True, null=True)
    Damage_pic2 =  models.ImageField(upload_to="repairs/images", blank=True, null=True)
    Damage_pic3 =  models.ImageField(upload_to="repairs/images", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    
    def __str__(self):
        return f"This car belongs to {self.user.username}"
    
