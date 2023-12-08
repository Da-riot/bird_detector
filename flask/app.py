from flask import Flask, render_template
from firebase_admin import credentials, storage, initialize_app
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuración de Firebase
cred = credentials.Certificate("./db.json")
firebase_app = initialize_app(cred, {'storageBucket': 'detector-aves.appspot.com'})

@app.route('/')
def index():
    # Obtener referencias a todos los objetos (imágenes) en el bucket
    bucket = storage.bucket(name='detector-aves.appspot.com')
    blobs = bucket.list_blobs()
    
    expiration_time = datetime.utcnow() + timedelta(seconds=3600)  # 1 hora
    image_urls = [blob.generate_signed_url(expiration=expiration_time) for blob in blobs]
    image_urls.pop(0)
    image_urls.reverse()

    # Renderizar la plantilla HTML con las URL de las imágenes
    return render_template('index.html', image_urls=image_urls)

if __name__ == '__main__':
    app.run(debug=True)
