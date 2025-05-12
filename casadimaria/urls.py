"""casadimaria URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from tastypie.api import Api
from .api import *

v1_api = Api(api_name='v1')

v1_api.register(CreateUser())
v1_api.register(CrearColaboradores())
v1_api.register(Login())
v1_api.register(GetEvento())
v1_api.register(GetPlatillo())
v1_api.register(GetComplemento())
v1_api.register(GetCostoFijo())
v1_api.register(GetColaboradores())
v1_api.register(GetCotizacion())
v1_api.register(CrearCotizacion())
v1_api.register(GenerarContrato())
v1_api.register(EliminarColaboradores())
v1_api.register(CancelarCotizacion())
v1_api.register(CrearEvento())
v1_api.register(CrearPlatillo())
v1_api.register(CrearPlatilloJoven())
v1_api.register(CrearCostoFijo())

urlpatterns = [
    path('api/', include(v1_api.urls)),
    path('admin/', admin.site.urls),
    re_path(r'^cotizaciones/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
