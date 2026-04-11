# Synchro - Dating App Backend

Este es el backend del proyecto Synchro, construido con Django y Django REST Framework. 

## Requisitos Previos

- Python 3.10 o superior instalado en el sistema.
- pip y virtualenv.

## Pasos de Instalación

Sigue estos pasos para instalar y ejecutar el proyecto de forma local:

### 1. Clonar o descargar el repositorio
Abre una terminal y navega hasta la carpeta donde deseas instalar el proyecto. Extrae o clona los archivos en este directorio.

### 2. Crear un entorno virtual
Es recomendable usar un entorno virtual para aislar las dependencias del proyecto.
En Windows (Símbolo del sistema o PowerShell):
```bash
python -m venv entorno
```

En Linux o macOS:
```bash
python3 -m venv entorno
```

### 3. Activar el entorno virtual
Activa el entorno antes de instalar las dependencias.

En Windows:
```bash
.\entorno\Scripts\activate
```

En Linux o macOS:
```bash
source entorno/bin/activate
```

### 4. Instalar las dependencias
Una vez activado el entorno, instala los paquetes necesarios definidos en el archivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 5. Aplicar migraciones a la base de datos
Navega a la carpeta donde se encuentra el archivo `manage.py` (carpeta `synchro`) y aplica las migraciones para inicializar la base de datos SQLite3:
```bash
cd synchro
python manage.py migrate
```

### 6. Crear un superusuario (Opcional pero recomendado)
Para poder ingresar al panel de administración de Django, debes crear una cuenta de administrador:
```bash
python manage.py createsuperuser
```
Sigue las instrucciones en la consola para ingresar correo electrónico, nombre de usuario y contraseña.

### 7. Ejecutar el servidor de desarrollo
Finalmente, levanta el servidor de pruebas para verificar que todo funcione:
```bash
python manage.py runserver
```

Ahora puedes abrir un navegador web e ir a `http://127.0.0.1:8000/`. El panel de administrador estará disponible en `http://127.0.0.1:8000/admin/`.

## Tecnologías Utilizadas
- **Django 5.2**
- **Django REST Framework**
- **Simple JWT** (Autenticación con JSON Web Tokens)
- **SQLite3** (Base de datos por defecto)
