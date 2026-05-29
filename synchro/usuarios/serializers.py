<<<<<<< HEAD
from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
=======
# ---------------------------------------------------------------------------
# SERIALIZERS - Aplicación 'usuarios'
#
# ¿Qué es un Serializer?
# Es el componente que convierte los objetos de Django (modelos) a JSON
# y viceversa. Actúa como un "traductor" entre la base de datos y la API.
#
# Flujo de datos:
#   FRONTEND → JSON → Serializer (valida) → Modelo → Base de Datos  (ESCRITURA)
#   Base de Datos → Modelo → Serializer (formatea) → JSON → FRONTEND (LECTURA)
#
# Cada modelo tiene su serializer correspondiente. Algunos modelos tienen
# más de uno (ej: Usuario tiene UsuarioSerializer y RegistroUsuarioSerializer)
# porque necesitan comportamientos diferentes según la operación.
# ---------------------------------------------------------------------------

from rest_framework import serializers
from .models import (
    Usuario, IntencionBusqueda, PreguntaEncuesta,
    RespuestaEncuesta, Match, Mensaje, Sesion
)


# ===========================================================================
# SERIALIZERS DE USUARIO
# ===========================================================================

class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer principal del perfil de usuario.
    Se usa para VER y ACTUALIZAR la información personal de un usuario existente.

    Campos expuestos:
        - id_usuario: Identificador único (solo lectura, lo genera la DB)
        - email: Correo electrónico del usuario
        - nombre: Nombre completo
        - fecha_nacimiento: Fecha de nacimiento (formato: "YYYY-MM-DD")
        - ciudad: Ciudad de residencia
        - intencion_busqueda: FK a la intención (se envía el ID numérico)
        - genero: Género del usuario
        - foto_perfil: URL de la foto de perfil
        - idioma_preferido: "es" o "en"
        - tema_preferido: "light" o "dark"
        - bio_ai: Biografía generada/analizada por IA

    Ejemplo de respuesta JSON:
        {
            "id_usuario": 1,
            "email": "usuario@correo.com",
            "nombre": "Thomas",
            "fecha_nacimiento": "2000-01-15",
            "ciudad": "Medellín",
            "intencion_busqueda": 2,
            "genero": "Masculino",
            "foto_perfil": "/media/perfiles/foto.jpg",
            "idioma_preferido": "es",
            "tema_preferido": "dark",
            "bio_ai": "Le gusta la tecnología..."
        }
    """
>>>>>>> master
    class Meta:
        model = Usuario
        fields = [
            'id_usuario', 'email', 'nombre', 'fecha_nacimiento',
            'ciudad', 'intencion_busqueda', 'genero', 'foto_perfil',
<<<<<<< HEAD
            'idioma_preferido', 'tema_preferido', 'bio_ai'
        ]
        read_only_fields = ['id_usuario']

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
=======
            'idioma_preferido', 'tema_preferido', 'bio_ai',
        ]
        # read_only_fields: campos que el usuario NO puede modificar manualmente
        read_only_fields = ['id_usuario']


class UsuarioResumenSerializer(serializers.ModelSerializer):
    """
    Versión LIGERA del serializer de usuario.
    Se usa para anidar dentro de Match y Mensaje, mostrando solo los datos
    mínimos necesarios sin exponer información sensible (email, bio, etc.).

    Ejemplo de respuesta JSON:
        {
            "id_usuario": 1,
            "nombre": "Thomas",
            "foto_perfil": "/media/perfiles/foto.jpg",
            "ciudad": "Medellín"
        }
    """
    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nombre', 'foto_perfil', 'ciudad']


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer especializado SOLO para el REGISTRO de nuevos usuarios.
    A diferencia de UsuarioSerializer, este:
      - Acepta 'password' (write_only: se envía pero NUNCA se devuelve en la respuesta)
      - Solo requiere los campos mínimos: email, nombre, password
      - Usa create_user() para hashear la contraseña (NUNCA se guarda en texto plano)

    Body esperado (JSON):
        {
            "email": "nuevo@correo.com",
            "nombre": "Nuevo Usuario",
            "password": "mi_contraseña_segura"
        }

    Respuesta exitosa (201):
        {
            "email": "nuevo@correo.com",
            "nombre": "Nuevo Usuario"
        }
    Nota: La contraseña NO aparece en la respuesta porque es write_only.
    """
    # write_only=True: el campo acepta datos de entrada pero NUNCA se incluye en la salida
    password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'}
    )
