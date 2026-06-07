import texturas
import pygame
import random
import os
from objetos import Rocas, Mineral_calcita, Hierro, Cristal
from pygame import Surface

class Chunk:
    def __init__(self, chunk_x, chunk_y, chunk_size=800, semilla_mundo=0):
        self.world_x = chunk_x * chunk_size
        self.world_y = chunk_y * chunk_size
        self.chunk_size = chunk_size
        probabilidad_veta_hierro = 0.7
        probabilidad_veta_cristal = 0.5
        
        
        state = random.getstate()
        random.seed(hash((chunk_x, chunk_y, semilla_mundo)))  # Semilla basada en posición y semilla global
        
        self.rocas = [Rocas(self.world_x + random.randint(0, chunk_size - texturas.roca), 
                            self.world_y + random.randint(0, chunk_size - texturas.roca)) for _ in range(8)]

        self.calcita = [Mineral_calcita(self.world_x + random.randint(0, chunk_size - texturas.calcita), 
                                        self.world_y + random.randint(0, chunk_size - texturas.calcita)) for _ in range(5)]


        self.hierros = []
        if random.random() < probabilidad_veta_hierro:
            cantidad = random.randint(1, 4)  # definimos cuántos pueden salir (entre 1 y 4)
    
            for _ in range(cantidad):
                nuevo_hierro = Hierro(
                    self.world_x + random.randint(10, chunk_size - texturas.hierro),
                    self.world_y + random.randint(10, chunk_size - texturas.hierro)
                )
                self.hierros.append(nuevo_hierro)
        self.cristales = []
        if random.random() < probabilidad_veta_cristal:
            cantidad = random.randint(1, 5)  # cuántos pueden salir (entre 1 y 5)
    
            for _ in range(cantidad):
                nuevo_cristal = Cristal(
                    self.world_x + random.randint(10, chunk_size - texturas.cristal),
                    self.world_y + random.randint(10, chunk_size - texturas.cristal)
                )
                self.cristales.append(nuevo_cristal)

        random.setstate(state)

