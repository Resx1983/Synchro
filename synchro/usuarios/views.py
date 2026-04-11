from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Usuario
from .serializers import UsuarioSerializer, RegistroUsuarioSerializer

class RegistroView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistroUsuarioSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD Completo para usuarios.
    Protegido para que solo usuarios autenticados puedan modificar o ver datos.
    Dependiendo de las reglas, tal vez un usuario solo deba poder editarse a sí mismo.
    Por ahora es un CRUD general que requiere estar logueado.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = (IsAuthenticated,)


class MatchEmpezarView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # Este endpoint está en construcción según lo solicitado en el plan
        # Aquí se ejecutaría la lógica del algoritmo o creación de un "Match" inicial.
        return Response({
            "status": "success",
            "message": "Funcionalidad 'Empezar el match' en construcción. ¡Próximamente conectaremos perfiles compatibles!"
        }, status=status.HTTP_200_OK)

