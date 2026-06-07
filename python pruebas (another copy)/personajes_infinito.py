import pygame
import texturas
import math
import random 
import inventario 

class Personaje:
    def __init__(self, x, y):
        # Posición absoluta en el mundo
        self.world_x = x
        self.world_y = y
        
        # Posición en el centro de la pantalla
        self.screen_x = texturas.width // 2
        self.screen_y = texturas.height // 2
        
        self.size = 20 
        self.inventory = {"Roca": 0, "Calcita": 0, "Hierro": 0, "Cristal": 0} 

        self.food = texturas.food_max
        self.energy = texturas.energy_max
        self.instamina = texturas.instamina
        
    def draw(self, screen): 
        # Dibujar al personaje en el centro
        pygame.draw.rect(screen, texturas.negro, (self.screen_x, self.screen_y, self.size, self.size))
        # Dibujar las barras de estadisticas
        self.draw_bar(screen)
            
    def move(self, dx, dy, mundo_infinito):
        # colisiones
        nueva_world_x = self.world_x + dx
        nueva_world_y = self.world_y + dy

        objetos = mundo_infinito.obtener_objetos_cercanos(self.world_x, self.world_y, radio=100)
        
        colision = False
        # Verificar colisiones con rocas
        for roca in objetos['rocas']:
            if self.check_collision_world(nueva_world_x, nueva_world_y, roca):
                colision = True
                break
        
        if not colision:
            self.world_x = nueva_world_x
            self.world_y = nueva_world_y
            # Actualizar chunks basado en la nueva posición de mundo
            mundo_infinito.actualizar(self.world_x, self.world_y)

        self.update_energy(-0.05)
            
    def check_collision_world(self, p_world_x, p_world_y, obj):
        # Detección de colisión usando coordenadas globales
        return (p_world_x < obj.x + obj.size and 
                p_world_x + self.size > obj.x and 
                p_world_y < obj.y + obj.size and 
                p_world_y + self.size > obj.y)
            
    def esta_cerca(self, objeto, mundo_infinito, distancia=40):
        
        p_centro_x = self.world_x + self.size / 2
        p_centro_y = self.world_y + self.size / 2
        
        o_centro_x = objeto.x + objeto.size / 2
        o_centro_y = objeto.y + objeto.size / 2
        
        dist = math.sqrt((p_centro_x - o_centro_x)**2 + (p_centro_y - o_centro_y)**2)
        return dist < distancia
    
    def recolectar(self, lista_objetos, inventario_sistema, nombre_item, mundo_infinito):
        # Lógica de recolección para mundo infinito
        for objeto in lista_objetos[:]:
            if self.esta_cerca(objeto, mundo_infinito):
                if inventario_sistema.agregar_item(nombre_item, 1):
                    mundo_infinito.remover_objeto(objeto)
                    print(f"Recogido: {nombre_item}")
                    return True
        return False

    def update_energy(self, amount):
        self.energy = max(0, min(self.energy + amount, texturas.energy_max))
        
    def update_food(self, amount):
        self.food = max(0, min(self.food + amount, texturas.food_max))

    def update_instamina(self, amount):
        self.instamina = max(0, min(self.instamina + amount, texturas.instamina))

    def update_state(self):
        self.update_food(-0.01) #Actualiza las barras de estadisticas con el tiempo
        self.update_instamina(-0.02)

        if self.food < texturas.food_max * 0.2 or self.instamina < texturas.instamina * 0.2:
            self.update_energy(-0.05)
        else:
            self.update_energy(0.01)

    def draw_bar(self, screen):
        # Dibuja todas las barras de estado
        bar_width = 100
        bar_height = 10
        x_offset = 10
        y_offset = 550
        
        #  Barra Energía
        pygame.draw.rect(screen, texturas.background, (x_offset, y_offset, bar_width, bar_height))
        ancho_e = bar_width * (self.energy / texturas.energy_max)
        pygame.draw.rect(screen, texturas.color_energy, (x_offset, y_offset, ancho_e, bar_height))
        
        #  Barra Comida (Recuperada)
        y_offset += 15
        pygame.draw.rect(screen, texturas.background, (x_offset, y_offset, bar_width, bar_height))
        ancho_f = bar_width * (self.food / texturas.food_max)
        pygame.draw.rect(screen, texturas.color_food, (x_offset, y_offset, ancho_f, bar_height))

        #  Barra Instamina (Recuperada)
        y_offset += 15
        pygame.draw.rect(screen, texturas.background, (x_offset, y_offset, bar_width, bar_height))
        ancho_i = bar_width * (self.instamina / texturas.instamina) 
        pygame.draw.rect(screen, texturas.color_instamina, (x_offset, y_offset, ancho_i, bar_height))

