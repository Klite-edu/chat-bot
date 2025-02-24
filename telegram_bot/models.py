from django.db import models

# Create your models here.
class Users(models.Model):
    user_id = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)

    def __str__(self):
        return f'id = {self.user_id} name = {self.user_name}'