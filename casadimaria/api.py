# -*- encoding: utf-8 -*-
from __future__ import division
import locale
from datetime import datetime, timedelta
import os
import pdb
from django.conf import settings
from django.utils.crypto import get_random_string
from django.db.models import Q
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS, Resource
from tastypie import fields
from tastypie.validation import Validation
from tastypie.authorization import Authorization
from tastypie.authentication import BasicAuthentication
from tastypie.exceptions import Unauthorized
from tastypie.authentication import Authentication
from tastypie.http import HttpUnauthorized, HttpResponse, HttpBadRequest, HttpNotFound
from tastypie.models import ApiKey
from tastypie.authentication import ApiKeyAuthentication
from tastypie.models import create_api_key  
from tastypie.cache import SimpleCache
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
import io
import json
from .models import *

class CrearColaboradores(ModelResource):
    class Meta:
        queryset = Colaboradore.objects.all()
        limit = 1
        resource_name = 'createcolaborador'
        allowed_methods = ['post']

    def post_list(self, request, **kwargs):
        data = json.loads(request.body)
        colaborador = Colaboradore()
        colaborador.nombre = data['nombre']
        colaborador.save()

        return HttpResponse(content_type='application/json', status=201)
    
class EliminarColaboradores(ModelResource):
    class Meta:
        queryset = Colaboradore.objects.all()
        resource_name = 'deletecolaborador'
        allowed_methods = ['delete']

    def obj_get(self, bundle, **kwargs):
        try:
            return Colaboradore.objects.get(pk=kwargs['pk'])
        except Colaboradore.DoesNotExist:
            raise HttpNotFound("Colaborador no encontrado")
        
    def obj_delete(self, bundle, **kwargs):
        colaborador = self.obj_get(bundle, **kwargs)
        colaborador.status = False
        colaborador.save()

class EditarCostoFijo(ModelResource):
    class Meta:
        queryset = CostoFijo.objects.all()
        resource_name = 'editcostofijo'
        allowed_methods = ['patch']

    def obj_get(self, bundle, **kwargs):
        try:
            return CostoFijo.objects.get(pk=kwargs['pk'])
        except CostoFijo.DoesNotExist:
            raise HttpNotFound("Costo Fijo no encontrado")

    def obj_update(self, bundle, **kwargs):
        # Aquí puedes personalizar la lógica de actualización si es necesario        
        costo_fijo = self.obj_get(bundle, **kwargs)
        costo_fijo.precio = bundle.data['precio']
        costo_fijo.save()

class EditarPlatillo(ModelResource):
    class Meta:
        queryset = Platillo.objects.all()
        resource_name = 'editplatillo'
        allowed_methods = ['patch']

    def obj_get(self, bundle, **kwargs):
        try:
            return Platillo.objects.get(pk=kwargs['pk'])
        except Platillo.DoesNotExist:
            raise HttpNotFound("Costo Fijo no encontrado")

    def obj_update(self, bundle, **kwargs):
        # Aquí puedes personalizar la lógica de actualización si es necesario        
        platillo = self.obj_get(bundle, **kwargs)
        platillo.precio = bundle.data['precio']
        platillo.save()
    
class CreateUser(ModelResource):
    class Meta:
        queryset = Usuario.objects.all()
        limit = 1
        resource_name = 'createuser'
        allowed_methods = ['post']

    def post_list(self, request, **kwargs):
        data = json.loads(request.body)
        datosarray = {}
        usuario = Usuario()
        usuario.nombre = data['nombre']
        usuario.telefono = data['telefono']
        usuario.password = make_password(data['pwd'])
        usuario.identificacion = data['identificacion'] #get_random_string(length=8)
        usuario.edit_no_password()

        return HttpResponse(content_type='application/json', status=201)
    
class GetUser(ModelResource):
    class Meta:
        queryset = Usuario.objects.all()
        limit = 0
        resource_name = 'getuser'
        allowed_methods = ['get']
    
class Login(ModelResource):
    class Meta:
        queryset = Usuario.objects.all()
        limit = 1
        resource_name = 'login'
        allowed_methods = ['get']

    def get_list(self, request, **kwargs):
        id_ = request.GET.get('id')
        pwd = request.GET.get('pwd')
        datosarray = {}
        usuario = Usuario.objects.get(identificacion=id_)
        if usuario:
            if usuario.check_password(pwd):
                datosarray['id'] = usuario.pk
                datosarray['identificacion'] = id_
                datosarray['nombre'] = usuario.nombre

                return HttpResponse(json.dumps(datosarray) ,content_type='application/json', status=200)
        
        return HttpResponse(status=404)
    
class GetEvento(ModelResource):
    class Meta:
        queryset = Evento.objects.all()
        resource_name = 'getevento'
        allowed_methods = ['get']
        always_return_data = True
        fields = ['id', 'nombre']

class GetPlatillo(ModelResource):
    class Meta:
        queryset = Platillo.objects.all().order_by('id')
        resource_name = 'getplatillos'
        allowed_methods = ['get']
        always_return_data = True
        fields = ['id', 'nombre', 'precio']
        ordering = ['id']

class GetPlatilloJoven(ModelResource):
    class Meta:
        queryset = PlatilloJovene.objects.all().order_by('id')
        resource_name = 'getplatillojoven'
        allowed_methods = ['get']
        always_return_data = True
        fields = ['id', 'nombre']
        ordering = ['id']

class GetComplemento(ModelResource):
    class Meta:
        queryset = Complemento.objects.all()
        resource_name = 'getcomplemento'
        allowed_methods = ['get']
        always_return_data = True
        fields = ['id', 'nombre', 'precio']

class GetCostoFijo(ModelResource):
    class Meta:
        queryset = CostoFijo.objects.all()
        resource_name = 'getcostofijo'
        allowed_methods = ['get']
        always_return_data = True
        fields = ['id', 'nombre', 'precio', 'pk']
        ordering = ['id']

