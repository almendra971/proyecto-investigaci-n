import os
import pygame
import texturas

class Rocas:
    _IMAGE = None 
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        if Rocas._IMAGE is None:
            path = os.path.join('imagenes', 'objetos', 'rok.png')
            try:
                img = pygame.image.load(path).convert_alpha() 
                Rocas._IMAGE = pygame.transform.scale(img, (texturas.roca, texturas.roca))
            except:
                Rocas._IMAGE = pygame.Surface((texturas.roca, texturas.roca))
                Rocas._IMAGE.fill((100, 100, 100))
        
        self.size = texturas.roca
    
    def draw(self, screen, cam_x, cam_y):
        screen.blit(self._IMAGE, (self.x - cam_x, self.y - cam_y))
        
class Mineral_calcita:
    _IMAGE = None
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = texturas.calcita
        
        if Mineral_calcita._IMAGE is None:
            path = os.path.join('imagenes', 'objetos', 'calcita.png')
            try:
                img = pygame.image.load(path).convert_alpha()
                Mineral_calcita._IMAGE = pygame.transform.scale(img, (self.size, self.size))
            except:
                Mineral_calcita._IMAGE = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.rect(Mineral_calcita._IMAGE, texturas.rojo, (0, 0, self.size, self.size))

    def draw(self, screen, cam_x, cam_y):
        screen.blit(Mineral_calcita._IMAGE, (self.x - cam_x, self.y - cam_y))
        
class Hierro:
    _IMAGE = None
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = texturas.hierro
        
        if Hierro._IMAGE is None:
            path = os.path.join('imagenes', 'objetos', 'hierro.png')
            try:
                img = pygame.image.load(path).convert_alpha()
                Hierro._IMAGE = pygame.transform.scale(img, (self.size, self.size))
            except:
                Hierro._IMAGE = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.rect(Hierro._IMAGE, texturas.dorado, (0, 0, self.size, self.size))

    def draw(self, screen, cam_x, cam_y):
        screen.blit(Hierro._IMAGE, (self.x - cam_x, self.y - cam_y))
        
class Cristal:
    _IMAGE = None
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = texturas.cristal
        
        if Cristal._IMAGE is None:
            path = os.path.join('imagenes', 'objetos', 'cristal.png')
            try:
                img = pygame.image.load(path).convert_alpha()
                Cristal._IMAGE = pygame.transform.scale(img, (self.size, self.size))
            except:
                Cristal._IMAGE = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.rect(Cristal._IMAGE, texturas.morado, (0, 0, self.size, self.size))

    def draw(self, screen, cam_x, cam_y):
        screen.blit(Cristal._IMAGE, (self.x - cam_x, self.y - cam_y))


# Tamaño real de la nave (se actualiza al cargar la imagen)
_NAVE_WIDTH = 600
_NAVE_HEIGHT = 400

class Nave:
    _IMAGE = None
    _WIDTH = 600   # ← tamaño real guardado a nivel de clase
    _HEIGHT = 400

    def __init__(self, world_x, world_y):
        self.world_x = world_x
        self.world_y = world_y

        if Nave._IMAGE is None:
            nave_path = os.path.join('imagenes', 'objetos', 'nave.png')
            try:
                img = pygame.image.load(nave_path).convert_alpha()
                ancho_deseado = 600  # ← ajusta este valor al tamaño que quieras
                proporcion = ancho_deseado / img.get_width()
                alto_calculado = int(img.get_height() * proporcion)
                Nave._WIDTH = ancho_deseado
                Nave._HEIGHT = alto_calculado
                Nave._IMAGE = pygame.transform.scale(img, (Nave._WIDTH, Nave._HEIGHT))
                print(f"✓ Nave cargada: {Nave._WIDTH}x{Nave._HEIGHT}")
            except Exception as e:
                print(f"⚠️ No se encontró nave.png: {e}")
                Nave._IMAGE = pygame.Surface((Nave._WIDTH, Nave._HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(Nave._IMAGE, (100, 120, 150), [
                    (Nave._WIDTH//2, 0),
                    (0, Nave._HEIGHT),
                    (Nave._WIDTH, Nave._HEIGHT)
                ])
                pygame.draw.rect(Nave._IMAGE, (80, 100, 130),
                               (Nave._WIDTH//4, Nave._HEIGHT//2,
                                Nave._WIDTH//2, Nave._HEIGHT//2))
                pygame.draw.circle(Nave._IMAGE, (100, 200, 255),
                                 (Nave._WIDTH//2 - 20, Nave._HEIGHT//3), 8)
                pygame.draw.circle(Nave._IMAGE, (100, 200, 255),
                                 (Nave._WIDTH//2 + 20, Nave._HEIGHT//3), 8)

        # Siempre usa el tamaño de clase (correcto aunque ya estuviera cargada)
        self.width = Nave._WIDTH
        self.height = Nave._HEIGHT

        # Puerta: parte inferior central de la nave
        # Ajusta puerta_offset_x y puerta_offset_y si necesitas moverla
        self.puerta_ancho = 60
        self.puerta_alto = 40
        self.puerta_offset_x = -20    # ← + mueve derecha, - mueve izquierda
        self.puerta_offset_y = -130  # ← + baja, - sube (respecto al borde inferior)

        self.puerta_rect = pygame.Rect(
            self.world_x + self.width // 2 - self.puerta_ancho // 2 + self.puerta_offset_x,
            self.world_y + self.height - self.puerta_alto + self.puerta_offset_y,
            self.puerta_ancho,
            self.puerta_alto
        )

        # Posición de salida del jugador (debajo de la nave, centrado)
        self.salida_x = self.world_x + self.width // 2
        self.salida_y = self.world_y + self.height + 20  # 20px debajo de la nave

    def draw(self, screen, camera_x, camera_y, jugador_world_x=None, jugador_world_y=None):
        # Dibujar la nave
        screen.blit(Nave._IMAGE, (self.world_x - camera_x, self.world_y - camera_y))

        # Indicador verde de la puerta (útil para ajustar posición)
        puerta_screen = pygame.Rect(
            self.puerta_rect.x - camera_x,
            self.puerta_rect.y - camera_y,
            self.puerta_rect.width,
            self.puerta_rect.height
        )
        s = pygame.Surface((puerta_screen.width, puerta_screen.height), pygame.SRCALPHA)
        s.fill((0, 255, 0, 80))
        screen.blit(s, (puerta_screen.x, puerta_screen.y))

        # Texto "Presiona E para entrar": solo si el jugador está cerca
        mostrar_texto = True
        if jugador_world_x is not None and jugador_world_y is not None:
            import math
            dist = math.sqrt(
                (jugador_world_x - self.salida_x) ** 2 +
                (jugador_world_y - self.salida_y) ** 2
            )
            mostrar_texto = dist < 150  # ← distancia en píxeles para mostrar el texto

        if mostrar_texto:
            font = pygame.font.SysFont("Arial", 14, bold=True)
            text = font.render("Presiona E para entrar", True, (255, 255, 255))
            # Texto justo encima de la puerta
            text_rect = text.get_rect(center=(
                self.puerta_rect.x + self.puerta_ancho // 2 - camera_x,
                self.puerta_rect.y - 15 - camera_y
            ))
            # Fondo semi-transparente para el texto
            fondo = pygame.Surface((text.get_width() + 10, text.get_height() + 6), pygame.SRCALPHA)
            fondo.fill((0, 0, 0, 140))
            screen.blit(fondo, (text_rect.x - 5, text_rect.y - 3))
            screen.blit(text, text_rect)