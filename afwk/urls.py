from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'ajax/classify/', views.classify, name='classify'),
    url(r'ajax/convertir/', views.convertir, name='convertir'),
    url(r'ajax/descargar/', views.descargar, name='descargar'),
    url(r'ajax/analizar/', views.analizar, name='analizar'),
] 
