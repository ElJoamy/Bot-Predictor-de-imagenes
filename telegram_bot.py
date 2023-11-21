import base64
import csv
import os
import requests
from datetime import datetime
from config import get_settings
from io import BytesIO
from telebot import telebot, types

API_TOKEN = get_settings().telegram_token

bot = telebot.TeleBot(API_TOKEN)

log_file = "user_log.csv"

API_URL = get_settings().api_url


def log_user_data(user_id, user_name, command_time, comando):
    file_exists = os.path.isfile(log_file)
    
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["User ID", "Username", "Command Time", "Date", "Command"])

        writer.writerow([user_id, user_name, command_time.strftime("%H:%M:%S"), command_time.strftime("%Y-%m-%d"), comando])


def get_user_ids_from_log():
    user_ids = set()
    try:
        with open(log_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader, None) 
            for row in reader:
                if row:
                    user_ids.add(int(row[0])) 
    except FileNotFoundError:
        print("Archivo de log no encontrado.")
    return user_ids

def generate_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    # Creando botones para cada comando
    start_button = types.KeyboardButton('/start')
    help_button = types.KeyboardButton('/help')
    status_button = types.KeyboardButton('/status')
    predict_button = types.KeyboardButton('/predict')
    choose_button = types.KeyboardButton('/choose')
    reports_button = types.KeyboardButton('/reports')

    # Añadiendo botones al teclado
    markup.row(start_button, help_button)
    markup.row(status_button, predict_button)
    markup.row(choose_button, reports_button)

    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text
    log_user_data(user_id, user_name, command_time, comando)

    markup= generate_markup()
    bot.reply_to(message, f"Hola {user_name}, bienvenido al bot Object Detection API! Usa el comando /help para ver los comandos disponibles.", reply_markup=markup)
    print (f"El {user_name} con ID {user_id} hizo el comando {comando} a las {command_time.strftime('%H:%M:%S')}")

