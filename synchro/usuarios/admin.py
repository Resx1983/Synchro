from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from usuarios.models import (
    Usuario, IntencionBusqueda, PreguntaEncuesta, 
    RespuestaEncuesta, Match, Mensaje, Sesion
)

@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    """
    Personalización del panel de administración para el modelo de Usuario.
    Permite gestionar los campos personalizados desde la interfaz de Django.
    """
    model = Usuario
    # Campos que se muestran en la lista principal
    list_display = ['email', 'nombre', 'is_staff', 'is_superuser']
    search_fields = ['email', 'nombre']
    ordering = ['email']
    
    # Agregamos nuestros campos personalizados a los formularios de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Perfil Synchro', {
            'fields': (
                'nombre', 'fecha_nacimiento', 'ciudad', 
                'intencion_busqueda', 'genero', 'foto_perfil', 
                'idioma_preferido', 'tema_preferido', 'bio_ai', 
                'embedding_perfil'
            )
        }),
    )

    # Campos requeridos al crear un usuario desde el admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Inicial', {
            'classes': ('wide',),
            'fields': ('email', 'nombre'),
        }),
    )

# Registro básico de los demás modelos para que sean editables en el panel admin
admin.site.register(IntencionBusqueda)
admin.site.register(PreguntaEncuesta)
admin.site.register(RespuestaEncuesta)
admin.site.register(Match)
admin.site.register(Mensaje)
admin.site.register(Sesion)

