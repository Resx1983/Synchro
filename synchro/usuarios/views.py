from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.generic import TemplateView
from .models import Usuario
from .serializers import UsuarioSerializer, RegistroUsuarioSerializer

class RegistroView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistroUsuarioSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = (IsAuthenticated,)


class MatchEmpezarView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return Response({
            "status": "success",
            "message": "Funcionalidad 'Empezar el match' en construcción. ¡Próximamente conectaremos perfiles compatibles!"
        }, status=status.HTTP_200_OK)

# --- Frontend Views ---
class InicioView(TemplateView):
    template_name = 'usuarios/inicio.html'

class LoginFrontendView(TemplateView):
    template_name = 'usuarios/login.html'

class RegistroFrontendView(TemplateView):
    template_name = 'usuarios/registro.html'

