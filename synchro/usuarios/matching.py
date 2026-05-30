from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

from django.db.models import Q

from .models import Match, Mensaje, PreguntaEncuesta, RespuestaEncuesta, Usuario
from .ml_matcher import MLMatcher, MLMatchInsight
from .ai_messaging import AIMessageGenerator

# Usar el sistema ML avanzado por defecto
USE_ML_MATCHING = True

STOPWORDS_ES = {
    'a', 'acá', 'ahí', 'al', 'algo', 'algunas', 'algunos', 'ante', 'antes', 'aquel', 'aquella', 'aquello',
    'aqui', 'aquí', 'así', 'aun', 'aunque', 'bajo', 'cada', 'casi', 'como', 'con', 'contra', 'cual', 'cuales',
    'cualquier', 'cuando', 'de', 'del', 'desde', 'donde', 'dos', 'el', 'ella', 'ellas', 'ellos', 'en', 'entre',
    'era', 'eramos', 'eran', 'es', 'esa', 'esas', 'ese', 'eso', 'esos', 'esta', 'estaba', 'estaban', 'estamos',
    'estan', 'estar', 'este', 'esto', 'estos', 'ha', 'hace', 'hacen', 'hacer', 'hacia', 'han', 'hasta', 'hay',
    'la', 'las', 'lo', 'los', 'más', 'mas', 'me', 'mi', 'mis', 'mucho', 'muy', 'no', 'nos', 'nosotros', 'o',
    'otra', 'otras', 'otro', 'otros', 'para', 'pero', 'por', 'porque', 'que', 'quien', 'quienes', 'se', 'ser',
    'si', 'sin', 'sobre', 'su', 'sus', 'tambien', 'también', 'tan', 'te', 'tiene', 'tienen', 'todo', 'todos',
    'tu', 'tus', 'un', 'una', 'uno', 'unos', 'y', 'ya', 'yo'
}

TOKEN_PATTERN = re.compile(r"[a-záéíóúñü0-9]+", re.IGNORECASE)


@dataclass(frozen=True)
class MatchInsight:
    score: float
    explanation: str
    shared_terms: list[str]


def ml_insight_to_match_insight(ml_insight: MLMatchInsight) -> MatchInsight:
    """Convierte MLMatchInsight a MatchInsight para compatibilidad hacia atrás"""
    return MatchInsight(
        score=ml_insight.score,
        explanation=ml_insight.explanation,
        shared_terms=ml_insight.shared_interests
    )


def _normalize_text(value: str | None) -> str:
    if not value:
        return ''
    normalized = unicodedata.normalize('NFKD', value)
    normalized = normalized.encode('ascii', 'ignore').decode('ascii')
    return normalized.lower()


def tokenize(value: str | None) -> list[str]:
    normalized = _normalize_text(value)
    tokens = [token for token in TOKEN_PATTERN.findall(normalized) if token not in STOPWORDS_ES]
    return tokens


def _feature_counter_from_user(user: Usuario) -> Counter:
    features: list[str] = []
    features.extend(tokenize(user.nombre))
    features.extend(tokenize(user.bio_ai))
    features.extend(tokenize(user.ciudad))
    features.extend(tokenize(user.genero))
    features.extend(tokenize(user.idioma_preferido))
    if user.intencion_busqueda:
        features.extend(tokenize(user.intencion_busqueda.nombre))
        features.extend(tokenize(user.intencion_busqueda.nombre_en))

    responses = RespuestaEncuesta.objects.filter(usuario=user).select_related('pregunta')
    for response in responses:
        features.extend(tokenize(response.pregunta.texto_pregunta))
        features.extend(tokenize(response.respuesta_texto))

    counter = Counter(features)
    if counter:
        total = sum(counter.values())
        for key in list(counter.keys()):
            counter[key] = round(counter[key] / total, 6)
    return counter


def ensure_user_embedding(user: Usuario) -> dict[str, float]:
    embedding = _feature_counter_from_user(user)
    user.embedding_perfil = dict(embedding)
    user.save(update_fields=['embedding_perfil'])
    return dict(embedding)


