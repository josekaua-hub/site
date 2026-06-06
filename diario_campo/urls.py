from django.urls import path
from . import views

urlpatterns = [
    path('', views.selecionar_campo, name='diario_campo'),
    path('registro/<int:campo_id>/', views.diario_campo, name='diario_campo_form'),
    path('registro/delete/<int:registro_id>/', views.excluir_registro, name='excluir_registro'),
    path('delete/<int:campo_id>/', views.excluir_campo, name='excluir_campo'),
    path('campo/editar/<int:campo_id>/', views.editar_campo, name='editar_campo'),
    path('campo/<int:campo_id>/reiniciar/', views.reiniciar_ciclo, name='reiniciar_ciclo'),
    path('download/<int:campo_id>/', views.download_campo_registros, name='download_registros'),
    path('download_registro/<int:registro_id>/', views.download_registro, name='download_registro'),
    path('download_campo/<int:campo_id>/', views.download_campo_registros, name='download_campo_registros'),
    path('download_ciclo/<int:campo_id>/<int:numero_ciclo>/', views.download_ciclo, name='download_ciclo'),
    path('download_todos/<int:campo_id>/', views.download_todos_ciclos, name='download_todos_ciclos'),
]