class GetDocumentoCotizacion(ModelResource):
    class Meta:
        queryset = DocumentoCotizacion.objects.all()
        resource_name = 'documentos'

class GetColaboradores(ModelResource):
    class Meta:
        queryset = Colaboradore.objects.filter(status=True)
        resource_name = 'getcolaboradores'
        allowed_methods = ['get']
        limit = 0
        always_return_data = True
        fields = ['id', 'nombre', 'status']
        filtering = {
            'id': ['exact'],
            'nombre': ['icontains', 'exact']
        }
        ordering = ['id']

class GetAgenda(ModelResource):
    class Meta:
        queryset = Cotizacion.objects.filter(status=1).order_by('fecha_evento')
        resource_name = 'getagenda'
        allowed_methods = ['get']
        limit = 0
        always_return_data = True
        fields = ['id', 'fecha_evento', 'hora_inicio', 'hora_fin', 'contrato', 'fecha_confirmacion']

    def apply_filters(self, request, applicable_filters):
        # Aplicar filtros estándar
        filtered = super(GetAgenda, self).apply_filters(request, applicable_filters)
        
        # Obtener parámetros de consulta personalizados adicionales
        desde_str = request.GET.get('desde', None)
        hasta_str = request.GET.get('hasta', None)
        desde, hasta = None, None
        if desde_str and hasta_str:
            desde = datetime.strptime(desde_str, '%Y-%m-%d')
            hasta = datetime.strptime(hasta_str, '%Y-%m-%d')
            hasta = hasta.replace(hour=23, minute=59, second=59)
        
        # Aplicar filtros personalizados adicionales si es necesario
        if desde and hasta:
            filtered = filtered.filter(fecha_evento__range=(desde, hasta))
        
        return filtered

    def dehydrate(self, bundle):
        # Configurar locale a español
        meses_es = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        # try:
        #     locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Linux/Mac
        # except:
        #     try:
        #         locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')  # Windows
        #     except:
        #         pass
        fecha = bundle.data['fecha_evento']
        mes_es = meses_es[fecha.month].capitalize()
        fecha_formateada = f"{mes_es} {fecha.day}, {fecha.year}"
        bundle.data['fecha_evento'] = fecha_formateada.upper()
        return bundle

class GetCotizacion(ModelResource):
    colaborador = fields.ForeignKey(GetColaboradores, 'colaborador', null=True, full=True)
    class Meta:
        queryset = Cotizacion.objects.filter(status=1, contrato=False).order_by('-id')
        resource_name = 'getcotizacion'
        allowed_methods = ['get']
        always_return_data = True
        limit = 0
        fields = ['id', 'folio', 'colaborador', 'created_at', 'fecha_expiracion', 'fecha_evento', 'status', 'telefono_novio', 'contrato', 'hora_inicio', 'hora_fin']
        filtering = {
            'id': ['exact'],
            'folio': ['icontains'],
            'telefono_novio': ['icontains'],
            'colaborador': ALL_WITH_RELATIONS
        }

    def build_filters(self, filters=None, ignore_bad_filters=False):
        if filters is None:
            filters = {}
        
        # Crear una copia de los filtros originales
        original_filters = filters.copy()
        
        # Procesar filtros personalizados
        colaborador_nombre = original_filters.pop('colaborador__nombre__icontains', None)
        
        # Ejecutar el método original para los filtros estándar
        orm_filters = super(GetCotizacion, self).build_filters(original_filters, ignore_bad_filters)
        
        # Aplicar filtro personalizado si se proporcionó
        if colaborador_nombre:
            # Obtener los IDs de colaboradores que coinciden con el nombre
            colaborador_ids = Colaboradore.objects.filter(nombre__icontains=colaborador_nombre).values_list('id', flat=True)
            
            # Añadir condición a los filtros ORM para filtrar por estos IDs
            if 'colaborador__in' not in orm_filters:
                orm_filters['colaborador__in'] = []
            
            orm_filters['colaborador__in'].extend(list(colaborador_ids))
        
        return orm_filters
    
    def apply_filters(self, request, applicable_filters):
        # Aplicar filtros estándar
        filtered = super(GetCotizacion, self).apply_filters(request, applicable_filters)
        
        # Obtener parámetros de consulta personalizados adicionales
        colaborador_nombre = request.GET.get('colaborador_nombre', None)
        
        # Aplicar filtros personalizados adicionales si es necesario
        if colaborador_nombre:
            filtered = filtered.filter(colaborador__nombre__icontains=colaborador_nombre)
        
        return filtered

    def dehydrate(self, bundle):
        bundle.data['url_cotizacion'] = ''
        bundle.data['url_contrato'] = ''        
        cotizacion = Cotizacion.objects.get(pk=bundle.data['id'])
        expiracion = cotizacion.fecha_expiracion - cotizacion.created_at
        documentos = cotizacion.documentos_cotizacion
        bundle.data['evento'] = cotizacion.evento.nombre
        bundle.data['expiracion'] = expiracion.days
        if documentos.exists():
            bundle.data['url_cotizacion'] = f"http://104.248.52.156/{documentos.first().url_cotizacion}"
            bundle.data['url_contrato'] = f"http://104.248.52.156/{documentos.first().url_contrato}"
        return bundle

