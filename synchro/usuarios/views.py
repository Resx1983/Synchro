from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .matching import (
    compare_users,
    ensure_match_message,
    ensure_user_embedding,
    find_best_match,
    get_or_create_match,
    user_matches,
)
from .models import IntencionBusqueda, Match, Mensaje, PreguntaEncuesta, RespuestaEncuesta, Usuario
from .serializers import (
    IntencionBusquedaSerializer,
    MatchSerializer,
    MensajeSerializer,
    PreguntaEncuestaSerializer,
    RegistroUsuarioSerializer,
    RespuestasEncuestaBulkSerializer,
    UsuarioSerializer,
)


class RegistroView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistroUsuarioSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Usuario.objects.filter(is_active=True).select_related('intencion_busqueda')


class IntencionBusquedaView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        serializer = IntencionBusquedaSerializer(IntencionBusqueda.objects.all().order_by('id_intencion'), many=True)
        return Response(serializer.data)


class PreguntasEncuestaView(APIView):
    # Questions are public (read-only) so the frontend can render the survey
    # even if the user has no valid token in the browser yet.
    permission_classes = (AllowAny,)

    def get(self, request):
        preguntas = PreguntaEncuesta.objects.all().order_by('orden', 'id_pregunta')
        serializer = PreguntaEncuestaSerializer(preguntas, many=True)

        respuestas_list = []
        encuesta_completa = False
        # If the user is authenticated, include their saved answers
        if request.user and request.user.is_authenticated:
            respuestas_qs = RespuestaEncuesta.objects.filter(usuario=request.user)
            respuestas_list = list(respuestas_qs.values('pregunta_id', 'respuesta_texto'))
            encuesta_completa = preguntas.count() > 0 and respuestas_qs.count() >= preguntas.count()

        return Response({
            'preguntas': serializer.data,
            'respuestas': respuestas_list,
            'encuesta_completa': encuesta_completa,
        })


class RespuestasEncuestaView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        respuestas = RespuestaEncuesta.objects.filter(usuario=request.user).select_related('pregunta').order_by('pregunta__orden')
        data = [
            {
                'id_respuesta': respuesta.id_respuesta,
                'pregunta': respuesta.pregunta.id_pregunta,
                'respuesta_texto': respuesta.respuesta_texto,
                'texto_pregunta': respuesta.pregunta.texto_pregunta,
            }
            for respuesta in respuestas
        ]
        return Response({'respuestas': data})

    def post(self, request):
        serializer = RespuestasEncuestaBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        preguntas_por_id = {
            pregunta.id_pregunta: pregunta
            for pregunta in PreguntaEncuesta.objects.filter(id_pregunta__in=[item['pregunta_id'] for item in serializer.validated_data['respuestas']])
        }
        respuestas_guardadas = []
        for item in serializer.validated_data['respuestas']:
            pregunta = preguntas_por_id.get(item['pregunta_id'])
            if not pregunta:
                continue
            respuesta, _ = RespuestaEncuesta.objects.update_or_create(
                usuario=request.user,
                pregunta=pregunta,
                defaults={'respuesta_texto': item['respuesta_texto']},
            )
            respuestas_guardadas.append(respuesta)

        embedding = ensure_user_embedding(request.user)
        return Response({
            'status': 'success',
            'message': 'Encuesta guardada correctamente.',
            'respuestas_guardadas': len(respuestas_guardadas),
            'embedding_perfil': embedding,
        }, status=status.HTTP_200_OK)


