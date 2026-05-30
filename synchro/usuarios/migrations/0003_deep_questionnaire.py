from django.db import migrations


PREGUNTAS_PROFUNDAS = [
    # PERSONALIDAD (11-20)
    ('¿Cómo describirías tu personalidad en tres palabras?', 'How would you describe your personality in three words?', '🧠', 11),
    ('¿Eres más introvertido o extrovertido?', 'Are you more introverted or extroverted?', '👤', 12),
    ('¿Qué te asusta más en las relaciones personales?', 'What scares you the most in personal relationships?', '😨', 13),
    ('¿Cuál es tu mayor fortaleza emocional?', 'What is your greatest emotional strength?', '💪', 14),
    ('¿Cómo manejas el conflicto o la desacuerdo?', 'How do you handle conflict or disagreement?', '⚡', 15),
    ('¿Qué tipo de persona eres: espontánea o planificadora?', 'What type of person are you: spontaneous or planner?', '📋', 16),
    ('¿Cuál es tu mayor inseguridad?', 'What is your biggest insecurity?', '🔐', 17),
    ('¿Cómo te describes en una cita importante?', 'How do you describe yourself on an important date?', '💫', 18),
    ('¿Qué tanto te importa la opinión de los demás?', 'How much do you care about others\' opinions?', '🎭', 19),
    ('¿Cómo lidias con la soledad?', 'How do you deal with loneliness?', '🌧️', 20),
    
    # VALORES Y FILOSOFÍA DE VIDA (21-30)
    ('¿Cuál es tu mayor motivación en la vida?', 'What is your biggest motivation in life?', '🎯', 21),
    ('¿Crees que el dinero compra felicidad?', 'Do you think money buys happiness?', '💰', 22),
    ('¿Cuál es el valor más importante para ti?', 'What is the most important value for you?', '✨', 23),
    ('¿Qué significa el éxito para ti?', 'What does success mean to you?', '🏆', 24),
    ('¿Eres religioso o espiritual?', 'Are you religious or spiritual?', '🙏', 25),
    ('¿Cuál es tu mayor sueño a largo plazo?', 'What is your biggest long-term dream?', '🌟', 26),
    ('¿Cómo contribuyes al mundo?', 'How do you contribute to the world?', '🌍', 27),
    ('¿Qué principios nunca comprometerías?', 'What principles would you never compromise?', '⚖️', 28),
    ('¿Cómo defines una vida significativa?', 'How do you define a meaningful life?', '📖', 29),
    ('¿Qué te enseñaron tus padres que nunca olvidarás?', 'What did your parents teach you that you\'ll never forget?', '👨‍👩‍👧', 30),
    
    # ESTILO DE VIDA Y RUTINA (31-40)
    ('¿Cuál es tu rutina diaria ideal?', 'What is your ideal daily routine?', '⏰', 31),
    ('¿Cuántas horas de sueño necesitas?', 'How many hours of sleep do you need?', '😴', 32),
    ('¿Eres de las personas que hace ejercicio regularmente?', 'Are you someone who exercises regularly?', '🏃', 33),
    ('¿Cómo describirías tu relación con la comida?', 'How would you describe your relationship with food?', '🍽️', 34),
    ('¿Cuáles son tus pasatiempos favoritos?', 'What are your favorite hobbies?', '🎨', 35),
    ('¿Qué red social usas más y por qué?', 'What social media do you use most and why?', '📱', 36),
    ('¿Te gusta viajar? ¿A dónde te gustaría ir?', 'Do you like to travel? Where would you like to go?', '✈️', 37),
    ('¿Eres más de películas, libros o series?', 'Are you more into movies, books, or series?', '📺', 38),
    ('¿Cómo pasas tu tiempo libre generalmente?', 'How do you usually spend your free time?', '🎯', 39),
    ('¿Te gusta la naturaleza? ¿Acampar o aventuras?', 'Do you like nature? Camping or adventures?', '⛺', 40),
    
    # RELACIONES E INTIMIDAD (41-50)
    ('¿Qué buscas realmente en una pareja?', 'What do you really look for in a partner?', '💑', 41),
    ('¿Cuál fue tu relación más significativa?', 'What was your most meaningful relationship?', '💔', 42),
    ('¿Cómo sabes que te enamoras de alguien?', 'How do you know when you fall in love with someone?', '😍', 43),
    ('¿Qué cosa más pequeña valoras en alguien?', 'What small thing do you most value in someone?', '💝', 44),
    ('¿Te importa la química o la compatibilidad?', 'Do you care about chemistry or compatibility?', '⚗️', 45),
    ('¿Cómo es tu forma de demostrar afecto?', 'What is your way of showing affection?', '🤗', 46),
    ('¿Qué dealbreaker tienes en una relación?', 'What is your dealbreaker in a relationship?', '🚫', 47),
    ('¿Cómo ves el futuro con alguien especial?', 'How do you envision the future with someone special?', '🌅', 48),
    ('¿Eres celoso o confías fácilmente?', 'Are you jealous or do you trust easily?', '👀', 49),
    ('¿Qué edad tienes y qué edad buscas?', 'What age are you and what age are you looking for?', '🎂', 50),
    
    # METAS Y FUTURO (51-60)
    ('¿Dónde te ves en 5 años?', 'Where do you see yourself in 5 years?', '🔮', 51),
    ('¿Quieres tener hijos? ¿Cuántos?', 'Do you want to have children? How many?', '👶', 52),
    ('¿Cuál es tu carrera o profesión actual?', 'What is your current career or profession?', '💼', 53),
    ('¿Te gusta tu trabajo?', 'Do you like your job?', '😊', 54),
    ('¿Cómo de importante es la estabilidad económica?', 'How important is financial stability?', '📊', 55),
    ('¿Quieres vivir en la ciudad o el campo?', 'Do you want to live in the city or countryside?', '🏙️', 56),
    ('¿Tienes planes de educación continua?', 'Do you have plans for continuous education?', '📚', 57),
    ('¿Cuál es tu meta más importante ahora?', 'What is your most important goal right now?', '🎯', 58),
    ('¿Te gustaría mudarte a otro país?', 'Would you like to move to another country?', '🌏', 59),
    ('¿Qué legado quieres dejar?', 'What legacy do you want to leave?', '🕊️', 60),
]


def seed_deep_questions(apps, schema_editor):
    PreguntaEncuesta = apps.get_model('usuarios', 'PreguntaEncuesta')
    
    for texto_pregunta, texto_pregunta_en, icono, orden in PREGUNTAS_PROFUNDAS:
        PreguntaEncuesta.objects.get_or_create(
            texto_pregunta=texto_pregunta,
            defaults={
                'texto_pregunta_en': texto_pregunta_en,
                'icono': icono,
                'orden': orden,
            },
        )


def unseed_deep_questions(apps, schema_editor):
    PreguntaEncuesta = apps.get_model('usuarios', 'PreguntaEncuesta')
    PreguntaEncuesta.objects.filter(orden__gte=11).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_seed_questionnaire'),
    ]

    operations = [
        migrations.RunPython(seed_deep_questions, reverse_code=unseed_deep_questions),
    ]
