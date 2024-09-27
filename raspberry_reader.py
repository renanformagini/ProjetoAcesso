import RPi.GPIO as GPIO
import requests
from time import sleep
from mfrc522 import SimpleMFRC522

rfid_reader = SimpleMFRC522()


colaboradores_cache = {}

def buscar_colaboradores():
    response = requests.get('http://localhost:5000/colaboradores')
    if response.status_code == 200:
        for colaborador in response.json():
            colaboradores_cache[colaborador['id']] = colaborador['nome']

try:
    buscar_colaboradores() 
    while True:
        tag_id, tag_text = rfid_reader.read()
        print(f"ID da tag: {tag_id}")

        if tag_id in colaboradores_cache:
            colaborador_id = tag_id
            tipo = "entrada"  
            requests.post('http://localhost:5000/acesso', json={"colaborador_id": colaborador_id, "tipo": tipo})
            sleep(1)
except KeyboardInterrupt:
    print("Programa interrompido")
finally:
    GPIO.cleanup()
