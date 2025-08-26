from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.db.models.signals import post_save
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
    # ext = filename.split(".")[-1]
    # filename = "%s.%s" % (instance.user.id, filename)
    return f"user_{instance.user.username }/{filename}"



class Profile(models.Model):
    pid = ShortUUIDField(primary_key=True, length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvwxyz12345")
    image = models.FileField(upload_to=user_directory_path, default="images\default.png", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    First_name = models.CharField(max_length = 20,blank=True, null=True)
    last_name = models.CharField(max_length = 20,blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    Country = models.CharField(max_length = 20, default="South Africa") 
    Province = models.CharField(max_length = 20, blank=True, null=True) 
    City = models.CharField(max_length = 20, blank=True, null=True) 
    
    wallet = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    verified = models.BooleanField(default=False)
    
    date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ["-date"]
        
    def __str__(self):
        return f" belongs to {self.user}"
        

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()     
    
post_save.connect(create_user_profile,sender=User)
post_save.connect(save_user_profile,sender=User)


