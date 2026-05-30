from django.db import migrations


INTENCIONES = [
    ('Conocer personas', 'Meet people'),
    ('Amistad', 'Friendship'),
    ('Pareja', 'Dating'),
    ('Ambos', 'Both'),
]


PREGUNTAS = [
    ('¿Qué actividad te hace sentir más tú?', 'What activity makes you feel most like yourself?', '⭐', 1),
    ('¿Prefieres planes tranquilos o experiencias intensas?', 'Do you prefer calm plans or intense experiences?', '✨', 2),
    ('¿Qué música escuchas cuando quieres conectar con alguien?', 'What music do you listen to when you want to connect with someone?', '🎵', 3),
    ('¿Qué valor es imprescindible para ti en una relación?', 'What value is essential to you in a relationship?', '💬', 4),
    ('¿Cómo describes tu fin de semana ideal?', 'How do you describe your ideal weekend?', '🌙', 5),
    ('¿Qué te atrae más de una persona nueva?', 'What attracts you most about a new person?', '🔥', 6),
    ('¿Te gusta conversar mucho o compartir silencios cómodos?', 'Do you like talking a lot or sharing comfortable silences?', '☕', 7),
    ('¿Qué pasatiempo te gustaría compartir con otra persona?', 'What hobby would you like to share with someone else?', '🎮', 8),
    ('¿Qué comida o bebida te representa?', 'What food or drink represents you?', '🍓', 9),
    ('¿Qué te gustaría encontrar en Synchro?', 'What would you like to find in Synchro?', '💞', 10),
]


def seed_data(apps, schema_editor):
    IntencionBusqueda = apps.get_model('usuarios', 'IntencionBusqueda')
    PreguntaEncuesta = apps.get_model('usuarios', 'PreguntaEncuesta')

    for nombre, nombre_en in INTENCIONES:
        IntencionBusqueda.objects.get_or_create(nombre=nombre, defaults={'nombre_en': nombre_en})

    for texto_pregunta, texto_pregunta_en, icono, orden in PREGUNTAS:
        PreguntaEncuesta.objects.get_or_create(
            texto_pregunta=texto_pregunta,
            defaults={
                'texto_pregunta_en': texto_pregunta_en,
                'icono': icono,
                'orden': orden,
            },
        )


def unseed_data(apps, schema_editor):
    IntencionBusqueda = apps.get_model('usuarios', 'IntencionBusqueda')
    PreguntaEncuesta = apps.get_model('usuarios', 'PreguntaEncuesta')
    IntencionBusqueda.objects.filter(nombre__in=[item[0] for item in INTENCIONES]).delete()
    PreguntaEncuesta.objects.filter(texto_pregunta__in=[item[0] for item in PREGUNTAS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_code=unseed_data),
    ]