class Enemigo:
    def __init__(self, world_x, world_y, tipo="basico"):
        self.world_x = world_x
        self.world_y = world_y
        self.tipo = tipo
        self.activo = True
        
        # Estadísticas según tipo
        stats = {
            "basico": {"vida": 30, "velocidad": 1.5, "daño": 5, "color": (150, 50, 50), "size": 25},
            "rapido": {"vida": 20, "velocidad": 3.0, "daño": 3, "color": (255, 100, 0), "size": 20},
            "tanque": {"vida": 80, "velocidad": 0.8, "daño": 10, "color": (100, 50, 150), "size": 35},
            "explosivo": {"vida": 15, "velocidad": 2.0, "daño": 20, "color": (255, 50, 50), "size": 22}
        }
        
        stat = stats.get(tipo, stats["basico"])
        self.vida_max = stat["vida"]
        self.vida = stat["vida"]
        self.velocidad = stat["velocidad"]
        self.daño = stat["daño"]
        self.color = stat["color"]
        self.size = stat["size"]
        
        drops = {
    "basico":    {"drop_chance": 0.6, "drop_cantidad": 1},
    "rapido":    {"drop_chance": 0.4, "drop_cantidad": 1},
    "tanque":    {"drop_chance": 0.9, "drop_cantidad": 3},
    "explosivo": {"drop_chance": 0.7, "drop_cantidad": 2}
}
        drop_info = drops.get(tipo, drops["basico"])
        self.drop_chance = drop_info["drop_chance"]
        self.drop_cantidad = drop_info["drop_cantidad"]

        # comportamiento
        self.target_x = None
        self.target_y = None
        self.rango_deteccion = 400  # Detecta al jugador a 400 píxeles
        self.rango_ataque = 30  # Ataca cuando está a 30 píxeles
        self.cooldown_ataque = 0
        self.cooldown_max = 60  # 1 segundo entre ataques
        
        # Animación
        self.angulo = 0
        self.pulso = 0
        
    def recibir_daño(self, cantidad):
        #Reduce la vida del enemigo
        self.vida -= cantidad
        if self.vida <= 0:
            self.activo = False
            return True  # Enemigo murió
        return False
    
    def detectar_jugador(self, jugador_x, jugador_y):
        #Verifica si el jugador está en su visonm
        dist = math.sqrt((self.world_x - jugador_x)**2 + (self.world_y - jugador_y)**2)
        if dist <= self.rango_deteccion:
            self.target_x = jugador_x
            self.target_y = jugador_y
            return True
        return False
    
    def mover_hacia_jugador(self, jugador_x, jugador_y, mundo):
        if self.target_x is None or self.target_y is None:
            return
        
        # Calcular dirección
        dx = self.target_x - self.world_x
        dy = self.target_y - self.world_y
        distancia = math.sqrt(dx**2 + dy**2)
        
        if distancia > self.rango_ataque:
            if distancia > 0:
                dx = (dx / distancia) * self.velocidad
                dy = (dy / distancia) * self.velocidad
                
                # Actualizar posición 
                self.world_x += dx
                self.world_y += dy
    
    def puede_atacar(self, jugador_x, jugador_y):
        if self.cooldown_ataque > 0:
            return False
        
        dist = math.sqrt((self.world_x - jugador_x)**2 + (self.world_y - jugador_y)**2)
        return dist <= self.rango_ataque
    
    def atacar(self, personaje):
        personaje.update_energy(-self.daño)
        self.cooldown_ataque = self.cooldown_max
        
        # Si es explosivo, muere al atacar
        if self.tipo == "explosivo":
            self.activo = False
        
        return True
    
    def actualizar(self, jugador_x, jugador_y, personaje, mundo):
        #Actualiza los enemigos cada frame 
        if not self.activo:
            return
        
        # Reducir cooldown
        if self.cooldown_ataque > 0:
            self.cooldown_ataque -= 1
        
        # Detectar y perseguir jugador
        if self.detectar_jugador(jugador_x, jugador_y):
            # Calcular distancia actual al jugador
            dist = math.sqrt((self.world_x - jugador_x)**2 + (self.world_y - jugador_y)**2)
            
            # Si está en rango de ataque
            if dist <= self.rango_ataque:
                if self.cooldown_ataque == 0:
                    self.atacar(personaje)
            else:
                # Si no está en rango, moverse hacia él
                self.mover_hacia_jugador(jugador_x, jugador_y, mundo)
        
        # Animación
        self.angulo = (self.angulo + 2) % 360
        self.pulso = (self.pulso + 1) % 60
    
    def draw(self, screen, camera_x, camera_y):
        if not self.activo:
            return
        
        screen_x = self.world_x - camera_x
        screen_y = self.world_y - camera_y
        
        # Solo dibujar si está visible
        if -50 < screen_x < texturas.width + 50 and -50 < screen_y < texturas.height + 50:
            # Efecto de pulso para explosivos
            size_actual = self.size
            if self.tipo == "explosivo":
                size_actual = self.size + int(math.sin(self.pulso / 10) * 3)
            
            # Color del cuerpo (rojo si está atacando)
            color_actual = self.color
            if self.cooldown_ataque > self.cooldown_max - 10:  # Recién atacó
                # Mezclar con rojo brillante
                color_actual = (
                    min(255, self.color[0] + 100),
                    max(0, self.color[1] - 50),
                    max(0, self.color[2] - 50)
                )
            
            # Cuerpo del enemigo
            pygame.draw.circle(screen, color_actual, (int(screen_x), int(screen_y)), size_actual // 2)
            
            # Ojos (para darle personalidad)
            eye_offset = size_actual // 4
            eye_size = size_actual // 8
            pygame.draw.circle(screen, texturas.negro, 
                             (int(screen_x - eye_offset), int(screen_y - eye_offset)), eye_size)
            pygame.draw.circle(screen, texturas.negro, 
                             (int(screen_x + eye_offset), int(screen_y - eye_offset)), eye_size)
            
            # Barra de vida
            barra_width = self.size
            barra_height = 4
            barra_x = screen_x - barra_width // 2
            barra_y = screen_y - self.size // 2 - 10
            
            # Fondo de la barra
            pygame.draw.rect(screen, texturas.gris_oscuro, 
                           (barra_x, barra_y, barra_width, barra_height))
            # Vida actual
            vida_porcentaje = self.vida / self.vida_max
            pygame.draw.rect(screen, texturas.rojo, 
                           (barra_x, barra_y, barra_width * vida_porcentaje, barra_height))


class GestorEnemigos:
    def __init__(self):
        self.enemigos = []
        self.tiempo_spawn = 0
        self.intervalo_spawn_base = 600  # Frames entre spawns (10 segundos a 60 FPS)
        self.intervalo_spawn_actual = self.intervalo_spawn_base
        self.dificultad = 1  # Aumenta con el tiempo
        self.tiempo_juego = 0  # En frames
        self.enemigos_eliminados = 0
        
        # Configuración de oleadas
        self.oleada_actual = 1
        self.enemigos_por_oleada = 3
        self.tiempo_entre_oleadas = 1800  # 30 segundos
        self.tiempo_proxima_oleada = self.tiempo_entre_oleadas
        
    def actualizar_dificultad(self):
        self.tiempo_juego += 1
        
        # Cada 3 minutos (10800 frames) aumenta la dificultad
        if self.tiempo_juego % 10800 == 0:
            self.dificultad += 0.5
            self.intervalo_spawn_actual = max(180, int(self.intervalo_spawn_base / self.dificultad))
            
    
    def spawn_enemigo_aleatorio(self, jugador_x, jugador_y):
        # Distancia del spawn (entre 300 y 500 píxeles del jugador)
        angulo = random.uniform(0, 2 * math.pi)
        distancia = random.uniform(300, 500)
        
        spawn_x = jugador_x + math.cos(angulo) * distancia
        spawn_y = jugador_y + math.sin(angulo) * distancia
        
        # Elegir tipo según dificultad
        tipos_disponibles = ["basico"]
        
        if self.dificultad >= 1.5:
            tipos_disponibles.append("rapido")
        if self.dificultad >= 2.5:
            tipos_disponibles.append("tanque")
        if self.dificultad >= 3.5:
            tipos_disponibles.append("explosivo")
        
        tipo = random.choice(tipos_disponibles)
        enemigo = Enemigo(spawn_x, spawn_y, tipo)
        self.enemigos.append(enemigo)
    
    def spawn_oleada(self, jugador_x, jugador_y):
        # oleada de enemigos
        cantidad = int(self.enemigos_por_oleada * self.dificultad)
        for _ in range(cantidad):
            self.spawn_enemigo_aleatorio(jugador_x, jugador_y)
        
        self.oleada_actual += 1
        self.tiempo_proxima_oleada = self.tiempo_juego + self.tiempo_entre_oleadas
    
    def actualizar(self, jugador_x, jugador_y, personaje, mundo):
        # Actualiza todos los enemigos y spawn
        self.actualizar_dificultad()
        
        # Sistema de oleadas
        if self.tiempo_juego >= self.tiempo_proxima_oleada:
            self.spawn_oleada(jugador_x, jugador_y)
        
        # Spawn continuo entre oleadas
        self.tiempo_spawn += 1
        if self.tiempo_spawn >= self.intervalo_spawn_actual:
            self.spawn_enemigo_aleatorio(jugador_x, jugador_y)
            self.tiempo_spawn = 0
        
        # Actualizar cada enemigo
        for enemigo in self.enemigos:
            enemigo.actualizar(jugador_x, jugador_y, personaje, mundo)
        
        # Eliminar enemigos muertos
        antes = len(self.enemigos)
        self.enemigos = [e for e in self.enemigos if e.activo]
        eliminados = antes - len(self.enemigos)
        if eliminados > 0:
            self.enemigos_eliminados += eliminados
    
    def draw(self, screen, camera_x, camera_y):
        for enemigo in self.enemigos:
            enemigo.draw(screen, camera_x, camera_y)
    
    def verificar_colisiones_proyectiles(self, gestor_disparos, inventario=None):
        enemigos_muertos = 0
        
        for proyectil in gestor_disparos.proyectiles:
            if not proyectil.activo:
                continue
            
            for enemigo in self.enemigos:
                if not enemigo.activo:
                    continue
                
                # Calcular distancia
                dist = math.sqrt((proyectil.world_x - enemigo.world_x)**2 + 
                               (proyectil.world_y - enemigo.world_y)**2)
                
                if dist < (proyectil.radio + enemigo.size // 2):
                    # Colisión detectada
                    proyectil.activo = False
                    murio = enemigo.recibir_daño(proyectil.daño)
                    if murio:
                        enemigos_muertos += 1


                        if inventario and random.random() < enemigo.drop_chance:
                            cantidad = random.randint(1, enemigo.drop_cantidad)
                            
                                
                    break
        
        return enemigos_muertos
    
    def get_stats(self):
        return {
            "enemigos_activos": len(self.enemigos),
            "enemigos_eliminados": self.enemigos_eliminados,
            "dificultad": self.dificultad,
            "oleada": self.oleada_actual
        }
    
    def limpiar(self):
        # Limpia todos los enemigos
        self.enemigos.clear()