>>>>>>> master

    class Meta:
        model = Usuario
        fields = ['email', 'nombre', 'password']

    def create(self, validated_data):
<<<<<<< HEAD
        # We use create_user so the password gets hashed correctly
=======
        """
        Crea un nuevo usuario con la contraseña hasheada.

        ¿Por qué create_user y no objects.create?
        - create_user() hashea la contraseña automáticamente (ej: pbkdf2_sha256$...)
        - objects.create() guardaría la contraseña en texto plano → INSEGURO

        También asignamos el email como username porque nuestro modelo
        usa email como campo de login (USERNAME_FIELD = 'email').
        """
>>>>>>> master
        user = Usuario.objects.create_user(
            email=validated_data['email'],
            nombre=validated_data['nombre'],
            password=validated_data['password'],
<<<<<<< HEAD
            # we can pass username as email to satisfy abstractuser if we really need to,
            # but we overrode username to allow blank/null. Let's provide it anyway.
            username=validated_data['email']
        )
        return user
=======
            username=validated_data['email'], # Usamos el email como username por defecto
        )
        return user


# ===========================================================================
# SERIALIZER DE INTENCIÓN DE BÚSQUEDA
# ===========================================================================

class IntencionBusquedaSerializer(serializers.ModelSerializer):
    """
    Serializer para las intenciones de búsqueda del usuario.
    Ejemplo: "Encontrar equipo", "Hacer networking", etc.

    Ejemplo de respuesta JSON:
        {
            "id_intencion": 1,
            "nombre": "Encontrar equipo",
            "nombre_en": "Find a team"
        }
    """
    class Meta:
        model = IntencionBusqueda
        fields = ['id_intencion', 'nombre', 'nombre_en']
        read_only_fields = ['id_intencion']


# ===========================================================================
# SERIALIZER DE PREGUNTAS DE ENCUESTA
# ===========================================================================

class PreguntaEncuestaSerializer(serializers.ModelSerializer):
    """
    Serializer para las preguntas de la encuesta de compatibilidad.

    Ejemplo de respuesta JSON:
        {
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué tipo de proyectos te interesan?",
            "texto_pregunta_en": "What kind of projects interest you?",
            "icono": "🚀",
            "orden": 1
        }
    """
    class Meta:
        model = PreguntaEncuesta
        fields = ['id_pregunta', 'texto_pregunta', 'texto_pregunta_en', 'icono', 'orden']
        read_only_fields = ['id_pregunta']


# ===========================================================================
# SERIALIZER DE RESPUESTAS DE ENCUESTA
# ===========================================================================

