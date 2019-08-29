from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def crear_usuario_perfil(sender, instance, created, **kwargs):
    if created:
        Usuario_acceso.objects.create(usuario=instance)

class Usuario_acceso(models.Model):
    lista_holder = (("Activado", "Activado"), ("Desactivado", "Desactivado"), ("Pendiente", "Pendiente"))
    lista_status = (("Activado", "Activado"), ("Desactivado", "Desactivado"), ("Pendiente", "Pendiente"))
    usuario = models.CharField(max_length=255)
    nombre = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now=True)
    fecha_peticion_holder = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=255, choices=lista_status, default='Desactivado')
    status_holder = models.CharField(max_length=255, choices=lista_holder, default='Desactivado')
    wallet = models.CharField(max_length=255, unique=True, blank=True, null=True)
    registro_pagos = models.CharField(max_length=9999999, default='[]')


    def __User__(self):
        return self.status

    class Meta:
        ordering = ("id",)


class Lista_de_espera(models.Model):
    usuario = models.CharField(max_length=255)
    fecha_peticion = models.CharField(max_length=255)
    wallet = models.CharField(max_length=255, unique=True)


    def __User__(self):
        return self.fecha_peticion

    class Meta:
        ordering = ("id",)