def _cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0

    common_keys = set(left).intersection(right)
    numerator = sum(left[key] * right[key] for key in common_keys)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def compare_users(left: Usuario, right: Usuario) -> MatchInsight:
    left_embedding = left.embedding_perfil or ensure_user_embedding(left)
    right_embedding = right.embedding_perfil or ensure_user_embedding(right)

    cosine = _cosine_similarity(left_embedding, right_embedding)
    score = cosine * 72.0
    bonuses: list[str] = []

    if left.intencion_busqueda_id and left.intencion_busqueda_id == right.intencion_busqueda_id:
        score += 14.0
        bonuses.append('misma intención de búsqueda')

    if left.ciudad and right.ciudad and _normalize_text(left.ciudad) == _normalize_text(right.ciudad):
        score += 6.0
        bonuses.append('misma ciudad')

    if left.genero and right.genero and _normalize_text(left.genero) == _normalize_text(right.genero):
        score += 4.0

    left_tokens = set(left_embedding.keys())
    right_tokens = set(right_embedding.keys())
    shared_terms = sorted(left_tokens.intersection(right_tokens), key=lambda token: (-left_embedding[token], token))[:6]

    if shared_terms:
        bonuses.append('gustos compartidos: ' + ', '.join(shared_terms[:4]))

    score = max(0.0, min(100.0, round(score, 2)))
    explanation_parts = bonuses[:]
    if not explanation_parts and shared_terms:
        explanation_parts.append('comparten afinidades detectadas por la encuesta')
    if not explanation_parts:
        explanation_parts.append('perfil compatible por similitud semántica')

    return MatchInsight(score=score, explanation='; '.join(explanation_parts), shared_terms=shared_terms)


def build_candidate_queryset(user: Usuario):
    return (
        Usuario.objects.exclude(id_usuario=user.id_usuario)
        .exclude(is_active=False)
        .select_related('intencion_busqueda')
    )


def find_best_match(user: Usuario):
    """
    Encuentra el mejor match para un usuario
    Utiliza ML avanzado si está habilitado
    """
    if USE_ML_MATCHING:
        # Usar sistema ML mejorado
        matches_ml = MLMatcher.find_best_matches_ml(user, limit=10)
        if matches_ml:
            return matches_ml
        else:
            return []
    else:
        # Fallback al sistema original
        ensure_user_embedding(user)
        candidates = []
        for candidate in build_candidate_queryset(user):
            if not RespuestaEncuesta.objects.filter(usuario=candidate).exists() and not candidate.embedding_perfil:
                continue
            insight = compare_users(user, candidate)
            candidates.append((candidate, insight))
        candidates.sort(key=lambda item: item[1].score, reverse=True)
        return candidates


def get_or_create_match(user_a: Usuario, user_b: Usuario, insight):
    """
    Obtiene o crea un match entre dos usuarios
    Genera automáticamente un mensaje inicial si es nuevo
    """
    first, second = sorted((user_a, user_b), key=lambda item: item.id_usuario)
    match, created = Match.objects.get_or_create(
        usuario1=first,
        usuario2=second,
        defaults={
            'compatibilidad': insight.score,
            'explicacion_afinidad': insight.explanation,
            'sugerencia_ia': 'Comienza por los gustos compartidos y mantén una conversación abierta.',
            'estado': 'pendiente',
        },
    )
    if not created:
        # Actualizar scores si ya existe
        match.compatibilidad = insight.score
        match.explicacion_afinidad = insight.explanation
        match.fecha_actualizacion = __import__('django.utils.timezone', fromlist=['now']).now()
        match.save(update_fields=['compatibilidad', 'explicacion_afinidad', 'fecha_actualizacion'])
    else:
        # Generar mensaje inicial automático si es un match nuevo
        try:
            generate_initial_match_message(match, insight)
        except Exception as e:
            # No fallar si hay error en generar mensaje
            pass
    
    return match, created


def generate_initial_match_message(match: Match, insight) -> Mensaje:
    """
    Genera automáticamente un mensaje inicial inteligente cuando se crea un match
    """
    # Determinar quién inicia (el que tiene más respuestas)
    respuestas_u1 = RespuestaEncuesta.objects.filter(usuario=match.usuario1).count()
    respuestas_u2 = RespuestaEncuesta.objects.filter(usuario=match.usuario2).count()
    
    if respuestas_u1 >= respuestas_u2:
        iniciador = match.usuario1
        receptor = match.usuario2
    else:
        iniciador = match.usuario2
        receptor = match.usuario1
    
    # Generar mensaje inteligente
    mensaje_texto = AIMessageGenerator.generate_initial_message(
        user_a=iniciador,
        user_b=receptor,
        compatibility_score=match.compatibilidad,
        explanation=match.explicacion_afinidad
    )
    
    # Crear mensaje de sistema inicial
    mensaje = ensure_match_message(
        match=match,
        sender=iniciador,
        recipient=receptor,
        message_text=mensaje_texto,
        tipo='texto'
    )
    
    return mensaje


def user_matches(user: Usuario):
    return Match.objects.filter(Q(usuario1=user) | Q(usuario2=user)).select_related(
        'usuario1', 'usuario2'
    ).order_by('-fecha_actualizacion')


def ensure_match_message(match: Match, sender: Usuario, recipient: Usuario, message_text: str, tipo: str = 'texto') -> Mensaje:
    return Mensaje.objects.create(
        match=match,
        remitente=sender,
        destinatario=recipient,
        mensaje=message_text,
        tipo_mensaje=tipo,
    )
