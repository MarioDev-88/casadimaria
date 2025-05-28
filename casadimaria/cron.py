# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Cotizacion

# Cron para dar por cancelada una cotizacion al pasar 15 dias
def CronVencerCotizacion():
    fecha_actual = timezone.now()
    for cotizacion in Cotizacion.objects.filter(status=1, contrato=False):
        diff = fecha_actual - cotizacion.created_at
        if diff.days == 15:
            cotizacion.status = 2
            cotizacion.fecha_cancelacion = datetime.now()
            cotizacion.save()