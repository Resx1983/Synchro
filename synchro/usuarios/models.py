from django.db import models
from django.contrib.auth.models import AbstractUser

class IntencionBusqueda(models.Model):
    id_intencion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    nombre_en = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    id_usuario = models.BigAutoField(primary_key=True)
    # email is used as login, so we make it unique
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True, unique=False) # override to allow blank
    
    nombre = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    intencion_busqueda = models.ForeignKey(IntencionBusqueda, on_delete=models.SET_NULL, null=True, blank=True)
    genero = models.CharField(max_length=50, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    idioma_preferido = models.CharField(max_length=20, default='es')
    tema_preferido = models.CharField(max_length=20, default='light')
    bio_ai = models.TextField(blank=True, null=True)
    embedding_perfil = models.JSONField(blank=True, null=True) # Useful to store AI vector points if any

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nombre']

    def __str__(self):
        return f"{self.email} - {self.nombre}"


class PreguntaEncuesta(models.Model):
    id_pregunta = models.AutoField(primary_key=True)
    texto_pregunta = models.TextField()
    texto_pregunta_en = models.TextField(blank=True, null=True)
    icono = models.CharField(max_length=50, blank=True, null=True)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return self.texto_pregunta


class RespuestaEncuesta(models.Model):
    id_respuesta = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(PreguntaEncuesta, on_delete=models.CASCADE)
    respuesta_texto = models.TextField()

    def __str__(self):
        return f"{self.usuario.email} - {self.pregunta.id_pregunta}"


class Match(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
    ]
    
    id_match = models.BigAutoField(primary_key=True)
    usuario1 = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='match_usuario1')
    usuario2 = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='match_usuario2')
    compatibilidad = models.DecimalField(max_digits=5, decimal_places=2, default=0.0) # e.g. 98.50
    explicacion_afinidad = models.TextField(blank=True, null=True)
    fecha_match = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    sugerencia_ia = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Match {self.id_match} - {self.usuario1.nombre} y {self.usuario2.nombre}"


class Mensaje(models.Model):
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
    id_sesion = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones')
    token = models.CharField(max_length=500) # Assuming it could be a JWT string copy
    expira_en = models.DateTimeField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sesión {self.id_sesion} de {self.usuario.email}"

