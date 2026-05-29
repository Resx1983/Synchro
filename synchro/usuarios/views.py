from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.generic import TemplateView
<<<<<<< HEAD
from .models import Usuario
from .serializers import UsuarioSerializer, RegistroUsuarioSerializer

class RegistroView(generics.CreateAPIView):
=======

from .models import Usuario, IntencionBusqueda, PreguntaEncuesta, RespuestaEncuesta, Match, Mensaje, Sesion
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UsuarioSerializer,
    RegistroUsuarioSerializer,
    IntencionBusquedaSerializer,
    PreguntaEncuestaSerializer,
    RespuestaEncuestaSerializer,
    MatchSerializer,
    MensajeSerializer,
    SesionSerializer,
    CustomTokenObtainPairSerializer, # Importado
)


# ---------------------------------------------------------------------------
# Auth / Registro
# ---------------------------------------------------------------------------

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista de login (Token Obtain).
    Sustituye a la vista por defecto de SimpleJWT para usar nuestro
    serializador personalizado (CustomTokenObtainPairSerializer),
    el cual se encarga de guardar la sesión en la DB.
    """
    serializer_class = CustomTokenObtainPairSerializer

class RegistroView(generics.CreateAPIView):
    """
    Vista para registrar nuevos usuarios en el sistema.
    Permite el acceso público (sin token).
    """
>>>>>>> master
    queryset = Usuario.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistroUsuarioSerializer

<<<<<<< HEAD
class UsuarioViewSet(viewsets.ModelViewSet):
    
=======

# ---------------------------------------------------------------------------
# ViewSets REST
# ---------------------------------------------------------------------------

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    Gestiona los perfiles de los usuarios.
    Requiere autenticación para cualquier operación.
    """
>>>>>>> master
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = (IsAuthenticated,)


<<<<<<< HEAD
class MatchEmpezarView(APIView):
=======
class IntencionBusquedaViewSet(viewsets.ModelViewSet):
    queryset = IntencionBusqueda.objects.all()
    serializer_class = IntencionBusquedaSerializer
    permission_classes = (IsAuthenticated,)


class PreguntaEncuestaViewSet(viewsets.ModelViewSet):
    queryset = PreguntaEncuesta.objects.all().order_by('orden')
    serializer_class = PreguntaEncuestaSerializer
    permission_classes = (IsAuthenticated,)


class RespuestaEncuestaViewSet(viewsets.ModelViewSet):
    """
    Gestiona las respuestas de la encuesta.
    Un usuario solo puede ver y editar sus propias respuestas.
    """
    serializer_class = RespuestaEncuestaSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Filtramos para que cada usuario solo vea sus propias respuestas
        return RespuestaEncuesta.objects.filter(usuario=self.request.user)


class MatchViewSet(viewsets.ModelViewSet):
    """
    Muestra los matches del usuario autenticado.
    Filtra los registros donde el usuario es usuario1 o usuario2.
    """
    serializer_class = MatchSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Match.objects.filter(usuario1=user) | Match.objects.filter(usuario2=user)


class MensajeViewSet(viewsets.ModelViewSet):
    serializer_class = MensajeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Mensaje.objects.filter(remitente=user) | Mensaje.objects.filter(destinatario=user)


class SesionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SesionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Sesion.objects.filter(usuario=self.request.user)


# ---------------------------------------------------------------------------
# Endpoint de Match especial
# ---------------------------------------------------------------------------

class MatchEmpezarView(APIView):
    """
    Endpoint dedicado para iniciar el proceso de matching mediante IA.
    (Actualmente en desarrollo).
    """
>>>>>>> master
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return Response({
            "status": "success",
<<<<<<< HEAD
            "message": "Funcionalidad 'Empezar el match' en construcción. ¡Próximamente conectaremos perfiles compatibles!"
        }, status=status.HTTP_200_OK)

# --- Frontend Views ---
=======
            "message": "Funcionalidad 'Empezar el match' en construcción. ¡Próximamente conectaremos perfiles compatibles mediante IA!"
        }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Frontend Views
# ---------------------------------------------------------------------------

>>>>>>> master
class InicioView(TemplateView):
    template_name = 'usuarios/inicio.html'

class LoginFrontendView(TemplateView):
    template_name = 'usuarios/login.html'

class RegistroFrontendView(TemplateView):
    template_name = 'usuarios/registro.html'
<<<<<<< HEAD

=======
>>>>>>> master
