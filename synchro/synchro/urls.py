"""
URL configuration for synchro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import InicioView, LoginFrontendView, RegistroFrontendView

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('api/usuarios/', include('usuarios.urls')),
    
    # Frontend Routes
=======
    
    # Rutas de la API REST (definidas en usuarios/urls.py)
    path('api/usuarios/', include('usuarios.urls')),
    
    # Rutas del Frontend (Vistas de plantillas HTML)
>>>>>>> master
    path('', InicioView.as_view(), name='inicio_web'),
    path('login/', LoginFrontendView.as_view(), name='login_web'),
    path('registro/', RegistroFrontendView.as_view(), name='registro_web'),
]

<<<<<<< HEAD
=======
# Configuración para servir archivos multimedia (fotos de perfil, etc.) en desarrollo
>>>>>>> master
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

