# Bot Predictor de Imágenes
Nombre: Joseph Anthony Meneses Salguero
Codigo: 55669

## Indice
- [Bot Predictor de Imágenes](#bot-predictor-de-imágenes)
  - [Indice](#indice)
  - [Descripción](#descripción)
  - [Estrucutra del proyecto](#estrucutra-del-proyecto)
  - [Características](#características)
  - [Requisitos](#requisitos)
  - [Instalación](#instalación)
  - [Configuración](#configuración)
  - [Uso](#uso)
    - [Comandos del Bot](#comandos-del-bot)
  - [Demostración](#demostración)
  - [Autores](#autores)
  - [Licencia](#licencia)

## Descripción
Este proyecto es un bot de Telegram que interactúa con una API de FastAPI para realizar la detección de objetos en imágenes. Utiliza un modelo de YOLO (You Only Look Once) para identificar y etiquetar objetos en las imágenes que los usuarios suben a través del bot de Telegram.

## Estrucutra del proyecto
```bash
│   .env
│   .env.example  # Archivo de configuración de variables de entorno
│   .gitattributes # Archivo de configuración de Git 
│   .gitignore # Archivo de configuración de Git
│   app.py # Archivo principal para iniciar el bot y la API de FastAPI
│   config.py # Configuración de la API
│   detector.py # Clase para la detección de objetos
│   LICENSE # Licencia del proyecto
│   predictions_log.csv # Archivo de registro de predicciones
│   README.md # Archivo de documentación
│   requirements.txt # Archivo de dependencias 
│   telegram_bot.py # Clase para el bot de Telegram
│   user_log.csv # Archivo de registro de usuarios
│   yolov8x.pt # Modelo YOLO
│
├───media
│   └───telegrambot # Carpeta para mostrar el tutorial en el CreateBotTelegram.md
│           tele2.png
│           tele3.png
│           tele4.jpg
│           telegram1.png
│
└───tutorial
        CreateBotTelegram.md # Tutorial para crear un bot de Telegram
```

## Características

- **Detección de Objetos**: Usa YOLO para detectar objetos en imágenes.
- **Interacción a través de Telegram**: Permite a los usuarios interactuar con el modelo de IA a través de un bot de Telegram.
- **Personalización de Detección**: Los usuarios pueden especificar qué objetos quieren detectar en sus imágenes.

## Requisitos

Para ejecutar este proyecto, necesitarás lo siguiente:

- Python 3.6+
- Bibliotecas de Python: `fastapi`, `uvicorn`, `python-telegram-bot`, `opencv-python`, `numpy`, `pillow`, `pydantic`
- Un token de bot de Telegram (obtenido a través de BotFather en Telegram)

## Instalación

Clona el repositorio:

```bash
git clone https://github.com/ElJoamy/Bot-Predictor-de-imagenes.git
cd Bot-Predictor-de-imagenes
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

1. **Token de Telegram**: Configura tu token de bot de Telegram en el archivo [.env.example](.env.example).
2. **Modelo YOLO**: Asegúrate de que el modelo YOLO esté correctamente configurado en el archivo [.env.example](.env.example).

```.env
# FAST API
API_NAME="Object Detection API EXAMPLE"
REVISION="debug"
YOLO_VERSION="yolov8x.pt" # Puedes escoger entre estas yolov8s.pt, yolov8m.pt, yolov8n.pt, yolov8l.pt, yolov8x.pt
LOG_LEVEL="CRITICAL"

# Telegram
TELEGRAM_TOKEN="TU_TOKEN_AQUI_DE_TELEGRAM" # Configura tu token de bot de Telegram aquí

# API URL
API_URL="http://127.0.0.1:8000/"
```

3. Puedes cambair el nombre del archivo [.env.example](.env.example) a `.env` para que el programa pueda leer las variables de entorno.
```bash
mv .env.example .env
```

4. Si no sabes como obtener tu TOKEN de Telegram, puedes seguir [Los siguientes pasos](/tutorial/CreateBotTelegram.md)

## Uso

Para iniciar el bot y la API:

```bash
python app.py
```

### Comandos del Bot

- `/start`: Iniciar interacción con el bot.
- `/help`: Obtener ayuda y una lista de comandos disponibles.
- `/status`: Verificar el estado del servicio.
- `/predict`: Enviar una imagen para realizar una detección de objetos.
- `/choose`: Especificar etiquetas para la detección personalizada en una imagen.
- `/reports`: Obtener un informe de las predicciones realizadas.

## Demostración
![ ](/media/demostracion/demostracion.gif)

## Autores
<table>
<tr>
    <td align="center">
        <a href="https://github.com/ElJoamy">
            <img src="https://avatars.githubusercontent.com/u/68487005?v=4" width="50;" alt="ElJoamy"/>
            <br />
            <sub><b>Joseph Anthony Meneses Salguero</b></sub>
        </a>
    </td></tr>
</table>

## Licencia

Este proyecto está bajo la Licencia GNU AFFERO GENERAL PUBLIC [LICENSE](LICENSE).