@bot.message_handler(commands=['help'])
def handle_help(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text
    log_user_data(user_id, user_name, command_time, comando)
    help_message = f"Este bot te permite interactuar con la API de detección de objetos.\n" \
                   f"Los comandos disponibles son:\n" \
                   f"/start - Iniciar el bot\n" \
                   f"/help - Mostrar este mensaje de ayuda\n" \
                   f"/status - Obtener el estado del servicio\n" \
                   f"/predict - Enviar una imagen para predecir\n" \
                   f"/choose - Elegir las etiquetas que deseas detectar\n" \
                   f"/reports - Obtener el reporte de predicciones\n" \
                   f"Tambien tienes en tu teclado los comandos disponibles a lado del clip de archivos.\n" \
                   f"Para más información, visita el repositorio del proyecto: https://github.com/ElJoamy/Bot-Predictor-de-imagenes.git \n" \
                   f"Si tienes mas dudas puedes revisar el {API_URL}docs"
                   
    bot.reply_to(message, help_message)
    print (f"El {user_name} con ID {user_id} hizo el comando {comando} a las {command_time.strftime('%H:%M:%S')}")


@bot.message_handler(commands=['status'])
def handle_status(message):
    user_id = message.from_user.id
    allowed_user_ids = get_user_ids_from_log()

    if user_id not in allowed_user_ids:
        bot.reply_to(message, "No tienes permiso para usar este comando.")
        return
    
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text
    log_user_data(user_id, user_name, command_time, comando)
    status_url = API_URL + "status"
    try:
        response = requests.get(status_url)
        if response.status_code == 200:
            status_data = response.json()
            reply_message = f"Estado del servicio: {status_data['message']}\n" \
                            f"API: {status_data['api_name']}\n" \
                            f"Revisión: {status_data['revision']}\n" \
                            f"Versión del modelo: {status_data['model_version']}\n" \
                            f"Nivel de log: {status_data['log_level']}"
        else:
            reply_message = "Error al obtener el estado del servicio."
    except requests.exceptions.RequestException as e:
        reply_message = f"Error al conectarse con la API: {e}"
    print (f"El {user_name} con ID {user_id} hizo el comando {comando} a las {command_time.strftime('%H:%M:%S')}")
    bot.reply_to(message, reply_message)

users_waiting_for_images = {}
user_state = {}

@bot.message_handler(commands=['predict'])
def request_image(message):
    users_waiting_for_images[message.from_user.id] = True
    bot.reply_to(message, "Por favor, sube una imagen para predecir.")
    user_id = message.from_user.id
    user_state[user_id] = 'predict'
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text
    log_user_data(user_id, user_name, command_time, comando)
    print (f"El {user_name} con ID {user_id} hizo el comando {comando} a las {command_time.strftime('%H:%M:%S')}")

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == 'predict', content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text
    log_user_data(user_id, user_name, command_time, comando)
    if users_waiting_for_images.get(message.from_user.id):
        del users_waiting_for_images[message.from_user.id]
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        print(f'Archivo descargado: {file_info.file_path}')
        bot.send_message(chat_id=message.chat.id, text="Procesando imagen...")
        contador = 0
        image_stream = BytesIO(downloaded_file)
        image_stream.name = f'image{contador}.jpg'

        while os.path.exists(image_stream.name):
            contador += 1
            image_stream.name = f'image{contador}.jpg'

        files = {'file': (image_stream.name, image_stream, 'image/jpeg')}
        data = {'threshold': 0.5}
        # response = requests.post(API_URL + 'predict', files=files, data=data)
        # if response.status_code == 200:
        #     bot.send_photo(chat_id=message.chat.id, photo=BytesIO(response.content), caption=f'Imagen procesada.')
        #     print("Imagen enviada.")
        # else:
        #     bot.send_message(chat_id=message.chat.id, text="Error al procesar la imagen.")
        response = requests.post(API_URL + 'predict', files=files, data=data)
        if response.status_code == 200:
            response_data = response.json()
            image_base64 = response_data["image"]
            detections = response_data["detections"]

            # Crear el mensaje de detección
            detection_message = ", ".join([f"{det['label']}: {det['confidence']:.2f}" for det in detections])
            
            # Decodificar y enviar la imagen
            img_data = base64.b64decode(image_base64)
            bot.send_photo(chat_id=message.chat.id, photo=img_data, caption=detection_message)
        else:
            bot.send_message(chat_id=message.chat.id, text="Error al procesar la imagen.")

    else:
        bot.send_message(chat_id=message.chat.id, text="Primero usa el comando /predict.")
    del user_state[user_id]

users_waiting_for_labels = {} 
users_labels = {} 

@bot.message_handler(commands=['choose'])
def start_choose_process(message):
    user_id = message.from_user.id
    user_state[user_id] = 'choose'
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text
    log_user_data(user_id, user_name, command_time, comando)
    bot.reply_to(message, "Por favor, envía las etiquetas que deseas detectar, separadas por comas. Ejemplo: perro,gato,persona")
    users_waiting_for_labels[message.from_user.id] = True

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == 'choose', content_types=['text'])
def receive_labels(message):
    user_id = message.from_user.id
    users_labels[user_id] = message.text.split(',') 
    del users_waiting_for_labels[user_id] 
    bot.reply_to(message, f'Las etiquetas que deseas detectar son: {users_labels[user_id]} y han sido recibidas. Ahora, por favor, sube una imagen para predecir.')

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == 'choose', content_types=['photo'])
def handle_choose_photo(message):
    user_id = message.from_user.id
    if user_id not in users_labels:
        bot.reply_to(message, "Primero usa el comando /choose.")
        return

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    image_stream = BytesIO(downloaded_file)
    image_stream.name = 'image.jpg'

    files = {'file': (image_stream.name, image_stream, 'image/jpeg')}
    data = {'threshold': 0.5, 'labels': users_labels[user_id]}
    response = requests.post(API_URL + 'choose_predict', files=files, data=data)

    if response.status_code == 200:
        bot.send_photo(chat_id=message.chat.id, photo=BytesIO(response.content), caption=f'Imagen procesada con las etiquetas {users_labels[user_id]}')
    else:
        bot.send_message(chat_id=message.chat.id, text="Error al procesar la imagen.")

    del users_labels[user_id]
    del user_state[user_id]

@bot.message_handler(commands=['reports'])
def handle_reports(message):
    user_id = message.from_user.id
    allowed_user_ids = get_user_ids_from_log()
    user_name = message.from_user.username
    command_time = datetime.now()
    comando = message.text
    log_user_data(user_id, user_name, command_time, comando)
    print (f"El {user_name} con ID {user_id} hizo el comando {comando} a las {command_time.strftime('%H:%M:%S')}")

    if user_id not in allowed_user_ids:
        bot.reply_to(message, "No tienes permiso para usar este comando.")
        return

    reports_url = API_URL + "reports"
    try:
        response = requests.get(reports_url)
        if response.status_code == 200:
            report = BytesIO(response.content)
            report.name = "report.csv"
            bot.send_document(chat_id=message.chat.id, document=report, caption="Reporte de predicciones")
        else:
            bot.reply_to(message, "Error al obtener el reporte.")
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Error al conectarse con la API: {e}")
