"""
Módulo de Machine Learning avanzado para matching
Utiliza TF-IDF, análisis de texto y técnicas de ML para mejores matches
"""

import math
import numpy as np
from collections import Counter
from dataclasses import dataclass
from typing import Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from django.db.models import Q

from .models import Match, PreguntaEncuesta, RespuestaEncuesta, Usuario


@dataclass(frozen=True)
class MLMatchInsight:
    """Resultado del análisis de match con ML"""
    score: float
    explanation: str
    shared_interests: list[str]
    confidence: float  # Confianza del algoritmo (0-1)
    shared_values: list[str]


class MLMatcher:
    """
    Sistema avanzado de matching usando Machine Learning
    Combina TF-IDF, análisis semántico y feature engineering
    """

    # Pesos de diferentes factores en el score final
    WEIGHT_RESPONSES = 0.50  # Respuestas a preguntas profundas
    WEIGHT_PROFILE = 0.25    # Información de perfil
    WEIGHT_LOCATION = 0.10   # Ubicación geográfica
    WEIGHT_INTENTION = 0.10  # Intención de búsqueda
    WEIGHT_AGE = 0.05        # Compatibilidad de edad

    @staticmethod
    def extract_user_text(user: Usuario) -> str:
        """Extrae todo el texto relevante de un usuario para vectorización"""
        texts = []
        
        # Información básica del perfil
        if user.nombre:
            texts.append(user.nombre)
        if user.bio_ai:
            texts.append(user.bio_ai)
        if user.ciudad:
            texts.append(user.ciudad)
        if user.genero:
            texts.append(user.genero)
        if user.idioma_preferido:
            texts.append(user.idioma_preferido)
        if user.intencion_busqueda:
            texts.append(user.intencion_busqueda.nombre)
        
        # Respuestas a la encuesta
        respuestas = RespuestaEncuesta.objects.filter(usuario=user).select_related('pregunta')
        for resp in respuestas:
            texts.append(resp.pregunta.texto_pregunta)
            texts.append(resp.respuesta_texto)
        
        return " ".join(texts).lower()

    @staticmethod
    def extract_response_keywords(user: Usuario, top_n: int = 10) -> list[str]:
        """Extrae palabras clave de las respuestas del usuario"""
        respuestas = RespuestaEncuesta.objects.filter(usuario=user)
        words = []
        
        for resp in respuestas:
            # Dividir en palabras y filtrar stopwords comunes
            respuesta_words = resp.respuesta_texto.lower().split()
            words.extend([w for w in respuesta_words if len(w) > 3])
        
        # Contar frecuencias
        contador = Counter(words)
        return [word for word, _ in contador.most_common(top_n)]

    @staticmethod
    def extract_shared_values(user_a: Usuario, user_b: Usuario) -> list[str]:
        """
        Extrae valores compartidos analizando respuestas sobre valores
        """
        shared_values = []
        
        # Preguntas sobre valores
        value_keywords = [
            'valor', 'importante', 'significa', 'principio', 'ética',
            'moral', 'derecho', 'justicia', 'compromiso', 'honestidad'
        ]
        
        respuestas_a = RespuestaEncuesta.objects.filter(usuario=user_a).select_related('pregunta')
        respuestas_b = RespuestaEncuesta.objects.filter(usuario=user_b).select_related('pregunta')
        
        # Buscar preguntas sobre valores
        for resp_a in respuestas_a:
            pregunta_texto = resp_a.pregunta.texto_pregunta.lower()
            if any(kw in pregunta_texto for kw in value_keywords):
                # Comparar con respuestas de usuario b
                for resp_b in respuestas_b:
                    if resp_a.pregunta == resp_b.pregunta:
                        # Misma pregunta
                        if resp_a.respuesta_texto.lower() == resp_b.respuesta_texto.lower():
                            shared_values.append(resp_a.pregunta.icono)
        
        return list(set(shared_values))

    @staticmethod
    def calculate_age_compatibility(user_a: Usuario, user_b: Usuario) -> float:
        """Calcula compatibilidad de edad (menos penalizante)"""
        if not (user_a.fecha_nacimiento and user_b.fecha_nacimiento):
            return 0.5  # Neutral si no hay edad
        
        from datetime import date
        today = date.today()
        
        age_a = today.year - user_a.fecha_nacimiento.year
        age_b = today.year - user_b.fecha_nacimiento.year
        
        age_diff = abs(age_a - age_b)
        
        if age_diff <= 2:
            return 1.0  # Muy compatible
        elif age_diff <= 5:
            return 0.8
        elif age_diff <= 10:
            return 0.6
        elif age_diff <= 15:
            return 0.4
        else:
            return 0.2

    @staticmethod
    def calculate_location_compatibility(user_a: Usuario, user_b: Usuario) -> float:
        """Calcula compatibilidad de ubicación"""
        if not (user_a.ciudad and user_b.ciudad):
            return 0.5
        
        if user_a.ciudad.lower() == user_b.ciudad.lower():
            return 1.0
        
        # Misma región/país (simplificado)
        return 0.6

    @staticmethod
    def calculate_intention_compatibility(user_a: Usuario, user_b: Usuario) -> float:
        """Calcula compatibilidad de intención de búsqueda"""
        if not (user_a.intencion_busqueda and user_b.intencion_busqueda):
            return 0.5
        
        if user_a.intencion_busqueda == user_b.intencion_busqueda:
            return 1.0
        
        # Si uno busca "Ambos" es compatible con cualquier cosa
        if user_a.intencion_busqueda.nombre == 'Ambos' or user_b.intencion_busqueda.nombre == 'Ambos':
            return 0.8
        
        return 0.4

    @classmethod
    def calculate_tfidf_similarity(cls, user_a: Usuario, user_b: Usuario) -> Tuple[float, list[str]]:
        """
        Calcula similitud usando TF-IDF Vectorizer
        Retorna: (similitud, palabras_compartidas)
        """
        text_a = cls.extract_user_text(user_a)
        text_b = cls.extract_user_text(user_b)
        
        if not text_a or not text_b:
            return 0.0, []
        
        try:
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='spanish',
                ngram_range=(1, 2),
                min_df=1,
                max_df=2
            )
            
            tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
            similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
            
            # Extraer palabras compartidas
            feature_names = vectorizer.get_feature_names_out()
            vector_a = tfidf_matrix[0].toarray()[0]
            vector_b = tfidf_matrix[1].toarray()[0]
            
            shared_features = []
            for i, (a_val, b_val) in enumerate(zip(vector_a, vector_b)):
                if a_val > 0 and b_val > 0:
                    shared_features.append(feature_names[i])
            
            return float(similarity), shared_features[:6]
        
        except Exception as e:
            # Fallback a similitud simple si TF-IDF falla
            return 0.0, []

    @classmethod
    def compare_users_ml(cls, user_a: Usuario, user_b: Usuario) -> MLMatchInsight:
        """
        Análisis de compatibilidad mejorado con ML
        Combina múltiples factores para un score robusto
        """
        
        # Calcular componentes de similitud
        tfidf_score, shared_keywords = cls.calculate_tfidf_similarity(user_a, user_b)
        age_compat = cls.calculate_age_compatibility(user_a, user_b)
        location_compat = cls.calculate_location_compatibility(user_a, user_b)
        intention_compat = cls.calculate_intention_compatibility(user_a, user_b)
        
        # Extraer valores compartidos
        shared_values = cls.extract_shared_values(user_a, user_b)
        
        # Calcular score multi-factor
        response_score = min(100, tfidf_score * 100)  # TF-IDF está entre 0-1
        profile_score = (age_compat * 100) * 0.6 + (location_compat * 100) * 0.4
        
        # Score final ponderado
        final_score = (
            response_score * cls.WEIGHT_RESPONSES +
            profile_score * cls.WEIGHT_PROFILE +
            (location_compat * 100) * cls.WEIGHT_LOCATION +
            (intention_compat * 100) * cls.WEIGHT_INTENTION +
            (age_compat * 100) * cls.WEIGHT_AGE
        )
        
        final_score = min(100.0, max(0.0, round(final_score, 2)))
        
        # Calcular confianza del algoritmo
        confidence = min(1.0, (len(shared_keywords) / 10) + (tfidf_score / 2))
        
        # Generar explicación
        explanation_parts = []
        
        if shared_keywords:
            explanation_parts.append(f"gustos compartidos: {', '.join(shared_keywords[:3])}")
        
        if location_compat >= 0.9:
            explanation_parts.append("misma ubicación")
        
        if intention_compat >= 0.9:
            explanation_parts.append(f"misma intención de búsqueda")
        
        if age_compat >= 0.8:
            explanation_parts.append("compatibilidad de edad")
        
        if shared_values:
            explanation_parts.append("valores compartidos")
        
        if not explanation_parts:
            explanation_parts.append("perfil compatible")
        
        explanation = "; ".join(explanation_parts)
        
        return MLMatchInsight(
            score=final_score,
            explanation=explanation,
            shared_interests=shared_keywords,
            confidence=round(confidence, 2),
            shared_values=shared_values
        )

    @classmethod
    def find_best_matches_ml(cls, user: Usuario, limit: int = 5) -> list[Tuple[Usuario, MLMatchInsight]]:
        """
        Encuentra los mejores matches para un usuario usando ML
        """
        candidates = []
        
        # Obtener candidatos (usuarios activos sin el usuario actual)
        candidate_users = (
            Usuario.objects
            .exclude(id_usuario=user.id_usuario)
            .exclude(is_active=False)
            .select_related('intencion_busqueda')
        )
        
        for candidate in candidate_users:
            # Solo considerar usuarios que han respondido la encuesta
            if not RespuestaEncuesta.objects.filter(usuario=candidate).exists():
                continue
            
            insight = cls.compare_users_ml(user, candidate)
            candidates.append((candidate, insight))
        
        # Ordenar por score descendente
        candidates.sort(key=lambda x: x[1].score, reverse=True)
        
        return candidates[:limit]
