"""
URL configuration for Site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.selecionar_campo, name='diario_campo'),
    path('registro/<int:campo_id>/', views.diario_campo, name='diario_campo_form'),
    path('registro/delete/<int:registro_id>/', views.excluir_registro, name='excluir_registro'),
    path('delete/<int:campo_id>/', views.excluir_campo, name='excluir_campo'),
    path('download/<int:campo_id>/', views.download_registros, name='download_registros'),
    path('download_registro/<int:registro_id>/', views.download_registro, name='download_registro'),
    path('download_campo/<int:campo_id>/', views.download_campo_registros, name='download_campo_registros'),
    path('campo/editar/<int:campo_id>/', views.editar_campo, name='editar_campo'),
]
