# ---------------------------------------------------------------------------
# Configuración de URLs para la aplicación 'usuarios'
# Define los endpoints de la API REST y la autenticación JWT
#
# ESTRUCTURA GENERAL DE LA API:
#   /api/usuarios/registro/       → Registro de nuevos usuarios (POST)
#   /api/usuarios/login/          → Obtener token JWT (POST con email + password)
#   /api/usuarios/login/refresh/  → Renovar token JWT expirado (POST con refresh token)
#   /api/usuarios/empezar-match/  → Iniciar proceso de matching IA (POST, requiere token)
#   /api/usuarios/lista/          → CRUD de usuarios (GET, POST, PUT, DELETE)
#   /api/usuarios/intenciones/    → CRUD de intenciones de búsqueda
#   /api/usuarios/preguntas/      → CRUD de preguntas de encuesta
#   /api/usuarios/respuestas/     → CRUD de respuestas de encuesta
#   /api/usuarios/matches/        → CRUD de matches entre usuarios
#   /api/usuarios/mensajes/       → CRUD de mensajes de chat
#   /api/usuarios/sesiones/       → Lectura de sesiones activas (solo GET)
# ---------------------------------------------------------------------------

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegistroView,
    UsuarioViewSet,
    IntencionBusquedaViewSet,
    PreguntaEncuestaViewSet,
    RespuestaEncuestaViewSet,
    MatchViewSet,
    MensajeViewSet,
    SesionViewSet,
    MatchEmpezarView,
    CustomTokenObtainPairView, # Vista personalizada que extiende el login JWT
)

# ---------------------------------------------------------------------------
# Router de DRF (Django Rest Framework)
#
# El DefaultRouter genera automáticamente las rutas estándar para cada ViewSet:
#   - GET    /recurso/       → Listar todos (list)
#   - POST   /recurso/       → Crear uno nuevo (create)
#   - GET    /recurso/{id}/  → Ver detalle de uno (retrieve)
#   - PUT    /recurso/{id}/  → Actualizar completo (update)
#   - PATCH  /recurso/{id}/  → Actualizar parcial (partial_update)
#   - DELETE /recurso/{id}/  → Eliminar (destroy)
#
# Ejemplo: al registrar 'lista' con UsuarioViewSet, se crean:
#   GET    /api/usuarios/lista/       → Lista todos los usuarios
#   POST   /api/usuarios/lista/       → Crea un usuario
#   GET    /api/usuarios/lista/1/     → Detalle del usuario con id=1
#   PUT    /api/usuarios/lista/1/     → Actualiza el usuario con id=1
#   DELETE /api/usuarios/lista/1/     → Elimina el usuario con id=1
# ---------------------------------------------------------------------------
router = DefaultRouter()
router.register(r'lista',           UsuarioViewSet,          basename='usuario')
router.register(r'intenciones',     IntencionBusquedaViewSet, basename='intencion')
router.register(r'preguntas',       PreguntaEncuestaViewSet,  basename='pregunta')
router.register(r'respuestas',      RespuestaEncuestaViewSet, basename='respuesta')
router.register(r'matches',         MatchViewSet,             basename='match')
router.register(r'mensajes',        MensajeViewSet,           basename='mensaje')
router.register(r'sesiones',        SesionViewSet,            basename='sesion')

urlpatterns = [
    # -----------------------------------------------------------------------
    # AUTENTICACIÓN Y REGISTRO
    # -----------------------------------------------------------------------

    # REGISTRO DE NUEVOS USUARIOS
    # Método: POST
    # URL: /api/usuarios/registro/
    # Body esperado (JSON):
    #   {
    #       "email": "correo@ejemplo.com",
    #       "nombre": "Nombre del usuario",
    #       "password": "contraseña_segura"
    #   }
    # Respuesta: Los datos del usuario creado (sin la contraseña)
    # Nota: Este endpoint es público, NO requiere token de autenticación
    path('registro/',      RegistroView.as_view(),           name='registro'),

    # LOGIN - OBTENCIÓN DE TOKEN JWT
    # Método: POST
    # URL: /api/usuarios/login/
    # Body esperado (JSON):
    #   {
    #       "email": "correo@ejemplo.com",
    #       "password": "contraseña"
    #   }
    # Respuesta exitosa (200):
    #   {
    #       "access": "eyJ...",    ← Token de acceso (dura 1 día, se envía en cada request)
    #       "refresh": "eyJ...",   ← Token de refresco (dura 7 días, sirve para renovar el access)
    #       "user": {              ← Datos del perfil (añadido por nuestro serializer personalizado)
    #           "id": 1,
    #           "nombre": "Thomas",
    #           "email": "correo@ejemplo.com",
    #           "foto_perfil": null
    #       }
    #   }
    # Respuesta fallida (401):
    #   { "detail": "No active account found with the given credentials" }
    #
    # IMPORTANTE: Usa CustomTokenObtainPairView en lugar de la vista por defecto
    # para guardar la sesión en la DB y devolver datos del usuario en la respuesta.
    path('login/',         CustomTokenObtainPairView.as_view(),    name='token_obtain_pair'),

    # RENOVAR TOKEN JWT (REFRESH)
    # Método: POST
    # URL: /api/usuarios/login/refresh/
    # Body esperado (JSON):
    #   {
    #       "refresh": "eyJ..."   ← El refresh token obtenido en el login
    #   }
    # Respuesta exitosa (200):
    #   {
    #       "access": "eyJ...",   ← Nuevo token de acceso
    #       "refresh": "eyJ..."   ← Nuevo refresh token (porque ROTATE_REFRESH_TOKENS=True)
    #   }
    # ¿Cuándo usar esto? Cuando el token de acceso haya expirado (después de 1 día)
    # y no quieras obligar al usuario a iniciar sesión de nuevo.
    path('login/refresh/', TokenRefreshView.as_view(),       name='token_refresh'),

    # -----------------------------------------------------------------------
    # ACCIONES ESPECIALES
    # -----------------------------------------------------------------------

    # INICIAR PROCESO DE MATCHING POR IA
    # Método: POST
    # URL: /api/usuarios/empezar-match/
    # Requiere: Token JWT en el header → Authorization: Bearer <access_token>
    # Estado: En construcción (actualmente devuelve un mensaje informativo)
    path('empezar-match/', MatchEmpezarView.as_view(),       name='empezar_match'),

    # -----------------------------------------------------------------------
    # CRUD DE RECURSOS (generados automáticamente por el Router)
    # Todos estos endpoints requieren autenticación JWT.
    # Para usarlos, incluir en el header de cada petición:
    #   Authorization: Bearer <access_token>
    # -----------------------------------------------------------------------
    path('', include(router.urls)),
]