class GetContrato(ModelResource):
    colaborador = fields.ForeignKey(GetColaboradores, 'colaborador', null=True, full=True)
    class Meta:
        queryset = Cotizacion.objects.filter(status=1, contrato=True).order_by('-id')
        resource_name = 'getcontratos'
        allowed_methods = ['get']
        always_return_data = True
        limit = 0
        fields = ['id', 'folio', 'colaborador', 'created_at', 'fecha_expiracion', 'fecha_evento', 'fecha_confirmacion', 'status', 'telefono_novio', 'contrato', 'hora_inicio', 'hora_fin']
        filtering = {
            'id': ['exact'],
            'folio': ['icontains'],
            'telefono_novio': ['icontains'],
            'colaborador': ALL_WITH_RELATIONS
        }

    def build_filters(self, filters=None, ignore_bad_filters=False):
        if filters is None:
            filters = {}
        
        # Crear una copia de los filtros originales
        original_filters = filters.copy()
        
        # Procesar filtros personalizados
        colaborador_nombre = original_filters.pop('colaborador__nombre__icontains', None)
        
        # Ejecutar el método original para los filtros estándar
        orm_filters = super(GetContrato, self).build_filters(original_filters, ignore_bad_filters)
        
        # Aplicar filtro personalizado si se proporcionó
        if colaborador_nombre:
            # Obtener los IDs de colaboradores que coinciden con el nombre
            colaborador_ids = Colaboradore.objects.filter(nombre__icontains=colaborador_nombre).values_list('id', flat=True)
            
            # Añadir condición a los filtros ORM para filtrar por estos IDs
            if 'colaborador__in' not in orm_filters:
                orm_filters['colaborador__in'] = []
            
            orm_filters['colaborador__in'].extend(list(colaborador_ids))
        
        return orm_filters
    
    def apply_filters(self, request, applicable_filters):
        # Aplicar filtros estándar
        filtered = super(GetContrato, self).apply_filters(request, applicable_filters)
        
        # Obtener parámetros de consulta personalizados adicionales
        colaborador_nombre = request.GET.get('colaborador_nombre', None)
        desde_str = request.GET.get('desde', None)
        hasta_str = request.GET.get('hasta', None)
        desde, hasta = None, None
        if desde_str and hasta_str:
            desde = datetime.strptime(desde_str, '%Y-%m-%d')
            hasta = datetime.strptime(hasta_str, '%Y-%m-%d')
            hasta = hasta.replace(hour=23, minute=59, second=59)
        
        
        # Aplicar filtros personalizados adicionales si es necesario
        if colaborador_nombre:
            filtered = filtered.filter(colaborador__nombre__icontains=colaborador_nombre, contrato=True, status=1)

        if desde and hasta:
            filtered = filtered.filter(fecha_evento__range=(desde, hasta), contrato=True, status=1)
        
        return filtered

    def dehydrate(self, bundle):
        bundle.data['url_cotizacion'] = ''
        bundle.data['url_contrato'] = ''        
        cotizacion = Cotizacion.objects.get(pk=bundle.data['id'])
        expiracion = cotizacion.fecha_expiracion - cotizacion.created_at
        documentos = cotizacion.documentos_cotizacion
        bundle.data['evento'] = cotizacion.evento.nombre
        bundle.data['expiracion'] = expiracion.days
        if documentos.exists():
            bundle.data['url_cotizacion'] = f"http://104.248.52.156/{documentos.first().url_cotizacion}"
            bundle.data['url_contrato'] = f"http://104.248.52.156/{documentos.first().url_contrato}"
        return bundle

class CrearEvento(ModelResource):
    class Meta:
        queryset = Evento.objects.all()
        limit = 1
        resource_name = 'crearevento'
        allowed_methods = ['post']

    def post_list(self, request, **kwargs):
        data = json.loads(request.body)
        evento = Evento()
        evento.nombre = data['nombre']
        evento.save()

        return HttpResponse(content_type='application/json', status=201)
    
class CrearPlatillo(ModelResource):
    class Meta:
        queryset = Platillo.objects.all()
        limit = 1
        resource_name = 'crearplatillo'
        allowed_methods = ['post']

    def post_list(self, request, **kwargs):
        data = json.loads(request.body)
        evento = Platillo()
        evento.nombre = data['nombre']
        evento.precio = data['precio']
        evento.save()

        return HttpResponse(content_type='application/json', status=201)
    
class CrearPlatilloJoven(ModelResource):
    class Meta:
        queryset = PlatilloJovene.objects.all()
        limit = 1
        resource_name = 'crearplatillojoven'
        allowed_methods = ['post']

    def post_list(self, request, **kwargs):
        data = json.loads(request.body)
        evento = PlatilloJovene()
        evento.nombre = data['nombre']
        evento.save()

        return HttpResponse(content_type='application/json', status=201)
    
class CrearCostoFijo(ModelResource):
    class Meta:
        queryset = CostoFijo.objects.all()
        limit = 1
        resource_name = 'crearcostofijo'
        allowed_methods = ['post']

    def post_list(self, request, **kwargs):
        data = json.loads(request.body)
        evento = CostoFijo()
        evento.nombre = data['nombre']
        evento.precio = data['precio']
        evento.save()

        return HttpResponse(content_type='application/json', status=201)

class CrearComplemento(ModelResource):
    class Meta:
        queryset = Complemento.objects.all()
        limit = 1
        resource_name = 'crearcomplemento'
        allowed_methods = ['post']

    def post_list(self, request, **kwargs):
        data = json.loads(request.body)
        evento = Complemento()
        evento.nombre = data['nombre']
        evento.precio = data['precio']
        evento.save()

        return HttpResponse(content_type='application/json', status=201)

class GenerarContrato(ModelResource):
    class Meta:
        queryset = Cotizacion.objects.all()
        limit = 1
        resource_name = 'generarcontrato'
        allowed_methods = ['post']

    def post_list(self, request, **kwargs):
        data = json.loads(request.body)
        id_cotizacion = data['id_cotizacion']
        cotizacion = Cotizacion.objects.get(id=id_cotizacion)
        cotizacion.contrato = True
        cotizacion.fecha_confirmacion = datetime.now()
        cotizacion.save()

        # Generar PDF contrato
        doc = generar_contrato_pdf(cotizacion)

        return HttpResponse(json.dumps({
            'folio': cotizacion.folio,
            'contrato_url': request.build_absolute_uri(settings.MEDIA_URL + doc.url_contrato)
        }), content_type='application/json', status=201)
        

