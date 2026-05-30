"""
Módulo de IA para generación inteligente de mensajes iniciales
Analiza la compatibilidad y gustos compartidos para crear mensajes personalizados
"""

from typing import Optional
from .models import Match, PreguntaEncuesta, RespuestaEncuesta, Usuario


class AIMessageGenerator:
    """Genera mensajes iniciales contextuales basados en análisis de perfil"""

    # Templates de mensajes iniciales basados en compatibilidad
    TEMPLATES_ALTA_COMPATIBILIDAD = [
        "¡Hola {nombre}! Me sorprendió la compatibilidad que encontré contigo en nuestros gustos: {gustos_compartidos}. ¿Qué te parece si conversamos sobre eso?",
        "Hola {nombre}, parece que compartimos algunos intereses fascinantes como {gustos_compartidos}. Me gustaría conocerte mejor.",
        "¡{nombre}! La IA detectó que ambos valoramos {gustos_compartidos}. Creo que tenemos mucho de qué hablar.",
    ]

    TEMPLATES_MEDIA_COMPATIBILIDAD = [
        "Hola {nombre}, la plataforma me sugiere que podríamos tener conversaciones interesantes. ¿De qué te gusta hablar?",
        "Hola {nombre}, me intriga conocer más sobre ti. ¿Cuál es tu pasión principal?",
        "¿Qué tal, {nombre}? Parece que tenemos algunos intereses en común. ¿De cuál te gustaría hablar?",
    ]

    TEMPLATES_BAJA_COMPATIBILIDAD = [
        "Hola {nombre}, la plataforma sugiere que podríamos conocernos. ¿Qué te trae a Synchro?",
        "Hola {nombre}, ¿cuál es tu historia? Me gustaría saber más de ti.",
        "¡Hola {nombre}! Espero poder aprender cosas nuevas de ti.",
    ]

    TEMPLATES_LOCALIDAD = [
        "¡Qué bien! Somos de {ciudad}. ¿Hay algún lugar que te encante en la ciudad?",
        "¡Qué coincidencia! También soy de {ciudad}. ¿Cuál es tu rincón favorito?",
    ]

    TEMPLATES_INTENCION = [
        "Veo que ambos buscamos {intencion}. Creo que es un buen punto de partida.",
        "Excelente, compartimos la intención de {intencion}. Eso nos acerca.",
    ]

    @staticmethod
    def extract_shared_interests(user_a: Usuario, user_b: Usuario) -> list[str]:
        """Extrae los intereses compartidos entre dos usuarios"""
        # Obtener respuestas de ambos usuarios
        respuestas_a = RespuestaEncuesta.objects.filter(usuario=user_a).values_list('respuesta_texto', flat=True)
        respuestas_b = set(RespuestaEncuesta.objects.filter(usuario=user_b).values_list('respuesta_texto', flat=True))
        
        # Palabras clave comunes (simple matching)
        palabras_clave_a = set()
        for respuesta in respuestas_a:
            palabras = respuesta.lower().split()
            palabras_clave_a.update([p for p in palabras if len(p) > 3])
        
        intereses_compartidos = []
        for respuesta_b in respuestas_b:
            palabras_b = respuesta_b.lower().split()
            for palabra in palabras_b:
                if palabra in palabras_clave_a and len(palabra) > 3:
                    intereses_compartidos.append(palabra)
        
        # Remover duplicados y limitar a los 4 principales
        return list(set(intereses_compartidos))[:4]

    @staticmethod
    def extract_hobbies_from_responses(user: Usuario) -> list[str]:
        """Extrae los pasatiempos mencionados en las respuestas"""
        hobbies = []
        respuestas = RespuestaEncuesta.objects.filter(usuario=user).select_related('pregunta')
        
        for resp in respuestas:
            if any(kw in resp.pregunta.texto_pregunta.lower() for kw in ['pasatiempo', 'hobby', 'actividad']):
                # Extraer palabras significativas
                palabras = resp.respuesta_texto.lower().split()
                hobbies.extend([p for p in palabras if len(p) > 3])
        
        return list(set(hobbies))[:3]

    @staticmethod
    def get_compatibility_level(compatibility_score: float) -> str:
        """Clasifica el nivel de compatibilidad"""
        if compatibility_score >= 80:
            return "very_high"
        elif compatibility_score >= 65:
            return "high"
        elif compatibility_score >= 50:
            return "medium"
        elif compatibility_score >= 35:
            return "low"
        else:
            return "very_low"

    @classmethod
    def generate_initial_message(
        cls,
        user_a: Usuario,
        user_b: Usuario,
        compatibility_score: float,
        explanation: str = ""
    ) -> str:
        """
        Genera un mensaje inicial inteligente basado en compatibilidad y perfil
        
        Args:
            user_a: Usuario que inicia la conversación
            user_b: Usuario que recibe el mensaje
            compatibility_score: Puntuación de compatibilidad (0-100)
            explanation: Explicación de la afinidad
            
        Returns:
            Mensaje inicial personalizado
        """
        mensaje = ""
        
        # Seleccionar template basado en compatibilidad
        nivel = cls.get_compatibility_level(compatibility_score)
        
        if nivel == "very_high":
            templates = cls.TEMPLATES_ALTA_COMPATIBILIDAD
        elif nivel in ["high", "medium"]:
            templates = cls.TEMPLATES_MEDIA_COMPATIBILIDAD
        else:
            templates = cls.TEMPLATES_BAJA_COMPATIBILIDAD
        
        # Usar el primer template disponible
        template_base = templates[0] if templates else "¡Hola {nombre}! Me gustaría conocerte mejor."
        
        # Reemplazar placeholders
        gustos = cls.extract_shared_interests(user_a, user_b)
        gustos_str = ', '.join(gustos) if gustos else "algunas cosas interesantes"
        
        mensaje = template_base.format(
            nombre=user_b.nombre,
            gustos_compartidos=gustos_str
        )
        
        # Agregar contexto de localidad si es relevante
        if (user_a.ciudad and user_b.ciudad and 
            user_a.ciudad.lower() == user_b.ciudad.lower()):
            ciudad_template = cls.TEMPLATES_LOCALIDAD[0]
            mensaje += " " + ciudad_template.format(ciudad=user_b.ciudad)
        
        # Agregar contexto de intención si coinciden
        if (user_a.intencion_busqueda and user_b.intencion_busqueda and
            user_a.intencion_busqueda == user_b.intencion_busqueda):
            intencion_template = cls.TEMPLATES_INTENCION[0]
            mensaje += " " + intencion_template.format(
                intencion=user_b.intencion_busqueda.nombre.lower()
            )
        
        return mensaje

    @classmethod
    def generate_match_suggestion(cls, match: "Match") -> str:
        """
        Genera una sugerencia de conversación basada en el match
        
        Args:
            match: Objeto Match con la compatibilidad
            
        Returns:
            Sugerencia de conversación
        """
        user_a = match.usuario1
        user_b = match.usuario2
        
        sugerencias = [
            f"Pregunta sobre los gustos compartidos que la IA detectó: {', '.join(cls.extract_shared_interests(user_a, user_b)[:3])}",
            "Comienza preguntando qué lo/la trae a Synchro y qué espera encontrar.",
            "Propón una actividad basada en los intereses que mencionaron en la encuesta.",
        ]
        
        # Seleccionar sugerencia basada en compatibilidad
        if match.compatibilidad >= 75:
            return sugerencias[0] if cls.extract_shared_interests(user_a, user_b) else sugerencias[1]
        elif match.compatibilidad >= 50:
            return sugerencias[1]
        else:
            return sugerencias[2]