class MatchEmpezarView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        responses_count = RespuestaEncuesta.objects.filter(usuario=request.user).count()
        if responses_count == 0:
            return Response(
                {'detail': 'Primero completa la encuesta para calcular tus coincidencias.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        candidates = find_best_match(request.user)
        if not candidates:
            return Response(
                {'detail': 'Todavía no hay suficientes perfiles compatibles para generar un match.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        candidate, insight = candidates[0]
        match, created = get_or_create_match(request.user, candidate, insight)
        match_serializer = MatchSerializer(match, context={'request': request})
        return Response({
            'status': 'success',
            'created': created,
            'match': match_serializer.data,
            'message': f"Match generado con {candidate.nombre} ({insight.score}%).",
        }, status=status.HTTP_200_OK)


class MatchListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        matches = user_matches(request.user).select_related('usuario1', 'usuario2')
        serializer = MatchSerializer(matches, many=True, context={'request': request})
        return Response({'matches': serializer.data})


class MatchDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_match(self, match_id, user):
        return get_object_or_404(
            Match.objects.select_related('usuario1', 'usuario2').only(
                'id_match', 'usuario1_id', 'usuario2_id', 'compatibilidad',
                'explicacion_afinidad', 'fecha_match', 'fecha_actualizacion',
                'sugerencia_ia', 'estado', 'usuario1__nombre', 'usuario1__ciudad',
                'usuario1__foto_perfil', 'usuario2__nombre', 'usuario2__ciudad',
                'usuario2__foto_perfil'
            ),
            pk=match_id,
        )

    def get(self, request, match_id):
        match = self.get_match(match_id, request.user)
        if request.user not in (match.usuario1, match.usuario2):
            return Response({'detail': 'No tienes acceso a este match.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = MatchSerializer(match, context={'request': request})
        return Response(serializer.data)


class MensajesMatchView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_match(self, match_id):
        return get_object_or_404(Match.objects.select_related('usuario1', 'usuario2'), pk=match_id)

    def get(self, request, match_id):
        match = self.get_match(match_id)
        if request.user not in (match.usuario1, match.usuario2):
            return Response({'detail': 'No tienes acceso a este chat.'}, status=status.HTTP_403_FORBIDDEN)
        after_id = request.query_params.get('after_id')
        mensajes = Mensaje.objects.filter(match=match).select_related('remitente', 'destinatario').only(
            'id_mensaje', 'match_id', 'remitente_id', 'destinatario_id', 'mensaje', 'fecha_mensaje', 'tipo_mensaje', 'estado_leido',
            'remitente__id_usuario', 'remitente__nombre', 'destinatario__id_usuario', 'destinatario__nombre',
        ).order_by('fecha_mensaje')
        if after_id and after_id.isdigit():
            mensajes = mensajes.filter(id_mensaje__gt=int(after_id))
        serializer = MensajeSerializer(mensajes, many=True)
        return Response({'match_id': match.id_match, 'mensajes': serializer.data})

    def post(self, request, match_id):
        match = self.get_match(match_id)
        if request.user not in (match.usuario1, match.usuario2):
            return Response({'detail': 'No tienes acceso a este chat.'}, status=status.HTTP_403_FORBIDDEN)

        message_text = (request.data.get('mensaje') or '').strip()
        if not message_text:
            return Response({'detail': 'El mensaje no puede estar vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        recipient = match.usuario2 if request.user == match.usuario1 else match.usuario1
        message = ensure_match_message(match, request.user, recipient, message_text)
        serializer = MensajeSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InicioView(TemplateView):
    template_name = 'usuarios/inicio.html'


class LoginFrontendView(TemplateView):
    template_name = 'usuarios/login.html'


class RegistroFrontendView(TemplateView):
    template_name = 'usuarios/registro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['intenciones'] = IntencionBusqueda.objects.all().order_by('nombre')
        return context


class EncuestaFrontendView(TemplateView):
    template_name = 'usuarios/encuesta.html'


class MatchesFrontendView(TemplateView):
    template_name = 'usuarios/matches.html'


class ChatFrontendView(TemplateView):
    template_name = 'usuarios/chat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = get_object_or_404(
            Match.objects.select_related('usuario1', 'usuario2').only(
                'id_match', 'usuario1_id', 'usuario2_id', 'compatibilidad', 'explicacion_afinidad',
                'estado', 'usuario1__nombre', 'usuario1__ciudad', 'usuario1__foto_perfil',
                'usuario2__nombre', 'usuario2__ciudad', 'usuario2__foto_perfil'
            ),
            pk=kwargs.get('match_id')
        )
        context['match_id'] = match.id_match
        context['match'] = match
        context['otro_usuario'] = match.usuario2 if self.request.user == match.usuario1 else match.usuario1
        return context

