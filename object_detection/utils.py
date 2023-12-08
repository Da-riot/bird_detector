import cv2
import os
import time
import numpy as np
from tflite_support.task import processor
from typing import List, Dict
from tflite_support.task import vision
import firebase_admin
from firebase_admin import credentials, storage

# Ruta al archivo JSON que descargaste de Firebase (la clave de servicio)
cred = credentials.Certificate("db.json")

# Inicializa la app de Firebase
firebase_admin.initialize_app(cred, {
    'storageBucket': 'detector-aves.appspot.com'  # Reemplaza con tu URL del bucket de almacenamiento
})

_MARGIN = 10  # pixels
_ROW_SIZE = 10  # pixels
_FONT_SIZE = 1
_FONT_THICKNESS = 1
_TEXT_COLOR = (0, 255, 0)  # green
last_capture_time = 0
# Carpeta de salida para las capturas
output_folder = "capturas"  # Cambia esto a la carpeta que desees

# Asegúrate de que la carpeta exista, si no, créala
os.makedirs(output_folder, exist_ok=True)

def visualize(image: np.ndarray, filtered_detections: List[Dict]) -> np.ndarray:

    global last_capture_time  # Utilizamos la variable global

    current_time = time.time()
    for detection in filtered_detections:
        # Cambia la obtención de la bounding_box
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        cv2.rectangle(image, start_point, end_point, _TEXT_COLOR, 3)

        # Cambia la obtención de la categoría y la puntuación
        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)

        # Cambia la obtención del texto del resultado
        result_text = category_name + ' (' + str(probability) + ')'
        text_location = (_MARGIN + bbox.origin_x, _MARGIN + _ROW_SIZE + bbox.origin_y)
        cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    _FONT_SIZE, _TEXT_COLOR, _FONT_THICKNESS)

        # Añade la lógica de tiempo para la captura de imágenes
        if category_name == 'bird' and current_time - last_capture_time >= 30:
            # Captura la imagen
            capture_path = os.path.join(output_folder, f'capture_{current_time}.jpg')
            cv2.imwrite(capture_path, image)

            # Actualiza el tiempo de la última captura
            last_capture_time = current_time
            print(f"Captura guardada en: {capture_path}")
            # Referencia al bucket de Firebase Storage
            bucket = storage.bucket()

            # Ruta local de la imagen que deseas subir
            ruta_imagen_local = capture_path

            # Ruta dentro del bucket de almacenamiento donde deseas guardar la imagen
            ruta_destino_storage = "birds/" + f'capture_{current_time}.jpg'  # Ruta y nombre del archivo en Storage

            # Subir la imagen al Firebase Storage
            blob = bucket.blob(ruta_destino_storage)
            blob.upload_from_filename(filename=ruta_imagen_local)

            print(f"Imagen subida a Firebase Storage con éxito.")

    return image
