from django.urls import path
from . import views

app_name = 'church'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('visit/', views.visit, name='visit'),
    path('admins/', views.custom_admin_dashboard, name='church_admin_dashboard'),
 
    

]