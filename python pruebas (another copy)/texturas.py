import pygame
import sys

width = 800
height = 600
suelo = 500
roca = 50
calcita = 20
hierro = 20
cristal = 30


rojo = ((255, 0, 0))
negro = ((0, 0, 0))
blanco = ((255, 255, 255))
gris = ((128, 128, 128))
azul = ((255, 255, 0))
gris_distinto = ((80, 80, 80))
amarillo = 	(255, 255, 0)
azul_claro = (0, 191, 255)
gris_oscuro = (100, 100, 100)
azul_oscuro = (0, 0, 20)
naranja = (255, 193, 137)
dorado = (255, 215, 0)
morado = (128, 0, 128)
rosa = (90, 40, 40)
verde_suave = (130, 60, 60)

energy_max = 100
food_max = 100
instamina = 100


color_energy = amarillo
color_food = rojo
color_instamina = azul_claro
background = gris_oscuro

interval_update = 2000

duracion_dia = 24000
amanecer_tiempo = 6000
mañana_tiempo = 8000
tarde_tiempo = 18000
media_noche_tiempo = 24000
transicion_dia_noche = 4000
oscuridad_max = 180

color_noche = azul_oscuro
color_dia = blanco
color_amanecer_atardecer = naranja

craft_grid_size = 3
craft_slot_size = 50
craft_slot_margin = 5
craft_grid_x = width - (craft_grid_size * (craft_slot_size + craft_slot_margin)) - 20
craft_grid_y = height - (craft_grid_size * (craft_slot_size + craft_slot_margin)) - 20  