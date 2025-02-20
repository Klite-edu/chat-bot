from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),   
    path('file_upload', views.file_upload, name='file_upload'),
    path('Business_page', views.Business_page, name='Business_page'),
    path('Business_login', views.Business_login, name='Business_login'),
    path('Business_dashboard/<str:business_name>', views.Business_dashboard, name='Business_dashboard'),
    path('client_page', views.client_page, name='client_page'),
    path('client_sign_up', views.client_sign_up, name='client_sign_up'),
    path('client_login', views.client_login, name='client_login'),
    path('home/<str:encrypted_bussiness_name>/<str:encrypted_client_number>/', views.home, name='home'),
    path('exit_session/', views.exit_session, name='exit_session'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
