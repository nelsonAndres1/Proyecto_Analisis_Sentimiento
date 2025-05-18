import functions_framework
from google.cloud import speech
from google.cloud import storage
import os
import joblib
import re
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from classFile import ReemplazarJergas, LimpiarTexto, TokenizarYLematizar, Word2VecTransformer
import dill

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'speechCredentials.json'

nltk.download('wordnet')
nltk.download('punkt_tab')
nltk.download('stopwords')

jerga_dict_es = {
    "pa'": "para",
    "pana": "amigo"
}


with open('preprocessing_pipeline3.joblib', 'rb') as f:
    preprocessing_pipeline = dill.load(f)

vectorizer = joblib.load('vectorizer.joblib')
encoder = joblib.load('encoder.joblib')
svm_model_best = joblib.load('svm_model_best.pkl')
explainer = joblib.load('explainer.joblib')

def predict_fn(texts):
    # Primero, vectorizar los textos y luego hacer las predicciones con el modelo
    X_vec = vectorizer.transform(texts)  # Vectorizamos el texto
    X_ohe = encoder.transform(X_vec.toarray())  # Transformamos con OneHotEncoder
    return svm_model_best.predict_proba(X_ohe)  # Devolvemos las probabilidades

def transcribe_gcs_audio(gcs_uri):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000,  # Ajusta según el formato de tu audio
        language_code="es-CO",  # Cambia al idioma de tu elección
        audio_channel_count = 2,
        model="Telephony",
        enable_separate_recognition_per_channel = True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    #print("Esperando los resultados...")
    response = operation.result(timeout=90)
    transcripcionCompleta = ""
    #print("response")
    #print(f"{response}")
    # Procesar la respuesta
    for result in response.results:

        '''
            En este punto podemos crear una funcion que vaya guardando en un json o un dataset
            la ruta del audio (gcs_uri)
            y la transcripcion (result.alternatives[0].transcript)
            y cuando termine esta funcion , exportar este dataset en un csv o un excel
        '''
        transcripcionCompleta=transcripcionCompleta+str(result.alternatives[0].transcript)
        #print(f"Transcripción: {result.alternatives[0].transcript}")

    return [transcripcionCompleta,response]

def convertir_a_txt(ruta):
    # Eliminar 'files/' del inicio
    nombre = ruta[6:]  # Esto elimina los primeros 6 caracteres 'files/'
    # Reemplazar la extensión '.wav' por '.txt'
    nombre_txt = nombre.replace(".wav", ".txt")
    return nombre_txt

def convertir_a_html(ruta):
    # Eliminar 'files/' del inicio
    nombre = ruta[6:]  # Esto elimina los primeros 6 caracteres 'files/'
    # Reemplazar la extensión '.wav' por '.txt'
    nombre_txt = nombre.replace(".wav", ".html")
    return nombre_txt

def crear_archivo_texto(nombre_archivo, contenido):
    # Nombre del bucket donde se va a guardar el archivo
    bucket_name = "tesis-v1-database.firebasestorage.app"
    # Crear una instancia del cliente de Google Cloud Storage
    client = storage.Client()
    # Obtener el bucket
    bucket = client.get_bucket(bucket_name)
    # Crear un blob (objeto de archivo) en el bucket
    blob = bucket.blob(nombre_archivo)
    # Subir el archivo al bucket
    blob.upload_from_string(contenido)

    return f"Archivo {nombre_archivo} creado y subido a {bucket_name}."

def crear_archivo_html(nombre_archivo, contenido):
    # Nombre del bucket donde se va a guardar el archivo
    bucket_name = "tesis-v1-database.firebasestorage.app"
    # Crear una instancia del cliente de Google Cloud Storage
    client = storage.Client()
    # Obtener el bucket
    bucket = client.get_bucket(bucket_name)
    # Crear un blob (objeto de archivo) en el bucket
    blob = bucket.blob(nombre_archivo)
    # Subir el archivo al bucket
    blob.upload_from_string(contenido, content_type='text/html; charset=utf-8')

    return f"Archivo {nombre_archivo} creado y subido a {bucket_name}."


# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def hello_gcs(cloud_event):
    data = cloud_event.data
    if "files/" in data["name"]:  # Si existe la carpeta 'folder'
        print("ejecutando")
        ubicacion_audio = "gs://"+ data["bucket"]+ "/" +data["name"]
        transcriptionFull=transcribe_gcs_audio(ubicacion_audio)
        print(transcriptionFull[0])
        # Cargar el modelo guardado
        X_nuevos_datos = [transcriptionFull[0]]
        # Preprocesar los datos (asegúrate de que el mismo pipeline se aplique)
        X_procesado = preprocessing_pipeline.transform(X_nuevos_datos)  # X_nuevos_datos es el nuevo conjunto de datos
        #print(X_procesado)
        # Vectorizar y aplicar OneHotEncoder
        X_vectorized = vectorizer.transform(X_procesado) # Ajusta el vectorizador
        #print(X_vectorized)
        X_ohe = encoder.transform(X_vectorized.toarray())  # Aplica OneHotEncoder
        #print(X_ohe)
        y_pred_se = svm_model_best.predict(X_ohe)
        print(y_pred_se)
        explanation = explainer.explain_instance(transcriptionFull[0], predict_fn, num_features=10, labels=[0,1,2])
        html_explanation = explanation.as_html()
        crear_archivo_texto(convertir_a_txt(data["name"]), y_pred_se[0])
        print( y_pred_se[0])
        crear_archivo_html(convertir_a_html(data["name"]), html_explanation)
        print(html_explanation)
    else:
        #from nltk.tokenize import word_tokenize
        #X_nuevos_datos = ["alÛ Buenos dÌas por favor la joven Juanita Arenas  seÒora  mucho gusto Mi nombre es Valentina Me estoy comunicando a la universidad jariana Cali cÛmo est·  Muy bien  bueno el motivo de mi llamada es porque ha presentado interÈs por el programa de medicina y el dÌa de maÒana finalizamos proceso de inscripciÛn deseamos conocer si vas a iniciar el proceso  alÛ  Hola Me escuchas  alÛ  Hola  hola te ahÌ se escucha bien Hola  buenas alÛ alÛ"]
        #X_procesado = preprocessing_pipeline.transform(X_nuevos_datos)
        #print(X_procesado)
        # Vectorizar y aplicar OneHotEncoder
        #X_vectorized = vectorizer.transform(X_procesado) # Ajusta el vectorizador
        #print(X_vectorized)
        #X_ohe = encoder.transform(X_vectorized.toarray())  # Aplica OneHotEncoder
        #print(X_ohe)
        #y_pred_se = svm_model_best.predict(X_ohe)
        #print(y_pred_se)
        #print(X_procesado)
        print("no fue necesaria la ejecucion")

    print("concluye la ejecucion")
    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    #print(f"Event ID: {event_id}")
    #print(f"Event type: {event_type}")
    #print(f"Bucket: {bucket}")
    #print(f"File: {name}")
    #print(f"Metageneration: {metageneration}")
    #print(f"Created: {timeCreated}")
    #print(f"Updated: {updated}")
    return "ok"


@functions_framework.http
def hello_http(request):
    return "Hello world!"


if __name__ == '__main__':
    print("inicio")