class CrearCotizacion(ModelResource):
    class Meta:
        queryset = Cotizacion.objects.all()
        limit = 1
        resource_name = 'crearcotizacion'
        allowed_methods = ['post']

    def post_list(self, request, **kwargs):
        data = json.loads(request.body)
        telefono = data['telefono_novio']
        dataarray = {}
        if Cotizacion.objects.filter(telefono_novio=telefono).exists():
            cotizacion = Cotizacion.objects.get(telefono_novio=telefono)            
            return HttpResponse(json.dumps({
                'folio': cotizacion.folio,
                'exists': True,
                'cotizacion': request.build_absolute_uri(settings.MEDIA_URL + cotizacion.documentos_cotizacion.get().url_cotizacion)
            }) ,content_type='application/json', status=200) 
        
        fecha_evento_str  = data['fecha_evento']
        fecha_evento = datetime.strptime(fecha_evento_str, '%Y-%m-%d')
        hora_inicio_str =  data['hora_inicio']
        hora_fin_str = data['hora_fin']
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()

        cotizacion = Cotizacion()
        cotizacion.nombre_novio = data['nombre_novio']
        cotizacion.nombre_novia = data['nombre_novia']
        cotizacion.telefono_novio = data['telefono_novio']
        cotizacion.telefono_novia = data['telefono_novia']
        cotizacion.correo_electronico = data['correo']
        cotizacion.fecha_evento = fecha_evento
        cotizacion.hora_inicio = hora_inicio
        cotizacion.hora_fin = hora_fin
        cotizacion.evento = Evento.objects.get(Q(nombre__iexact=data['id_evento']))
        cotizacion.platillo = Platillo.objects.get(Q(nombre__iexact=data['id_platillo']))
        if data['id_evento'] == "XV Años": # XV Anos
            cotizacion.platillo_jovenes = PlatilloJovene.objects.get(Q(nombre__iexact=data['id_platillo_joven']))
            cotizacion.numero_jovenes = data['personas_jovenes']
        if 'adicional' in data:
            cotizacion.adicional = Complemento.objects.get(Q(nombre__iexact=data['adicional']))
        cotizacion.numero_personas = data['personas']
        cotizacion.colaborador = Colaboradore.objects.get(Q(nombre__iexact=data['colaborador']))
        cotizacion.creada_por = Usuario.objects.get(id=data['usuario'])        
        cotizacion.save()
        cotizacion_instance = Cotizacion.objects.get(id=cotizacion.id)
        cotizacion_instance.fecha_expiracion = cotizacion_instance.created_at + timedelta(days=15)
        cotizacion_instance.folio = f"{cotizacion.creada_por.identificacion}-COT{cotizacion.id:05d}"
        cotizacion_instance.save()

        #Detalle
        personas = cotizacion_instance.numero_personas
        jovenes =  cotizacion_instance.numero_jovenes if cotizacion_instance.numero_jovenes else 0
        bebida = Complemento.objects.get(nombre="Bebidas").precio
        meseros = Complemento.objects.get(nombre="Meseros").precio
        uso_jardon = Complemento.objects.get(nombre="Uso Jardin").precio
        costo_fijo = 0
        total_personas = 0
        if cotizacion_instance.evento.pk == 3: # XV Anos
            total_personas = (personas + jovenes)
        else:
            total_personas = personas
        npc, npp, npb, npm, npj, npjp = 0, 0, 0 ,0, 0, 0
        if total_personas <= 200:
            npp = CostoFijo.objects.get(nombre="0 a 200").precio + cotizacion_instance.platillo.precio
        elif total_personas >= 201 and total_personas <= 300:
            npp = CostoFijo.objects.get(nombre="201 a 300").precio + cotizacion_instance.platillo.precio
        else:
            npp = CostoFijo.objects.get(nombre="301 a 399").precio + cotizacion_instance.platillo.precio
        #npp = personas * cotizacion_instance.platillo.precio
        if cotizacion_instance.evento.pk == 3: # XV Anos
            precio_jovenes = Platillo.objects.get(id=8).precio
            if jovenes <= 200:
                npjp = CostoFijo.objects.get(nombre="0 a 200").precio + precio_jovenes
            elif jovenes >= 201 and total_personas <= 300:
                npjp = CostoFijo.objects.get(nombre="201 a 300").precio + precio_jovenes
            else:
                npjp = CostoFijo.objects.get(nombre="301 a 399").precio + precio_jovenes
        #npb = personas * bebida
        #npm = personas * meseros
        #npj = personas * uso_jardon
        #if 'adicional' in data:            
        #    npc = personas * cotizacion_instance.adicional.precio

        detalle = DetalleCotizacion()
        detalle.cotizacion = cotizacion_instance
        detalle.npp = npp # Costo por persona
        detalle.npb = npb
        detalle.npm = npm
        detalle.npj = npjp # Costo por joven
        detalle.npc = npc

        # costo_fijo += CostoFijo.objects.get(nombre="Permiso de alcoholes").precio
        # costo_fijo += CostoFijo.objects.get(nombre="Personal de limpieza de banos").precio
        # costo_fijo += CostoFijo.objects.get(nombre="Personal de limpieza de cocina").precio
        # costo_fijo += CostoFijo.objects.get(nombre="Hostess").precio
        # costo_fijo += CostoFijo.objects.get(nombre="Personal de mantenimiento").precio

        
        # if total_personas >= 200:
        #     costo_fijo += CostoFijo.objects.get(nombre="Permisos (200 - 499 personas)").precio

        # if total_personas >= 30 and total_personas <= 199:
        #     costo_fijo += CostoFijo.objects.get(nombre="Guardias de seguridad (30 - 199 personas)").precio
        # elif total_personas >= 200 and total_personas <= 299:
        #     costo_fijo += CostoFijo.objects.get(nombre="Guardias de seguridad (200 - 299 personas)").precio
        # else:
        #     costo_fijo += CostoFijo.objects.get(nombre="Guardias de seguridad (300 - 499 personas)").precio

        # if cotizacion_instance.evento.pk == 3:
        #     detalle.total = (costo_fijo + npp + npjp)  #(costo_fijo + npp + npb + npm + npj + npc)
        # else:
        #     detalle.total = (costo_fijo + npp)  #(costo_fijo + npp + npb + npm + npj + npc)
        detalle.total = npp * total_personas
        if cotizacion_instance.evento.pk == 3:
            detalle.total = (npp * cotizacion_instance.numero_personas) + (npj * cotizacion_instance.numero_jovenes)
        detalle.save()

        doc = generar_pdf_cotizacion(cotizacion_instance, detalle.total)

        return HttpResponse(json.dumps({
            'folio': cotizacion_instance.folio,
            'documento_url': request.build_absolute_uri(settings.MEDIA_URL + doc.url_cotizacion)
        }), content_type='application/json', status=201)
    

