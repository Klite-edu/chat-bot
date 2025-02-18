from django.db import models

class Bussiness(models.Model):
    bussiness_name = models.CharField(max_length=30)
    api_key = models.CharField(max_length=100)
    file = models.CharField(max_length=50)
    llm_model = models.CharField(max_length=50)

    def __str__(self):
        return f'bussiness = {self.bussiness_name} api = {self.api_key} file = {self.file} model = {self.llm_model}'


class Client(models.Model):
    client_number = models.CharField(max_length=20)
    bussiness_name = models.ForeignKey(Bussiness, on_delete=models.CASCADE)

    def __str__(self):
        return f'client = {self.client_number} bussiness = {self.bussiness_name}'


class Chats(models.Model):
    chat = models.CharField(max_length=1000)
    client_number = models.CharField(max_length=20)
    bussiness_name = models.ForeignKey(Bussiness, on_delete=models.CASCADE)  # Changed from CharField to ForeignKey
    is_client = models.BooleanField()
    time_of_chat = models.DateTimeField()

    # Showing chats in admin panel
    def __str__(self):
        return f'chat = {self.chat} client = {self.client_number} bussiness = {self.bussiness_name} is_client = {self.is_client} time {self.time_of_chat}'
