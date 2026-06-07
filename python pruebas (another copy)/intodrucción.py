import pygame 
import sys
pygame.pygame.cdrom.init()
def introduccion():
    nombre_usuario = input("Escribe tu nombre: ")
    nombre_usuario = input("Confirma tu nombre: ")
    print("Soy Sara la ia que te guíara en tu misión")
    parada = input(" ")
    print("Se te a elegido para pilotar al planeta XH-3892 y encontrar muestras de el anterior viaje de exploración, para determinar que les ocurrio")
    confirma = input("Deseas dirigir la misión, confirma si o no: ")
    validar_pregunta(confirma)
    
    while confirma.casefold() not in ("si", "no"):
        print("estoy en el while")
        confirma = input("Deseas dirigir la misión, confirma si o no: ")
        validar_pregunta(confirma)
        
def validar_pregunta (confirma):
    if confirma.upper() == "NO":
        print("Adiós")
    elif confirma.upper() == "SI":
        inicio()
    else: 
        print("opción no valida")

def inicio():
    print("muy bien, comenzara tu misión")
    parada = input("")

introduccion()

comida = 15
energia = 100
medicina = 5
dias = 0
print("Para el vaije necesitaras gestionar tus recursos ya que no podras contactar con ningúna estación o equipo cercano, vas a tener un contador de comida de comida y energía que se reportara al inicio de cada día, tambíen podras ver tu estado de salud, tendras  reservas de medicamentos y equipo que tambíen se te indicara al inicio de cada día. Algo muy importante es que cuides tu salud mental y leas bien los informes que te dare cada día, por el momento esto es lo más importante ya despúes te indicare que más necesitas")
parada = input("")
contador_dias = input

    
