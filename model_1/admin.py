from django.contrib import admin
from .models import Chats, Bussiness, Client

# class BusinessAdmin(admin.ModelAdmin):
#     list_display = ('model', 'file', 'api')  # Display model, file, and API in the list view
#     search_fields = ('model', 'api')  # Allow searching by model and API key
#     list_filter = ('model',)  # Filter by model field

# # Register the Business model with the custom admin class
# admin.site.register(Business, BusinessAdmin)

# showing the data at admin panel
admin.site.register(Chats)
admin.site.register(Bussiness)
admin.site.register(Client)