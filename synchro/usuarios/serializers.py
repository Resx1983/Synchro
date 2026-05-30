from rest_framework import serializers
from .models import (
    Usuario,
    IntencionBusqueda,
    PreguntaEncuesta,
    RespuestaEncuesta,
    Match,
    Mensaje,
)


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id_usuario', 'email', 'nombre', 'fecha_nacimiento',
            'ciudad', 'intencion_busqueda', 'genero', 'foto_perfil',
            'idioma_preferido', 'tema_preferido', 'bio_ai', 'embedding_perfil'
        ]
        read_only_fields = ['id_usuario']


class IntencionBusquedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntencionBusqueda
        fields = ['id_intencion', 'nombre', 'nombre_en']


class PreguntaEncuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreguntaEncuesta
        fields = ['id_pregunta', 'texto_pregunta', 'texto_pregunta_en', 'icono', 'orden']


class RespuestaEncuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaEncuesta
        fields = ['id_respuesta', 'usuario', 'pregunta', 'respuesta_texto']
        read_only_fields = ['id_respuesta', 'usuario']


class RespuestaEncuestaCreateSerializer(serializers.Serializer):
    pregunta_id = serializers.IntegerField()
    respuesta_texto = serializers.CharField()


class RespuestasEncuestaBulkSerializer(serializers.Serializer):
    respuestas = RespuestaEncuestaCreateSerializer(many=True)


class MensajeSerializer(serializers.ModelSerializer):
    remitente_nombre = serializers.CharField(source='remitente.nombre', read_only=True)
    destinatario_nombre = serializers.CharField(source='destinatario.nombre', read_only=True)

    class Meta:
        model = Mensaje
        fields = [
            'id_mensaje', 'match', 'remitente', 'remitente_nombre',
            'destinatario', 'destinatario_nombre', 'mensaje', 'fecha_mensaje',
            'tipo_mensaje', 'estado_leido'
        ]
        read_only_fields = ['id_mensaje', 'fecha_mensaje', 'remitente_nombre', 'destinatario_nombre']


class MatchSerializer(serializers.ModelSerializer):
    usuario1_nombre = serializers.CharField(source='usuario1.nombre', read_only=True)
    usuario2_nombre = serializers.CharField(source='usuario2.nombre', read_only=True)
    otro_usuario = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            'id_match', 'usuario1', 'usuario2', 'usuario1_nombre', 'usuario2_nombre',
            'otro_usuario', 'compatibilidad', 'explicacion_afinidad', 'fecha_match',
            'fecha_actualizacion', 'sugerencia_ia', 'estado'
        ]
        read_only_fields = [
            'id_match', 'usuario1_nombre', 'usuario2_nombre', 'otro_usuario',
            'compatibilidad', 'explicacion_afinidad', 'fecha_match', 'fecha_actualizacion',
            'sugerencia_ia', 'estado'
        ]

    def get_otro_usuario(self, obj):
        request = self.context.get('request')
        request_user = request.user if request else None
        other = obj.usuario2 if request_user and request_user == obj.usuario1 else obj.usuario1
        return {
            'id_usuario': other.id_usuario,
            'nombre': other.nombre,
            'email': other.email,
            'ciudad': other.ciudad,
            'foto_perfil': other.foto_perfil.url if other.foto_perfil else None,
        }


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    ciudad = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    genero = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    intencion_busqueda = serializers.PrimaryKeyRelatedField(
        queryset=IntencionBusqueda.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Usuario
        fields = ['email', 'nombre', 'password', 'ciudad', 'genero', 'fecha_nacimiento', 'intencion_busqueda']

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            email=validated_data['email'],
            nombre=validated_data['nombre'],
            password=validated_data['password'],
            username=validated_data['email']
        )
        user.ciudad = validated_data.get('ciudad')
        user.genero = validated_data.get('genero')
        user.fecha_nacimiento = validated_data.get('fecha_nacimiento')
        user.intencion_busqueda = validated_data.get('intencion_busqueda')
        user.save(update_fields=['ciudad', 'genero', 'fecha_nacimiento', 'intencion_busqueda'])
        return user

