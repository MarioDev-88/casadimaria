# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.hashers import make_password, check_password as ch_pass

class Usuario(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    telefono = models.CharField(max_length=150, verbose_name='Correo')
    password = models.CharField(max_length=250)
    tipo = models.IntegerField(default=1, verbose_name="Administrador = 1 / Coordinador")
    identificacion = models.CharField(max_length=50, verbose_name='Identificacion')
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True,null=True, verbose_name="Última actualización")

    def save(self,*args,**kwargs):
        if self.password=="":
            self.password = make_password(self.password)
        else:
            self.password = make_password(self.password)
        super(Usuario,self).save(*args,**kwargs)

    def edit_no_password(self,*args,**kwargs):
        super(Usuario,self).save(*args,**kwargs)

    def check_password(self, passw):
        return ch_pass(passw,self.password)

class Platillo(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True,null=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True,null=True, verbose_name="Última actualización")

class PlatilloJovene(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    created_at = models.DateTimeField(auto_now_add=True,null=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True,null=True, verbose_name="Última actualización")

class Evento(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    created_at = models.DateTimeField(auto_now_add=True,null=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True,null=True, verbose_name="Última actualización")

    def __str__(self):
        return self.nombre

class Complemento(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True,null=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True,null=True, verbose_name="Última actualización")

class CostoFijo(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True,null=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True,null=True, verbose_name="Última actualización")

class Colaboradore(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True,null=True, verbose_name="Última actualización")

    def __str__(self):
        return self.nombre

class Cotizacion(models.Model):
    fecha_evento = models.DateTimeField(verbose_name="Fecha y hora del evento")
    hora_inicio = models.TimeField(verbose_name="Hora de inicio del evento")
    hora_fin = models.TimeField(verbose_name="Hora de finalización del evento")
    fecha_confirmacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de confirmación")
    fecha_cancelacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de cancelación")
    nombre_novio = models.CharField(max_length=200, verbose_name='Nombre novio')
    nombre_novia = models.CharField(max_length=200, verbose_name='Nombre novia', null=True, blank=True)
    telefono_novio = models.CharField(max_length=50, verbose_name='Telefono novio')    
    telefono_novia = models.CharField(max_length=50, verbose_name='Telefono novia', null=True, blank=True)    
    correo_electronico = models.CharField(max_length=150, verbose_name='Correo novio', null=True, blank=True)
    evento = models.ForeignKey(Evento, related_name="evento_cotizacion", on_delete=models.CASCADE)
    platillo = models.ForeignKey(Platillo, related_name="platillo_cotizacion", on_delete=models.CASCADE)
    platillo_jovenes = models.ForeignKey(PlatilloJovene, related_name="platillo_jovenes_cotizacion", on_delete=models.CASCADE, null=True, blank=True)
    adicional = models.ForeignKey(Complemento, related_name="complemento_cotizacion", on_delete=models.CASCADE, null=True, blank=True)
    numero_personas = models.IntegerField(verbose_name="Numero de personas")
    numero_jovenes = models.IntegerField(verbose_name="Numero de personas jovenes", null=True, blank=True)
    colaborador = models.ForeignKey(Colaboradore, related_name="colaborar_cotizacion", on_delete=models.CASCADE, null=True, blank=True)
    status = models.IntegerField(default=1)
    creada_por = models.ForeignKey(Usuario, related_name="creada_usuario", null=True, blank=True, on_delete=models.CASCADE)
    contrato = models.BooleanField(default=False)
    folio = models.CharField(max_length=100, verbose_name='Folio')
    fecha_expiracion = models.DateTimeField(null=True, verbose_name="Fecha de expiracion")
    created_at = models.DateTimeField(auto_now_add=True,null=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True,null=True, verbose_name="Última actualización")

class DetalleCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, related_name="detalle_cotizacion", on_delete=models.CASCADE, null=True, blank=True)
    npp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="(Numero de personas * platillo)")
    npb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="(Numero de personas * bebidas)")
    npm = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="(Numero de personas * meseros)")
    npj = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="(Numero de personas * uso jardin)")
    npc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="(Numero de personas * Complemento)")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="(Costo fijo + npp + npb + npm + npj + npc)")
    created_at = models.DateTimeField(auto_now_add=True,null=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True,null=True, verbose_name="Última actualización")

class DocumentoCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, related_name="documentos_cotizacion", on_delete=models.CASCADE)
    url_cotizacion = models.CharField(max_length=500, verbose_name="Ruta de la cotizacion", null=True, blank=True)
    url_contrato = models.CharField(max_length=500, verbose_name="Ruta del contrato", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True,null=True, verbose_name="Última actualización")
