from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ChatFrontendView,
    EncuestaFrontendView,
    IntencionBusquedaView,
    LoginFrontendView,
    MatchDetailView,
    MatchEmpezarView,
    MatchListView,
    MatchesFrontendView,
    MensajesMatchView,
    PreguntasEncuestaView,
    RegistroFrontendView,
    RegistroView,
    RespuestasEncuestaView,
    UsuarioViewSet,
)

router = DefaultRouter()
router.register(r'lista', UsuarioViewSet, basename='usuario')

urlpatterns = [
    # Auth y Registro
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('intenciones/', IntencionBusquedaView.as_view(), name='intenciones_busqueda'),
    path('preguntas/', PreguntasEncuestaView.as_view(), name='preguntas_encuesta'),
    path('respuestas/', RespuestasEncuestaView.as_view(), name='respuestas_encuesta'),
    
    # Endpoint Match
    path('empezar-match/', MatchEmpezarView.as_view(), name='empezar_match'),
    path('matches/', MatchListView.as_view(), name='lista_matches'),
    path('matches/<int:match_id>/', MatchDetailView.as_view(), name='detalle_match'),
    path('matches/<int:match_id>/mensajes/', MensajesMatchView.as_view(), name='mensajes_match'),
    
    # CRUD Usuarios
    path('', include(router.urls)),

    # Frontend routes
    path('frontend/encuesta/', EncuestaFrontendView.as_view(), name='encuesta_web'),
    path('frontend/matches/', MatchesFrontendView.as_view(), name='matches_web'),
    path('frontend/chat/<int:match_id>/', ChatFrontendView.as_view(), name='chat_web'),
]