def generar_contrato_pdf(cotizacion_instance):
    # Configurar locale a español
    # try:
    #     locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Linux/Mac
    # except:
    #     try:
    #         locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')  # Windows
    #     except:
    #         pass
    meses_es = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    fecha_evento = cotizacion_instance.fecha_evento
    fecha_creacion = cotizacion_instance.created_at
    fecha_formateada = f"{fecha_evento.day} de {meses_es[fecha_evento.month].capitalize()} del {fecha_evento.year}" #cotizacion_instance.fecha_evento.strftime("%d de %B del %Y")
    fecha_creada = f"{fecha_creacion.day} de {meses_es[fecha_creacion.month].capitalize()} del {fecha_creacion.year}" #cotizacion_instance.created_at.strftime("%d de %B del %Y")
    pdfmetrics.registerFont(TTFont('Aleo', f'{settings.MEDIA_ROOT}Aleo-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('AleoLight', f'{settings.MEDIA_ROOT}Aleo-Thin.ttf'))
    pdfmetrics.registerFont(TTFont('Roboto', f'{settings.MEDIA_ROOT}Roboto_Condensed-Regular.ttf'))
    pdf_filename = f"contrato_{cotizacion_instance.id}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'cotizaciones', pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'contrato_base.pdf')
    # Crear un PDF en memoria con la información dinámica
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont("Roboto", 12)
    c.drawString(85, 568, f"{cotizacion_instance.nombre_novio}")
    c.drawString(85, 333, f"{cotizacion_instance.nombre_novio}")
    c.drawString(310, 319, f"{cotizacion_instance.evento.nombre}")
    c.drawString(85, 144, f"{cotizacion_instance.evento.nombre}")
    c.drawString(325, 144, f"{fecha_formateada}")
    # c.drawString(185, 532, f"{cotizacion_instance.evento.nombre}")
    # c.drawString(132, 517, f"{fecha_formateada}")
    # c.drawString(225, 502, f"{cotizacion_instance.numero_personas}")
    # c.drawString(192, 488, f"{cotizacion_instance.platillo.nombre}")
    # if cotizacion_instance.platillo_jovenes:
    #     c.drawString(192, 474, f"{cotizacion_instance.platillo_jovenes.nombre}")
    # else:
    #     c.drawString(192, 474, f"Sin platillo")
    # c.drawString(148, 459, f"{cotizacion_instance.hora_inicio} a {cotizacion_instance.hora_fin}")
    # c.drawString(278, 444, "${:,.2f} MXN".format(cotizacion_instance.detalle_cotizacion.get().npp))
    # c.drawString(258, 428, "${:,.2f} MXN".format(cotizacion_instance.detalle_cotizacion.get().npj))
    c.showPage()
    c.drawString(218, 550, f"{cotizacion_instance.evento.nombre}")    
    c.drawString(385, 550, f"{fecha_formateada}")
    c.showPage()    
    if cotizacion_instance.evento.pk == 3:
        c.drawString(201, 212, f"{cotizacion_instance.numero_personas+cotizacion_instance.numero_jovenes}")
    else:
        c.drawString(201, 212, f"{cotizacion_instance.numero_personas}")
    c.showPage()
    c.showPage()
    c.drawString(335, 285, f"{cotizacion_instance.nombre_novio}")
    c.showPage()    
    c.showPage()
    c.drawString(85, 355, f"{cotizacion_instance.nombre_novio}")
    c.showPage()    
    #c.drawString(157, 445, f"{fecha_creada}")
    #c.drawString(325, 315, f"{cotizacion_instance.nombre_novio}")
    c.save()
    # Mover al inicio del BytesIO
    packet.seek(0)
    # Abrir la plantilla de PDF existente
    existing_pdf = PdfReader(pdf_template_path)
    output = PdfWriter()

    # Añadir el contenido de la plantilla
    page = existing_pdf.pages[0] # 1

    # Obtener el contenido que acabamos de crear
    new_pdf = PdfReader(packet)

    # Fusionar los PDFs
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    # Si la plantilla tiene más páginas, añadirlas
    for i in range(1, len(existing_pdf.pages)):
        page = existing_pdf.pages[i]
        if i == 0:
            page.merge_page(new_pdf.pages[0])
        if i == 1:
            page.merge_page(new_pdf.pages[1])
        if i == 2:
            page.merge_page(new_pdf.pages[2])
        if i == 3:
            page.merge_page(new_pdf.pages[3])
        if i == 4:
            page.merge_page(new_pdf.pages[4])
        if i == 6:
            page.merge_page(new_pdf.pages[6])
        output.add_page(existing_pdf.pages[i])

    # Guardar el PDF final
    with open(pdf_path, "wb") as output_stream:
        output.write(output_stream)

    doc = DocumentoCotizacion.objects.get(
        cotizacion=cotizacion_instance,        
    )
    doc.url_contrato = f'cotizaciones/{pdf_filename}'
    doc.save()

    return doc

# Generar PDF para cotizacion
def generar_pdf_cotizacion(cotizacion_instance, total):  
    meses_es = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }  
    pdfmetrics.registerFont(TTFont('Aleo', f'{settings.MEDIA_ROOT}Aleo-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('AleoLight', f'{settings.MEDIA_ROOT}Aleo-Thin.ttf'))
    pdfmetrics.registerFont(TTFont('Roboto', f'{settings.MEDIA_ROOT}Roboto_Condensed-Regular.ttf'))
    # Suponiendo que cotizacion_instance.fecha_evento es un objeto datetime
    fecha_evento = cotizacion_instance.fecha_evento
    fecha_creacion = cotizacion_instance.created_at
    fecha_formateada = f"{fecha_evento.day} de {meses_es[fecha_evento.month].capitalize()} del {fecha_evento.year}" #cotizacion_instance.fecha_evento.strftime("%d de %B del %Y")
    fecha_formateada_creacion = f"{fecha_creacion.day} de {meses_es[fecha_creacion.month].capitalize()} del {fecha_creacion.year}" #cotizacion_instance.created_at.strftime("%d de %B del %Y")
    # Formatear el total como moneda mexicana
    total_formateado = "${:,.2f} MXN".format(total)
    pdf_filename = f"cotizacion_{cotizacion_instance.id}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'cotizaciones', pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    # Ruta al PDF base (plantilla)
    if cotizacion_instance.platillo.pk == 1 or cotizacion_instance.platillo.pk == 9: # Pollo
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_pollo_base.pdf')
    elif cotizacion_instance.platillo.pk == 2 or cotizacion_instance.platillo.pk == 10: # Puerco
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_cerdo_base.pdf')
    elif cotizacion_instance.platillo.pk == 3: # Italiano
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_italiano_base.pdf')
    elif cotizacion_instance.platillo.pk == 4: # Mixto
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_mixto_base.pdf')
    elif cotizacion_instance.platillo.pk == 5 or cotizacion_instance.platillo.pk == 13: # Premium
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_premium_base.pdf')
    elif cotizacion_instance.platillo.pk == 6: # Parrillada
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_parrillada_base.pdf')
    else: # Guiso
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_guisos_base.pdf')        
    # Crear un PDF en memoria con la información dinámica
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    if cotizacion_instance.platillo.pk == 1 or cotizacion_instance.platillo.pk == 9:
        c.setFont("AleoLight", 32)
        c.drawCentredString(305, 230, f"{cotizacion_instance.evento.nombre.upper()}")
        c.setFont("Aleo", 16)
        c.drawCentredString(310, 200, f"{cotizacion_instance.nombre_novio}")
        c.drawCentredString(310, 170, f"{fecha_formateada}")
        #if cotizacion_instance.evento.pk == 3: #XV Anos
        #    c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas + cotizacion_instance.numero_jovenes} invitados {total_formateado}")
        #else:
        #    c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas} invitados {total_formateado}")
        c.showPage()        
        c.showPage()        
        if cotizacion_instance.numero_personas <= 200:
            precio_por_persona_pollo = CostoFijo.objects.get(nombre="0 a 200").precio + Platillo.objects.get(nombre="Pollo").precio
            precio_por_persona_puerco = CostoFijo.objects.get(nombre="0 a 200").precio + Platillo.objects.get(nombre="Puerco").precio
            precio_por_persona_res = CostoFijo.objects.get(nombre="0 a 200").precio + Platillo.objects.get(nombre="Premium").precio
        elif cotizacion_instance.numero_personas >= 201 and cotizacion_instance.numero_personas <= 300:
            precio_por_persona_pollo = CostoFijo.objects.get(nombre="201 a 300").precio + Platillo.objects.get(nombre="Pollo").precio
            precio_por_persona_puerco = CostoFijo.objects.get(nombre="201 a 300").precio + Platillo.objects.get(nombre="Puerco").precio
            precio_por_persona_res = CostoFijo.objects.get(nombre="201 a 300").precio + Platillo.objects.get(nombre="Premium").precio
        else:
            precio_por_persona_pollo = CostoFijo.objects.get(nombre="301 a 399").precio + Platillo.objects.get(nombre="Pollo").precio
            precio_por_persona_puerco = CostoFijo.objects.get(nombre="301 a 399").precio + Platillo.objects.get(nombre="Puerco").precio
            precio_por_persona_res = CostoFijo.objects.get(nombre="301 a 399").precio + Platillo.objects.get(nombre="Premium").precio

        c.drawString(276, 640, "${:,.2f}".format(precio_por_persona_pollo)) 
        c.drawString(355, 640, "${:,.2f}".format(precio_por_persona_puerco))
        c.drawString(430, 640, "${:,.2f}".format(precio_por_persona_res))
        c.setFont("Aleo", 10)
        c.drawString(118, 605, f"PRECIO POR {cotizacion_instance.numero_personas} INVITADOS")
        c.drawString(276, 605, "${:,.2f}".format(precio_por_persona_pollo * cotizacion_instance.numero_personas)) 
        c.drawString(355, 605, "${:,.2f}".format(precio_por_persona_puerco * cotizacion_instance.numero_personas))
        c.drawString(430, 605, "${:,.2f}".format(precio_por_persona_res * cotizacion_instance.numero_personas))
        c.showPage()
        c.showPage()
        c.showPage()
        c.setFont("Roboto", 13)
        c.drawString(110, 365, f"{cotizacion_instance.colaborador.nombre}")
        c.setFont("Roboto", 11)
        c.drawString(340, 198, f"Cotización realizada el día {fecha_formateada_creacion}")
        c.showPage()
    elif cotizacion_instance.platillo.pk == 2 or cotizacion_instance.platillo.pk == 10:
        c.setFont("AleoLight", 32)
        c.drawCentredString(305, 230, f"{cotizacion_instance.evento.nombre.upper()}")
        c.setFont("Aleo", 16)
        c.drawCentredString(310, 200, f"{cotizacion_instance.nombre_novio}")
        c.drawCentredString(310, 170, f"{fecha_formateada}")
        # if cotizacion_instance.evento.pk == 3: #XV Anos
        #     c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas + cotizacion_instance.numero_jovenes} invitados {total_formateado}")
        # else:
        #     c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas} invitados {total_formateado}")
        c.showPage()
        c.showPage()
        if cotizacion_instance.numero_personas <= 200:
            precio_por_persona_pollo = CostoFijo.objects.get(nombre="0 a 200").precio + Platillo.objects.get(nombre="Pollo").precio
            precio_por_persona_puerco = CostoFijo.objects.get(nombre="0 a 200").precio + Platillo.objects.get(nombre="Puerco").precio
            precio_por_persona_res = CostoFijo.objects.get(nombre="0 a 200").precio + Platillo.objects.get(nombre="Premium").precio
        elif cotizacion_instance.numero_personas >= 201 and cotizacion_instance.numero_personas <= 300:
            precio_por_persona_pollo = CostoFijo.objects.get(nombre="201 a 300").precio + Platillo.objects.get(nombre="Pollo").precio
            precio_por_persona_puerco = CostoFijo.objects.get(nombre="201 a 300").precio + Platillo.objects.get(nombre="Puerco").precio
            precio_por_persona_res = CostoFijo.objects.get(nombre="201 a 300").precio + Platillo.objects.get(nombre="Premium").precio
        else:
            precio_por_persona_pollo = CostoFijo.objects.get(nombre="301 a 399").precio + Platillo.objects.get(nombre="Pollo").precio
            precio_por_persona_puerco = CostoFijo.objects.get(nombre="301 a 399").precio + Platillo.objects.get(nombre="Puerco").precio
            precio_por_persona_res = CostoFijo.objects.get(nombre="301 a 399").precio + Platillo.objects.get(nombre="Premium").precio

        c.drawString(276, 640, "${:,.2f}".format(precio_por_persona_pollo)) 
        c.drawString(355, 640, "${:,.2f}".format(precio_por_persona_puerco))
        c.drawString(430, 640, "${:,.2f}".format(precio_por_persona_res))
        c.setFont("Aleo", 10)
        c.drawString(118, 605, f"PRECIO POR {cotizacion_instance.numero_personas} INVITADOS")
        c.drawString(276, 605, "${:,.2f}".format(precio_por_persona_pollo * cotizacion_instance.numero_personas)) 
        c.drawString(355, 605, "${:,.2f}".format(precio_por_persona_puerco * cotizacion_instance.numero_personas))
        c.drawString(430, 605, "${:,.2f}".format(precio_por_persona_res * cotizacion_instance.numero_personas))
        c.showPage()
        c.showPage()
        c.setFont("Roboto", 13) #13
        c.drawString(110, 365, f"{cotizacion_instance.colaborador.nombre}") #110 , 320
        c.setFont("Roboto", 11)
        c.drawString(340, 198, f"Cotización realizada el día {fecha_formateada_creacion}")
        c.showPage()
    elif cotizacion_instance.platillo.pk == 3:
        c.setFont("AleoLight", 32)
        c.drawCentredString(305, 230, f"{cotizacion_instance.evento.nombre.upper()}")
        c.setFont("Aleo", 16)
        c.drawCentredString(310, 200, f"{cotizacion_instance.nombre_novio}")
        c.drawCentredString(310, 170, f"{fecha_formateada}")
        if cotizacion_instance.evento.pk == 3: #XV Anos
            c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas + cotizacion_instance.numero_jovenes} invitados {total_formateado}")
        else:
            c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas} invitados {total_formateado}")
        c.showPage()
        c.showPage()
        c.showPage()
        c.showPage()
        c.setFont("Roboto", 13)
        c.drawString(110, 365, f"{cotizacion_instance.colaborador.nombre}")        
        c.setFont("Roboto", 11)
        c.drawString(340, 198, f"Cotización realizada el día {fecha_formateada_creacion}")
        c.showPage()
    elif cotizacion_instance.platillo.pk == 4:
        c.setFont("AleoLight", 32)
        c.drawCentredString(305, 230, f"{cotizacion_instance.evento.nombre.upper()}")
        c.setFont("Aleo", 16)
        c.drawCentredString(310, 200, f"{cotizacion_instance.nombre_novio}")
        c.drawCentredString(310, 170, f"{fecha_formateada}")
        if cotizacion_instance.evento.pk == 3: #XV Anos
            c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas + cotizacion_instance.numero_jovenes} invitados {total_formateado}")
        else:
            c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas} invitados {total_formateado}")
        c.showPage()
        c.showPage()
        c.showPage()
        c.showPage()
        c.setFont("Roboto", 13)
        c.drawString(110, 365, f"{cotizacion_instance.colaborador.nombre}")        
        c.setFont("Roboto", 11)
        c.drawString(340, 198, f"Cotización realizada el día {fecha_formateada_creacion}")
        c.showPage()
    elif cotizacion_instance.platillo.pk == 5 or cotizacion_instance.platillo.pk == 13:
        c.setFont("AleoLight", 32)
        c.drawCentredString(305, 230, f"{cotizacion_instance.evento.nombre.upper()}")
        c.setFont("Aleo", 16)
        c.drawCentredString(310, 200, f"{cotizacion_instance.nombre_novio}")
        c.drawCentredString(310, 170, f"{fecha_formateada}")
        # if cotizacion_instance.evento.pk == 3: #XV Anos
        #     c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas + cotizacion_instance.numero_jovenes} invitados {total_formateado}")
        # else:
        #     c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas} invitados {total_formateado}")
        c.showPage()
        c.showPage()
        if cotizacion_instance.numero_personas <= 200:
            precio_por_persona_pollo = CostoFijo.objects.get(nombre="0 a 200").precio + Platillo.objects.get(nombre="Pollo").precio
            precio_por_persona_puerco = CostoFijo.objects.get(nombre="0 a 200").precio + Platillo.objects.get(nombre="Puerco").precio
            precio_por_persona_res = CostoFijo.objects.get(nombre="0 a 200").precio + Platillo.objects.get(nombre="Premium").precio
        elif cotizacion_instance.numero_personas >= 201 and cotizacion_instance.numero_personas <= 300:
            precio_por_persona_pollo = CostoFijo.objects.get(nombre="201 a 300").precio + Platillo.objects.get(nombre="Pollo").precio
            precio_por_persona_puerco = CostoFijo.objects.get(nombre="201 a 300").precio + Platillo.objects.get(nombre="Puerco").precio
            precio_por_persona_res = CostoFijo.objects.get(nombre="201 a 300").precio + Platillo.objects.get(nombre="Premium").precio
        else:
            precio_por_persona_pollo = CostoFijo.objects.get(nombre="301 a 399").precio + Platillo.objects.get(nombre="Pollo").precio
            precio_por_persona_puerco = CostoFijo.objects.get(nombre="301 a 399").precio + Platillo.objects.get(nombre="Puerco").precio
            precio_por_persona_res = CostoFijo.objects.get(nombre="301 a 399").precio + Platillo.objects.get(nombre="Premium").precio

        c.drawString(276, 640, "${:,.2f}".format(precio_por_persona_pollo)) 
        c.drawString(355, 640, "${:,.2f}".format(precio_por_persona_puerco))
        c.drawString(430, 640, "${:,.2f}".format(precio_por_persona_res))
        c.setFont("Aleo", 10)
        c.drawString(118, 605, f"PRECIO POR {cotizacion_instance.numero_personas} INVITADOS")
        c.drawString(276, 605, "${:,.2f}".format(precio_por_persona_pollo * cotizacion_instance.numero_personas)) 
        c.drawString(355, 605, "${:,.2f}".format(precio_por_persona_puerco * cotizacion_instance.numero_personas))
        c.drawString(430, 605, "${:,.2f}".format(precio_por_persona_res * cotizacion_instance.numero_personas))
        c.showPage()
        c.showPage()
        c.setFont("Roboto", 13)
        c.drawString(110, 365, f"{cotizacion_instance.colaborador.nombre}")        
        c.setFont("Roboto", 11)
        c.drawString(340, 198, f"Cotización realizada el día {fecha_formateada_creacion}")
        c.showPage()
    elif cotizacion_instance.platillo.pk == 6:
        c.setFont("AleoLight", 32)
        c.drawCentredString(305, 230, f"{cotizacion_instance.evento.nombre.upper()}")
        c.setFont("Aleo", 16)
        c.drawCentredString(310, 200, f"{cotizacion_instance.nombre_novio}")
        c.drawCentredString(310, 170, f"{fecha_formateada}")
        if cotizacion_instance.evento.pk == 3: #XV Anos
            c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas + cotizacion_instance.numero_jovenes} invitados {total_formateado}")
        else:
            c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas} invitados {total_formateado}")
        c.showPage()
        c.showPage()
        c.showPage()
        c.showPage()
        c.setFont("Roboto", 13)
        c.drawString(110, 365, f"{cotizacion_instance.colaborador.nombre}")        
        c.setFont("Roboto", 11)
        c.drawString(340, 198, f"Cotización realizada el día {fecha_formateada_creacion}")
        c.showPage()
    else:
        c.setFont("AleoLight", 32)
        c.drawCentredString(305, 230, f"{cotizacion_instance.evento.nombre.upper()}")
        c.setFont("Aleo", 16)
        c.drawCentredString(310, 200, f"{cotizacion_instance.nombre_novio}")
        c.drawCentredString(310, 170, f"{fecha_formateada}")
        if cotizacion_instance.evento.pk == 3: #XV Anos
            c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas + cotizacion_instance.numero_jovenes} invitados {total_formateado}")
        else:
            c.drawCentredString(310, 140, f"Costo por {cotizacion_instance.numero_personas} invitados {total_formateado}")
        c.showPage()
        c.showPage()
        c.showPage()
        c.showPage()
        c.setFont("Roboto", 13)
        c.drawString(110, 365, f"{cotizacion_instance.colaborador.nombre}")        
        c.setFont("Roboto", 11)
        c.drawString(340, 198, f"Cotización realizada el día {fecha_formateada_creacion}")
        c.showPage()
    c.save()
    # Mover al inicio del BytesIO
    packet.seek(0)
    # Abrir la plantilla de PDF existente
    existing_pdf = PdfReader(pdf_template_path)
    output = PdfWriter()

    # Añadir el contenido de la plantilla
    page = existing_pdf.pages[0] # 1

    # Obtener el contenido que acabamos de crear
    new_pdf = PdfReader(packet)

    # Fusionar los PDFs
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    # Si la plantilla tiene más páginas, añadirlas
    for i in range(1, len(existing_pdf.pages)):
        page = existing_pdf.pages[i]
        if i == 0:
            page.merge_page(new_pdf.pages[0])
        if i == 2:
            page.merge_page(new_pdf.pages[2])
        if i == 4:
            page.merge_page(new_pdf.pages[4])
        if i == 5:
            page.merge_page(new_pdf.pages[5])
        output.add_page(existing_pdf.pages[i])

    # Guardar el PDF final
    with open(pdf_path, "wb") as output_stream:
        output.write(output_stream)

    doc = DocumentoCotizacion.objects.create(
        cotizacion=cotizacion_instance,
        url_cotizacion=f'cotizaciones/{pdf_filename}'
    )

    return doc
    
class CancelarCotizacion(ModelResource):
    class Meta:
        queryset = Cotizacion.objects.all()
        resource_name = 'cancelarcotizacion'
        allowed_methods = ['delete']

    def obj_get(self, bundle, **kwargs):
        try:
            return Cotizacion.objects.get(pk=kwargs['pk'])
        except Cotizacion.DoesNotExist:
            raise HttpNotFound("Cotizacion no encontrada")
        
    def obj_delete(self, bundle, **kwargs):
        cotizacion = self.obj_get(bundle, **kwargs)
        cotizacion.status = 2
        cotizacion.fecha_cancelacion = datetime.now()
        cotizacion.save()

