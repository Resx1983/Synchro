from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegistroView, UsuarioViewSet, MatchEmpezarView

router = DefaultRouter()
router.register(r'lista', UsuarioViewSet, basename='usuario')

urlpatterns = [
    # Auth y Registro
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Endpoint Match
    path('empezar-match/', MatchEmpezarView.as_view(), name='empezar_match'),
    
    # CRUD Usuarios
    path('', include(router.urls)),
]