class RespuestaEncuestaSerializer(serializers.ModelSerializer):
    """
    Serializer para las respuestas de cada usuario a las preguntas de la encuesta.

    Campos especiales:
        - pregunta (write_only): Al CREAR una respuesta, solo se envía el ID de la pregunta
        - pregunta_detalle (read_only): Al LEER, se muestra la pregunta completa anidada
        - usuario (hidden): Se asigna automáticamente al usuario autenticado (request.user)

    Body para CREAR (POST):
        {
            "pregunta": 1,                        ← Solo el ID de la pregunta
            "respuesta_texto": "Me gustan los proyectos de IA"
        }

    Respuesta al LEER (GET):
        {
            "id_respuesta": 10,
            "pregunta_detalle": {                  ← Pregunta completa anidada
                "id_pregunta": 1,
                "texto_pregunta": "¿Qué tipo de proyectos te interesan?",
                "texto_pregunta_en": "What kind of projects interest you?",
                "icono": "🚀",
                "orden": 1
            },
            "respuesta_texto": "Me gustan los proyectos de IA"
        }
    """
    # source='pregunta': le dice a DRF que tome los datos del campo 'pregunta' del modelo
    # read_only=True: solo aparece en la respuesta, no se espera al enviar datos
    pregunta_detalle = PreguntaEncuestaSerializer(source='pregunta', read_only=True)

    # write_only=True: solo se usa al enviar datos (POST/PUT), no aparece en la respuesta
    pregunta = serializers.PrimaryKeyRelatedField(
        queryset=PreguntaEncuesta.objects.all(), write_only=True
    )

    # HiddenField + CurrentUserDefault: el usuario se toma automáticamente del request
    # → El frontend NO necesita enviar el ID del usuario, se detecta por el token JWT
    usuario = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = RespuestaEncuesta
        fields = ['id_respuesta', 'usuario', 'pregunta', 'pregunta_detalle', 'respuesta_texto']
        read_only_fields = ['id_respuesta']


# ===========================================================================
# SERIALIZER DE MATCH
# ===========================================================================

class MatchSerializer(serializers.ModelSerializer):
    """
    Serializer para los matches (conexiones) entre dos usuarios.

    Usa el patrón de "doble campo" para cada usuario:
        - usuario1 / usuario2: Para ESCRIBIR, se envía solo el ID numérico
        - usuario1_detalle / usuario2_detalle: Para LEER, se devuelve el perfil resumido

    Body para CREAR (POST):
        {
            "usuario1": 1,                         ← ID del primer usuario
            "usuario2": 2,                         ← ID del segundo usuario
            "compatibilidad": 85.50,
            "explicacion_afinidad": "Ambos disfrutan de la tecnología",
            "sugerencia_ia": "¡Hablen sobre sus proyectos de IA!",
            "estado": "pendiente"
        }

    Respuesta al LEER (GET):
        {
            "id_match": 1,
            "usuario1": 1,
            "usuario1_detalle": {                  ← Perfil resumido anidado
                "id_usuario": 1,
                "nombre": "Thomas",
                "foto_perfil": null,
                "ciudad": "Medellín"
            },
            "usuario2": 2,
            "usuario2_detalle": { ... },
            "compatibilidad": "85.50",
            "explicacion_afinidad": "Ambos disfrutan...",
            "fecha_match": "2026-05-07T20:00:00Z",
            "fecha_actualizacion": "2026-05-07T20:00:00Z",
            "sugerencia_ia": "¡Hablen sobre...",
            "estado": "pendiente"
        }

    Validaciones:
        - No se permite que un usuario haga match consigo mismo
    """
    # Campos de LECTURA: muestran el perfil resumido de cada usuario
    usuario1_detalle = UsuarioResumenSerializer(source='usuario1', read_only=True)
    usuario2_detalle = UsuarioResumenSerializer(source='usuario2', read_only=True)

    # Campos de ESCRITURA: aceptan el ID numérico del usuario
    usuario1 = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())
    usuario2 = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = Match
        fields = [
            'id_match',
            'usuario1', 'usuario1_detalle',
            'usuario2', 'usuario2_detalle',
            'compatibilidad', 'explicacion_afinidad',
            'fecha_match', 'fecha_actualizacion',
            'sugerencia_ia', 'estado',
        ]
        read_only_fields = ['id_match', 'fecha_match', 'fecha_actualizacion']

    def validate(self, attrs):
        """Validación personalizada: un usuario NO puede hacer match consigo mismo."""
        if attrs.get('usuario1') == attrs.get('usuario2'):
            raise serializers.ValidationError("Un usuario no puede hacer match consigo mismo.")
        return attrs


# ===========================================================================
# SERIALIZER DE MENSAJE
# ===========================================================================

