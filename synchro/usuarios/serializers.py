from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id_usuario', 'email', 'nombre', 'fecha_nacimiento',
            'ciudad', 'intencion_busqueda', 'genero', 'foto_perfil',
            'idioma_preferido', 'tema_preferido', 'bio_ai'
        ]
        read_only_fields = ['id_usuario']

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = Usuario
        fields = ['email', 'nombre', 'password']

    def create(self, validated_data):
        # We use create_user so the password gets hashed correctly
        user = Usuario.objects.create_user(
            email=validated_data['email'],
            nombre=validated_data['nombre'],
            password=validated_data['password'],
            # we can pass username as email to satisfy abstractuser if we really need to,
            # but we overrode username to allow blank/null. Let's provide it anyway.
            username=validated_data['email']
        )
        return user

