from django.contrib import admin
from .models import Usuario_acceso, Lista_de_espera

@admin.register(Usuario_acceso)
class Admin_Usuario_acceso(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'nombre', 'fecha', 'status', 'status_holder', 'fecha_peticion_holder', 'wallet')
    list_filter = ('id',)

@admin.register(Lista_de_espera)
class Admin_Lista_de_espera(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_peticion', 'wallet')
    list_filter = ('id',)