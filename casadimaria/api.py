# -*- encoding: utf-8 -*-
from __future__ import division
from datetime import datetime, timedelta
import os
import pdb
from django.conf import settings
from django.utils.crypto import get_random_string
from tastypie.resources import ModelResource,ALL, ALL_WITH_RELATIONS, Resource
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
        usuario.save()

        return HttpResponse(content_type='application/json', status=201)
    
class Login(ModelResource):
    class Meta:
        queryset = Usuario.objects.all()
        limit = 1
        resource_name = 'login'
        allowed_methods = ['get']

    def get_list(self, request, **kwargs):
        id_ = request.GET.get('id')
        #pwd = request.GET.get('pwd')
        datosarray = {}
        usuario = Usuario.objects.get(identificacion=id_)
        if usuario:
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
        queryset = Platillo.objects.all()
        resource_name = 'getplatillos'
        allowed_methods = ['get']
        always_return_data = True
        fields = ['id', 'nombre', 'precio']

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
        fields = ['id', 'nombre', 'precio']

class GetColaboradores(ModelResource):
    class Meta:
        queryset = Colaboradore.objects.filter(status=True)
        resource_name = 'getcolaboradores'
        allowed_methods = ['get']
        always_return_data = True
        fields = ['id', 'nombre']

class GetCotizacion(ModelResource):
    class Meta:
        queryset = Cotizacion.objects.all()
        resource_name = 'getcotizacion'
        allowed_methods = ['get']
        always_return_data = True
        limit = 0
        filtering = {
            'id': ['exact'],
            'folio': ['icontains'],
            'colaborador': ['icontains']
        }

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
        cotizacion.evento = Evento.objects.get(id=data['id_evento'])
        cotizacion.platillo = Platillo.objects.get(id=data['id_platillo'])
        if data['id_evento'] == "3": # XV Anos
            cotizacion.platillo_jovenes = PlatilloJovene.objects.get(id=data['id_platillo_joven'])
            cotizacion.numero_jovenes = data['personas_jovenes']
        if 'adicional' in data:
            cotizacion.adicional = Complemento.objects.get(id=data['adicional'])
        cotizacion.numero_personas = data['personas']
        cotizacion.colaborador = Colaboradore.objects.get(id=data['colaborador'])
        cotizacion.creada_por = Usuario.objects.get(id=data['usuario'])
        cotizacion.fecha_expiracion = fecha_evento + timedelta(days=15)
        cotizacion.save()
        cotizacion_instance = Cotizacion.objects.get(id=cotizacion.id)
        cotizacion_instance.folio = "COT%04d" % cotizacion.id
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
    fecha_formateada = cotizacion_instance.fecha_evento.strftime("%d de %B del %Y")
    fecha_creada = cotizacion_instance.created_at.strftime("%d de %B del %Y")
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
    c.drawString(360, 628, f"{cotizacion_instance.nombre_novio}")
    c.drawString(185, 532, f"{cotizacion_instance.evento.nombre}")
    c.drawString(132, 517, f"{fecha_formateada}")
    c.drawString(225, 502, f"{cotizacion_instance.numero_personas}")
    c.drawString(192, 488, f"{cotizacion_instance.platillo.nombre}")
    if cotizacion_instance.platillo_jovenes:
        c.drawString(192, 474, f"{cotizacion_instance.platillo_jovenes.nombre}")
    else:
        c.drawString(192, 474, f"Sin platillo")
    c.drawString(148, 459, f"{cotizacion_instance.hora_inicio} a {cotizacion_instance.hora_fin}")
    c.drawString(278, 444, "${:,.2f} MXN".format(cotizacion_instance.detalle_cotizacion.get().npp))
    c.drawString(258, 428, "${:,.2f} MXN".format(cotizacion_instance.detalle_cotizacion.get().npj))
    c.showPage()
    c.showPage()
    c.showPage()
    c.drawString(157, 445, f"{fecha_creada}")
    c.drawString(325, 315, f"{cotizacion_instance.nombre_novio}")
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
        if i == 3:
            page.merge_page(new_pdf.pages[3])
        output.add_page(existing_pdf.pages[i])

    # Guardar el PDF final
    with open(pdf_path, "wb") as output_stream:
        output.write(output_stream)

    doc = DocumentoCotizacion.objects.get(
        cotizacion=cotizacion_instance,        
    )
    doc.url_contrato = url_cotizacion=f'cotizaciones/{pdf_filename}'
    doc.save()

    return doc

# Generar PDF para cotizacion
def generar_pdf_cotizacion(cotizacion_instance, total):    
    pdfmetrics.registerFont(TTFont('Aleo', f'{settings.MEDIA_ROOT}Aleo-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('AleoLight', f'{settings.MEDIA_ROOT}Aleo-Thin.ttf'))
    pdfmetrics.registerFont(TTFont('Roboto', f'{settings.MEDIA_ROOT}Roboto_Condensed-Regular.ttf'))
    # Suponiendo que cotizacion_instance.fecha_evento es un objeto datetime
    fecha_formateada = cotizacion_instance.fecha_evento.strftime("%d de %B del %Y")
    fecha_formateada_creacion = cotizacion_instance.created_at.strftime("%d de %B del %Y")
    # Formatear el total como moneda mexicana
    total_formateado = "${:,.2f} MXN".format(total)
    pdf_filename = f"cotizacion_{cotizacion_instance.id}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'cotizaciones', pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    # Ruta al PDF base (plantilla)
    if cotizacion_instance.platillo.pk == 1: # Pollo
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_pollo_base.pdf')
    elif cotizacion_instance.platillo.pk == 2: # Puerco
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_cerdo_base.pdf')
    elif cotizacion_instance.platillo.pk == 3: # Italiano
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_italiano_base.pdf')
    elif cotizacion_instance.platillo.pk == 4: # Mixto
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_mixto_base.pdf')
    elif cotizacion_instance.platillo.pk == 5: # Premium
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_premium_base.pdf')
    elif cotizacion_instance.platillo.pk == 6: # Parrillada
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_parrillada_base.pdf')
    else: # Guiso
        pdf_template_path = os.path.join(settings.MEDIA_ROOT, '', 'cotizacion_guisos_base.pdf')        
    # Crear un PDF en memoria con la información dinámica
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    if cotizacion_instance.platillo.pk == 1:
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
        c.showPage()
        c.setFont("Roboto", 13)
        c.drawString(110, 365, f"{cotizacion_instance.colaborador.nombre}")
        c.setFont("Roboto", 11)
        c.drawString(340, 198, f"Cotización realizada el día {fecha_formateada_creacion}")
        c.showPage()
    elif cotizacion_instance.platillo.pk == 2:
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
    elif cotizacion_instance.platillo.pk == 5:
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
        cotizacion.status = False
        cotizacion.save()

