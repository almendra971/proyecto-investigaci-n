import pygame
import math
import texturas

class Proyectil:
    def __init__(self, world_x, world_y, direccion_x, direccion_y, velocidad=10, color=texturas.amarillo, daño=10):
        # Posición en coordenadas del mundo
        self.world_x = world_x
        self.world_y = world_y
        
        # Dirección 
        magnitud = math.sqrt(direccion_x**2 + direccion_y**2)
        if magnitud > 0:
            self.dir_x = direccion_x / magnitud
            self.dir_y = direccion_y / magnitud
        else:
            self.dir_x = 1
            self.dir_y = 0
        
        self.velocidad = velocidad
        self.color = color
        self.daño = daño
        self.radio = 5  # Tamaño del proyectil
        self.activo = True
        self.distancia_recorrida = 0
        self.alcance_maximo = 500  # Distancia máxima antes de desaparecer
        
    def actualizar(self):
        # Actualiza la posición del proyectil
        if not self.activo:
            return
        
        # Mover en coordenadas del mundo
        self.world_x += self.dir_x * self.velocidad
        self.world_y += self.dir_y * self.velocidad
        
        # Contar distancia recorrida
        self.distancia_recorrida += self.velocidad
        
        # Desactivar si excede el alcance
        if self.distancia_recorrida >= self.alcance_maximo:
            self.activo = False
    
    def draw(self, screen, camera_x, camera_y):
        if not self.activo:
            return
        
        # Convertir coordenadas del mundo a pantalla
        screen_x = self.world_x - camera_x
        screen_y = self.world_y - camera_y
        
        if -20 < screen_x < texturas.width + 20 and -20 < screen_y < texturas.height + 20:
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radio)
            # Efecto de brillo 
            pygame.draw.circle(screen, texturas.blanco, (int(screen_x), int(screen_y)), self.radio // 2)
    
    def colisiona_con_punto(self, x, y, tamaño):
        return (self.world_x >= x and self.world_x <= x + tamaño and
                self.world_y >= y and self.world_y <= y + tamaño)
    
    def colisiona_con_objeto(self, objeto):
        # Verifica colisión con objetos del mundo
        dist = math.sqrt((self.world_x - (objeto.x + objeto.size/2))**2 + 
                        (self.world_y - (objeto.y + objeto.size/2))**2)
        return dist < (self.radio + objeto.size/2)


class ArmaLaser(Proyectil):
    """Proyectil tipo láser - más rápido y recto"""
    def __init__(self, world_x, world_y, direccion_x, direccion_y):
        super().__init__(world_x, world_y, direccion_x, direccion_y, 
                        velocidad=15, color=texturas.azul_claro, daño=15)
        self.radio = 3
        self.alcance_maximo = 700
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja láser con efecto de estela"""
        if not self.activo:
            return
        
        screen_x = self.world_x - camera_x
        screen_y = self.world_y - camera_y
        
        if -20 < screen_x < texturas.width + 20 and -20 < screen_y < texturas.height + 20:
            # Estela
            tail_x = screen_x - self.dir_x * 15
            tail_y = screen_y - self.dir_y * 15
            pygame.draw.line(screen, self.color, (tail_x, tail_y), (screen_x, screen_y), 2)
            # Punta brillante
            pygame.draw.circle(screen, texturas.blanco, (int(screen_x), int(screen_y)), self.radio)


class ArmaPlasma(Proyectil):
    #Proyectil tipo plasma, mas daño
    def __init__(self, world_x, world_y, direccion_x, direccion_y):
        super().__init__(world_x, world_y, direccion_x, direccion_y, 
                        velocidad=7, color=texturas.morado, daño=25)
        self.radio = 8
        self.alcance_maximo = 400
        self.brillo = 0
        
    def actualizar(self):
        super().actualizar()
        self.brillo = (self.brillo + 10) % 100  # Efecto 
    
    def draw(self, screen, camera_x, camera_y):
        if not self.activo:
            return
        
        screen_x = self.world_x - camera_x
        screen_y = self.world_y - camera_y
        
        if -20 < screen_x < texturas.width + 20 and -20 < screen_y < texturas.height + 20:
            radio_aura = self.radio + int(self.brillo / 20)
            s = pygame.Surface((radio_aura * 2, radio_aura * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, 50), (radio_aura, radio_aura), radio_aura)
            screen.blit(s, (int(screen_x) - radio_aura, int(screen_y) - radio_aura))
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radio)
            pygame.draw.circle(screen, texturas.blanco, (int(screen_x), int(screen_y)), self.radio // 2)


class GestorDisparos:
    def __init__(self):
        self.proyectiles = []
        self.armas_disponibles = {
            "Pistola": Proyectil,
            "Laser": ArmaLaser,
            "Plasma": ArmaPlasma
        }
        self.arma_actual = "Pistola"
        self.cooldown = 0
        self.cooldown_maximo = 15  # Frames entre disparos
        
    def cambiar_arma(self, nombre_arma):
        if nombre_arma in self.armas_disponibles:
            self.arma_actual = nombre_arma
            return True
        return False
    
    def disparar(self, personaje_world_x, personaje_world_y, mouse_x, mouse_y, camera_x, camera_y, personaje=None):
        #Crea un nuevo proyectil hacia la posición del mouse
        if self.cooldown > 0:
            return False
        
        costos_energia = {
            "Pistola": 2,   # Pistola gasta 2 de energía
            "Laser": 5,     # Láser gasta 5 de energía
            "Plasma": 10    # Plasma gasta 10 de energía
        }
        
        costo = costos_energia.get(self.arma_actual, 2)
        
        # Si se proporcionó el personaje, verificar y gastar energía
        if personaje is not None:
            if personaje.energy < costo:
                return False
            # Gastar energía
            personaje.update_energy(-costo)
        
        # Convertir posición del mouse a coordenadas del mundo
        mouse_world_x = mouse_x + camera_x
        mouse_world_y = mouse_y + camera_y
        
        # Calcular dirección desde el personaje hacia el mouse
        dir_x = mouse_world_x - personaje_world_x
        dir_y = mouse_world_y - personaje_world_y
        
        # Crear proyectil desde el centro del personaje
        clase_proyectil = self.armas_disponibles[self.arma_actual]
        proyectil = clase_proyectil(personaje_world_x + 10, personaje_world_y + 10, dir_x, dir_y)
        self.proyectiles.append(proyectil)
        
        # Activar cooldown
        self.cooldown = self.cooldown_maximo
        return True
    
    def actualizar(self):
        # Actualiza todos los proyectiles
        # Actualizar cooldown
        if self.cooldown > 0:
            self.cooldown -= 1
        
        # Actualizar proyectiles
        for proyectil in self.proyectiles:
            proyectil.actualizar()
        
        # Eliminar proyectiles inactivos
        self.proyectiles = [p for p in self.proyectiles if p.activo]
    
    def draw(self, screen, camera_x, camera_y):
        for proyectil in self.proyectiles:
            proyectil.draw(screen, camera_x, camera_y)
    
    def verificar_colisiones_objetos(self, objetos_lista, mundo):
        # Verifica colisiones con objetos del mundo y los destruye
        destruidos = []
        
        for proyectil in self.proyectiles:
            if not proyectil.activo:
                continue
            
            for obj in objetos_lista:
                if proyectil.colisiona_con_objeto(obj):
                    proyectil.activo = False
                    destruidos.append(obj)
                    break
        
        # Remover objetos destruidos del mundo
        for obj in destruidos:
            mundo.remover_objeto(obj)
        
        return len(destruidos)
    
    def limpiar(self):
        # Limpia todos los proyectiles
        self.proyectiles.clear()