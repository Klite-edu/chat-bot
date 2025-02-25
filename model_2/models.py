from django.db import models

# Create your models here.
class test_chat(models.Model):
    chat = models.CharField(max_length=1000)
    user_id = models.CharField(max_length=20)
    role = models.CharField(max_length=10)