class WorldInfinito:
    def __init__(self, screen_width, screen_height, chunk_size=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.chunk_size = chunk_size
        self.chunks = {}
        self.semilla_mundo = random.randint(0, 999999)
        
        self.camera_x = 0
        self.camera_y = 0
        self._last_chunk_pos = (None, None)
        
        # 1. CARGAR SUELO AQUÍ (Solo una vez)
        suelo_path = os.path.join('imagenes', 'fondos', 'suelo.png')
        try:
            self.suelo_image = pygame.image.load(suelo_path).convert()
        except:
            self.suelo_image = pygame.Surface((texturas.suelo, texturas.suelo))
            self.suelo_image.fill((30, 30, 30))
        self.suelo_image = pygame.transform.scale(self.suelo_image, (texturas.suelo, texturas.suelo))

        # 2. SISTEMA DÍA/NOCHE
        self.tiempo_inicio_dia = pygame.time.get_ticks() 
        self.day_overlay = Surface((screen_width, screen_height))
        self.day_overlay.set_alpha(0) 
        
        
    def mezclar_colores(self, color1, color2, proporcion):
        # Aseguramos que la proporción esté entre 0 y 1 para evitar errores
        proporcion = max(0, min(1, proporcion))
        r = int(color1[0] + (color2[0] - color1[0]) * proporcion)
        g = int(color1[1] + (color2[1] - color1[1]) * proporcion)
        b = int(color1[2] + (color2[2] - color1[2]) * proporcion)
        return (r, g, b)

    def update_tiempo(self, dt=0):
        tiempo_actual = (pygame.time.get_ticks() - self.tiempo_inicio_dia) % texturas.duracion_dia
        
        # novhe 
        if tiempo_actual < texturas.transicion_dia_noche:
            color = texturas.color_noche
            alpha = texturas.oscuridad_max

        # amanecer
        elif tiempo_actual < texturas.amanecer_tiempo:
            p = (tiempo_actual - texturas.transicion_dia_noche) / (texturas.amanecer_tiempo - texturas.transicion_dia_noche)
            # Mezclamos de Azul Oscuro a Naranja
            color = self.mezclar_colores(texturas.color_noche, texturas.color_amanecer_atardecer, p)
            alpha = int(texturas.oscuridad_max - (p * 50)) 

        elif tiempo_actual < texturas.mañana_tiempo:
            p = (tiempo_actual - texturas.amanecer_tiempo) / (texturas.mañana_tiempo - texturas.amanecer_tiempo)
            color = self.mezclar_colores(texturas.color_amanecer_atardecer, texturas.color_dia, p)
            alpha = int(130 * (1 - p))

        elif tiempo_actual < texturas.tarde_tiempo:
            color = texturas.color_dia
            alpha = 0


        elif tiempo_actual < texturas.media_noche_tiempo:
            # Se divide en dos para que pase por naranja
            mitad = (texturas.tarde_tiempo + texturas.media_noche_tiempo) / 2
            
            if tiempo_actual < mitad:
                p = (tiempo_actual - texturas.tarde_tiempo) / (mitad - texturas.tarde_tiempo)
                color = self.mezclar_colores(texturas.color_dia, texturas.color_amanecer_atardecer, p)
                alpha = int(p * 130)
            else:
                p = (tiempo_actual - mitad) / (texturas.media_noche_tiempo - mitad)
                color = self.mezclar_colores(texturas.color_amanecer_atardecer, texturas.color_noche, p)
                alpha = int(130 + (p * (texturas.oscuridad_max - 130)))
        
        else:
            color = texturas.color_noche
            alpha = texturas.oscuridad_max

        self.day_overlay.fill(color)
        self.day_overlay.set_alpha(alpha)


    def _get_chunk_coords(self, x, y):
        return (int(x // self.chunk_size), int(y // self.chunk_size))

    def actualizar(self, j_x, j_y):
        self.update_tiempo() # Llamamos a la actualización de luz
        
        curr_chunk = self._get_chunk_coords(j_x, j_y) 
        if curr_chunk != self._last_chunk_pos:
            cx, cy = curr_chunk 
            radio_gen = 2
            for dx in range(-radio_gen, radio_gen + 1):
                for dy in range(-radio_gen, radio_gen + 1):
                    coords = (cx + dx, cy + dy)
                    if coords not in self.chunks:
                        self.chunks[coords] = Chunk(coords[0], coords[1], self.chunk_size, self.semilla_mundo)
            
            radio_limpieza = 4
            a_borrar = [c for c in self.chunks if abs(c[0]-cx) > radio_limpieza or abs(c[1]-cy) > radio_limpieza]
            for c in a_borrar: del self.chunks[c]
            self._last_chunk_pos = curr_chunk

    def draw(self, screen, j_x, j_y):
        self.camera_x = j_x - self.screen_width // 2
        self.camera_y = j_y - self.screen_height // 2
        
        # 1. Dibujar Suelo
        inicio_x = int(self.camera_x // texturas.suelo) * texturas.suelo
        inicio_y = int(self.camera_y // texturas.suelo) * texturas.suelo
        
        for y in range(inicio_y, inicio_y + self.screen_height + texturas.suelo, texturas.suelo):
            for x in range(inicio_x, inicio_x + self.screen_width + texturas.suelo, texturas.suelo):
                screen.blit(self.suelo_image, (x - self.camera_x, y - self.camera_y))
        
        # 2. Dibujar Objetos
        for chunk in self.chunks.values():
            if (chunk.world_x - self.camera_x > self.screen_width or 
                chunk.world_x + self.chunk_size - self.camera_x < 0 or
                chunk.world_y - self.camera_y > self.screen_height or
                chunk.world_y + self.chunk_size - self.camera_y < 0):
                continue
            
            for roca in chunk.rocas:
                roca.draw(screen, self.camera_x, self.camera_y)
            for ca in chunk.calcita:
                ca.draw(screen, self.camera_x, self.camera_y)
            for h in chunk.hierros:
                h.draw(screen, self.camera_x, self.camera_y)
            for cr in chunk.cristales:
                cr.draw(screen, self.camera_x, self.camera_y)

        screen.blit(self.day_overlay, (0, 0))

    def obtener_objetos_cercanos(self, world_x, world_y, radio=100):
        objetos = {'rocas': [], 'calcita': [], 'hierros': [], 'cristales': []}
        cx, cy = self._get_chunk_coords(world_x, world_y)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                chunk = self.chunks.get((cx + dx, cy + dy))
                if chunk:
                    objetos['rocas'].extend([r for r in chunk.rocas if abs(r.x - world_x) < radio and abs(r.y - world_y) < radio])
                    objetos['calcita'].extend([c for c in chunk.calcita if abs(c.x - world_x) < radio and abs(c.y - world_y) < radio])
                    objetos['hierros'].extend([h for h in chunk.hierros if abs(h.x - world_x) < radio and abs(h.y - world_y) < radio])
                    objetos['cristales'].extend([cr for cr in chunk.cristales if abs(cr.x - world_x) < radio and abs(cr.y - world_y) < radio])
        return objetos

    def remover_objeto(self, objeto):
        coords = self._get_chunk_coords(objeto.x, objeto.y)
        chunk = self.chunks.get(coords)
        if chunk:
            if objeto in chunk.rocas: chunk.rocas.remove(objeto); return True
            if objeto in chunk.calcita: chunk.calcita.remove(objeto); return True
            if objeto in chunk.hierros: chunk.hierros.remove(objeto); return True
            if objeto in chunk.cristales: chunk.cristales.remove(objeto); return True
        return False