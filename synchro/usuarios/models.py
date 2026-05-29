from django.db import models
from django.contrib.auth.models import AbstractUser

class IntencionBusqueda(models.Model):
    """
    Representa las diferentes intenciones que un usuario puede tener al usar la plataforma
    (por ejemplo: 'Encontrar equipo', 'Hacer networking', etc.).
    """
    id_intencion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    nombre_en = models.CharField(max_length=100, blank=True, null=True) # Traducción al inglés

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que utiliza el email como identificador principal.
    Almacena información del perfil, preferencias y datos generados por IA.
    """
    id_usuario = models.BigAutoField(primary_key=True)
    # El email se utiliza para el login, por lo que debe ser único.
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True, unique=False) # Permitimos username nulo/blanco
    
    nombre = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    intencion_busqueda = models.ForeignKey(IntencionBusqueda, on_delete=models.SET_NULL, null=True, blank=True)
    genero = models.CharField(max_length=50, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    idioma_preferido = models.CharField(max_length=20, default='es')
    tema_preferido = models.CharField(max_length=20, default='light')
    
    # Campo para almacenar la biografía generada o analizada por IA
    bio_ai = models.TextField(blank=True, null=True)
    
    # Almacena vectores o puntos de referencia para algoritmos de recomendación
    embedding_perfil = models.JSONField(blank=True, null=True) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nombre']

    def __str__(self):
        return f"{self.email} - {self.nombre}"


class PreguntaEncuesta(models.Model):
    """
    Define las preguntas de la encuesta inicial para determinar la compatibilidad.
    """
    id_pregunta = models.AutoField(primary_key=True)
    texto_pregunta = models.TextField()
    texto_pregunta_en = models.TextField(blank=True, null=True)
    icono = models.CharField(max_length=50, blank=True, null=True) # Icono visual para la UI
    orden = models.IntegerField(default=0) # Controla el orden de aparición

    def __str__(self):
        return self.texto_pregunta


class RespuestaEncuesta(models.Model):
    """
    Almacena las respuestas de cada usuario a las preguntas de la encuesta.
    """
    id_respuesta = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(PreguntaEncuesta, on_delete=models.CASCADE)
    respuesta_texto = models.TextField()

    def __str__(self):
        return f"{self.usuario.email} - Pregunta {self.pregunta.id_pregunta}"


class Match(models.Model):
    """
    Representa una conexión establecida entre dos usuarios.
    Incluye métricas de compatibilidad calculadas por el sistema.
    """
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
    ]
    
    id_match = models.BigAutoField(primary_key=True)
    usuario1 = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='match_usuario1')
    usuario2 = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='match_usuario2')
    
    # Porcentaje de compatibilidad (ej. 98.50)
    compatibilidad = models.DecimalField(max_digits=5, decimal_places=2, default=0.0) 
    # Justificación de por qué el sistema cree que son compatibles
    explicacion_afinidad = models.TextField(blank=True, null=True)
    
    fecha_match = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Recomendación o rompehielos generado por IA
    sugerencia_ia = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Match {self.id_match} - {self.usuario1.nombre} y {self.usuario2.nombre}"


class Mensaje(models.Model):
    """
    Almacena los mensajes de chat entre dos usuarios que tienen un match.
    """
    TIPOS = [
        ('texto', 'Texto'),
        ('imagen', 'Imagen'),
        ('audio', 'Audio'),
        ('sistema', 'Sistema'),
    ]

    id_mensaje = models.BigAutoField(primary_key=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='mensajes')
    remitente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    mensaje = models.TextField()
    fecha_mensaje = models.DateTimeField(auto_now_add=True)
    tipo_mensaje = models.CharField(max_length=20, choices=TIPOS, default='texto')
    estado_leido = models.BooleanField(default=False)

    def __str__(self):
        return f"De {self.remitente.email} a {self.destinatario.email}: {self.mensaje[:20]}"


class Sesion(models.Model):
    """
    Maneja el registro de sesiones activas y la expiración de tokens.
    """
    id_sesion = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones')
    token = models.CharField(max_length=500) # Copia del token JWT o similar
    expira_en = models.DateTimeField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sesión {self.id_sesion} de {self.usuario.email}"

