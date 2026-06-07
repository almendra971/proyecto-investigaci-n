import random

class dias:
    def __init__(self, numero_dia):
        self.numero = numero_dia
        self.clima = random.choice(["Soleado", "Lluvioso", "Nublado", "Tormenta"])
        self.eventos = []
        self.evento_dia()
        
    def evento_dia(self):
        posibles_eventos = [
            "Hay un daño en la nave",
            "Descubres algo interesante",
            "Recibes señales desconocidas"
        ]   # type: ignore
        self.eventos = random.sample(posibles_eventos, k=random.randint(1, 2))
        
    def informacion_del_dia(self):
        print(f"\n dia numero {self.numero}")
        print(f" Es un dia {self.clima}")
        for e in self.eventos:
            print(f"  - {e}")

class Juego:
    def __init__(self):
        self.dia_actual = 1

    def avanzar_dia(self):
        dia = dias(self.dia_actual)
        dia.informacion_del_dia()
        self.dia_actual += 1
         


juego = Juego()

while True:
    juego.avanzar_dia()
    opcion = input(f"\n¿Quieres pasar al siguiente día? (y/n): ").strip().lower()
    if opcion != 'y':
        print(" Sigue jugando")
        break