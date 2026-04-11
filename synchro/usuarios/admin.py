from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, IntencionBusqueda, PreguntaEncuesta, 
    RespuestaEncuesta, Match, Mensaje, Sesion
)

@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    model = Usuario
    # The fields to be used in displaying the User model
    list_display = ['email', 'nombre', 'is_staff', 'is_superuser']
    search_fields = ['email', 'nombre']
    ordering = ['email']
    
    # Custom fields we added
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Perfil', {'fields': ('nombre', 'fecha_nacimiento', 'ciudad', 'intencion_busqueda', 'genero', 'foto_perfil', 'idioma_preferido', 'tema_preferido', 'bio_ai', 'embedding_perfil')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'classes': ('wide',),
            'fields': ('email', 'nombre'),
        }),
    )

# Register the rest of the models simply
admin.site.register(IntencionBusqueda)
admin.site.register(PreguntaEncuesta)
admin.site.register(RespuestaEncuesta)
admin.site.register(Match)
admin.site.register(Mensaje)
admin.site.register(Sesion)

