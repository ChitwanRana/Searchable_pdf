# filepath: c:\Users\kushr\OneDrive\Desktop\New folder (3)\scanned\searchable\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('convert/', views.convert_pdf, name='convert_pdf'),
    path('download/', views.download_pdf, name='download_pdf'),
]