class MensajeSerializer(serializers.ModelSerializer):
    """
    Serializer para el envío y recepción de mensajes de chat.

    Lógica especial:
        - El remitente se asigna automáticamente al usuario del token (HiddenField)
        - Se valida que tanto remitente como destinatario pertenezcan al match

    Body para ENVIAR un mensaje (POST):
        {
            "match": 1,                            ← ID del match al que pertenece la conversación
            "destinatario": 2,                     ← ID del usuario que recibe el mensaje
            "mensaje": "¡Hola! ¿Cómo estás?",
            "tipo_mensaje": "texto"                ← Opciones: "texto", "imagen", "audio", "sistema"
        }
    Nota: El 'remitente' NO se envía, se detecta automáticamente del token JWT.

    Respuesta al LEER (GET):
        {
            "id_mensaje": 1,
            "match": 1,
            "remitente_detalle": {
                "id_usuario": 1,
                "nombre": "Thomas",
                "foto_perfil": null,
                "ciudad": "Medellín"
            },
            "destinatario_detalle": { ... },
            "mensaje": "¡Hola! ¿Cómo estás?",
            "fecha_mensaje": "2026-05-07T20:30:00Z",
            "tipo_mensaje": "texto",
            "estado_leido": false
        }
    """
    # Detalles de perfil para la lectura (read_only)
    remitente_detalle = UsuarioResumenSerializer(source='remitente', read_only=True)
    destinatario_detalle = UsuarioResumenSerializer(source='destinatario', read_only=True)

    # El remitente siempre es el usuario autenticado (se detecta del token JWT)
    remitente = serializers.HiddenField(default=serializers.CurrentUserDefault())
    destinatario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())
    match = serializers.PrimaryKeyRelatedField(queryset=Match.objects.all())

    class Meta:
        model = Mensaje
        fields = [
            'id_mensaje',
            'match',
            'remitente', 'remitente_detalle',
            'destinatario', 'destinatario_detalle',
            'mensaje', 'fecha_mensaje', 'tipo_mensaje', 'estado_leido',
        ]
        read_only_fields = ['id_mensaje', 'fecha_mensaje']

    def validate(self, attrs):
        """
        Regla de negocio: Solo los participantes de un match pueden enviarse mensajes.
        Se verifica que tanto el remitente (usuario autenticado) como el destinatario
        sean parte del match indicado.
        """
        match = attrs.get('match')
        remitente = self.context['request'].user
        destinatario = attrs.get('destinatario')

        # Obtenemos los IDs de los dos participantes del match
        participantes = {match.usuario1_id, match.usuario2_id}

        # Verificamos que ambos (remitente y destinatario) estén en ese match
        if remitente.pk not in participantes or destinatario.pk not in participantes:
            raise serializers.ValidationError(
                "Remitente y destinatario deben ser participantes del match especificado."
            )
        return attrs


# ===========================================================================
# SERIALIZER DE SESIÓN
# ===========================================================================

class SesionSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de sesiones activas.
    Cada vez que un usuario hace login, se crea un registro de sesión
    (ver CustomTokenObtainPairSerializer más abajo).

    Este serializer es de SOLO LECTURA (se usa con ReadOnlyModelViewSet en views.py).

    Ejemplo de respuesta JSON:
        {
            "id_sesion": 1,
            "usuario": 1,
            "token": "eyJ...",
            "expira_en": "2026-05-08T20:00:00Z",
            "creado_en": "2026-05-07T20:00:00Z"
        }
    """
    class Meta:
        model = Sesion
        fields = ['id_sesion', 'usuario', 'token', 'expira_en', 'creado_en']
        read_only_fields = ['id_sesion', 'creado_en']


# ===========================================================================
# SERIALIZER PERSONALIZADO DE LOGIN (JWT)
# ===========================================================================

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone
from datetime import timedelta

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado que EXTIENDE el login por defecto de SimpleJWT.

    ¿Por qué personalizar?
    El login por defecto solo devuelve { "access": "...", "refresh": "..." }.
    Nosotros queremos:
      1. Incluir datos del usuario en la respuesta (nombre, email, foto)
         → Así el frontend no tiene que hacer OTRA petición para obtener el perfil
      2. Guardar un registro de sesión en la base de datos
         → Para auditoría y control de sesiones activas
      3. Añadir el nombre del usuario dentro del token JWT
         → Para que el frontend pueda leer 'nombre' decodificando el token

    FLUJO COMPLETO DEL LOGIN:
    ┌─────────────────────────────────────────────────────────────┐
    │  1. Frontend envía POST a /api/usuarios/login/              │
    │     Body: { "email": "...", "password": "..." }             │
    │                                                             │
    │  2. SimpleJWT verifica las credenciales contra la DB        │
    │     → Si son incorrectas: devuelve 401 Unauthorized        │
    │     → Si son correctas: continúa al paso 3                 │
    │                                                             │
    │  3. get_token() genera el JWT con el nombre en el payload   │
    │                                                             │
    │  4. validate() guarda la sesión en la tabla 'Sesion'        │
    │                                                             │
    │  5. Se devuelve la respuesta con tokens + datos del usuario │
    │     {                                                       │
    │       "access": "eyJ...",                                   │
    │       "refresh": "eyJ...",                                  │
    │       "user": { "id": 1, "nombre": "...", ... }            │
    │     }                                                       │
    └─────────────────────────────────────────────────────────────┘
    """

    @classmethod
    def get_token(cls, user):
        """
        Personaliza el PAYLOAD (contenido) del token JWT.

        El token JWT tiene 3 partes: Header.Payload.Signature
        Por defecto el payload contiene: token_type, exp, iat, jti, user_id
        Aquí le añadimos 'nombre' para que el frontend pueda leerlo sin
        necesidad de hacer otra petición a la API.

        Ejemplo del payload decodificado:
            {
                "token_type": "access",
                "exp": 1778272810,
                "iat": 1778186410,
                "jti": "1e51e25f...",
                "user_id": "1",
                "nombre": "Thomas"        ← Campo personalizado que añadimos
            }
        """
        token = super().get_token(user)
        # Añadimos el nombre al payload del token
        token['nombre'] = user.nombre
        return token

    def validate(self, attrs):
        """
        Se ejecuta cuando el usuario envía sus credenciales (email + password).
        Si las credenciales son válidas, este método:
          1. Genera los tokens (access + refresh) → lo hace super().validate()
          2. Guarda un registro de sesión en la tabla Sesion
          3. Agrega los datos del usuario a la respuesta JSON

        Parámetros:
            attrs: dict con los datos enviados por el frontend
                   → { "email": "...", "password": "..." }

        Retorna:
            dict con la respuesta completa del login
                   → { "access": "...", "refresh": "...", "user": {...} }
        """
        # super().validate() hace la verificación de credenciales
        # y genera los tokens. Si las credenciales son incorrectas,
        # lanza una excepción y nunca se ejecuta el código de abajo.
        # self.user se asigna automáticamente al usuario autenticado.
        data = super().validate(attrs)

        # --- Persistencia de sesión en la base de datos ---
        # Creamos un registro en la tabla 'Sesion' para:
        #   - Saber cuántas sesiones activas tiene un usuario
        #   - Auditoría de accesos (quién se conectó y cuándo)
        #   - Posibilidad futura de cerrar sesiones remotamente
        Sesion.objects.create(
            usuario=self.user,
            token=data['access'],
            # La expiración debe coincidir con ACCESS_TOKEN_LIFETIME en settings.py (1 día)
            expira_en=timezone.now() + timedelta(days=1)
        )

        # --- Datos del usuario para el frontend ---
        # Agregamos un objeto 'user' a la respuesta para que el frontend
        # tenga los datos del perfil inmediatamente después del login,
        # sin necesidad de hacer otra petición a /api/usuarios/lista/{id}/
        data['user'] = {
            'id': self.user.id_usuario,
            'nombre': self.user.nombre,
            'email': self.user.email,
            'foto_perfil': self.user.foto_perfil.url if self.user.foto_perfil else None,
        }
        return data
>>>>>>> master
