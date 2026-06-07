import pygame
import texturas

class InterfazNave:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.boton_descansar = None
        
        # Colores
        self.color_fondo = (15, 15, 25)
        self.color_panel = (30, 30, 45)
        self.color_borde = (70, 130, 180)
        self.color_texto = (200, 220, 255)
        self.color_boton = (50, 80, 120)
        self.color_boton_hover = (70, 110, 160)
        self.color_energia_baja = (255, 80, 80)
        self.color_energia_media = (255, 200, 80)
        self.color_energia_alta = (80, 255, 120)
        
        # Botones
        self.boton_salir = None
        self.boton_panel = None
        
    def dibujar(self, screen, personaje, inventario):
        screen.fill(self.color_fondo)
        
        # Título
        self._dibujar_titulo(screen)
        
        # Panel de estado del personaje
        self._dibujar_estado_personaje(screen, personaje)
        
        # Panel de inventario resumido
        self._dibujar_inventario_resumido(screen, inventario)
        
        # Botones
        self._dibujar_botones(screen)
        
    def _dibujar_titulo(self, screen):
        # Dibuja el título de la nave
        font_titulo = pygame.font.SysFont("Arial", 48, bold=True)
        titulo = font_titulo.render("NAVE EXPLORADORA", True, self.color_borde)
        titulo_rect = titulo.get_rect(center=(self.screen_width // 2, 60))
        screen.blit(titulo, titulo_rect)
        
        font_subtitulo = pygame.font.SysFont("Arial", 20)
        subtitulo = font_subtitulo.render("Panel de Control", True, self.color_texto)
        subtitulo_rect = subtitulo.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(subtitulo, subtitulo_rect)
        
    def _dibujar_estado_personaje(self, screen, personaje):
        # Dibuja el panel con los estados del personaje
        panel_x = 50
        panel_y = 150
        panel_w = 350
        panel_h = 300
        
        # Fondo del panel
        pygame.draw.rect(screen, self.color_panel, (panel_x, panel_y, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(screen, self.color_borde, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=10)
        
        # Título del panel
        font_panel = pygame.font.SysFont("Arial", 24, bold=True)
        titulo_panel = font_panel.render("ESTADO DEL PILOTO", True, self.color_texto)
        screen.blit(titulo_panel, (panel_x + 20, panel_y + 15))
        
        # Barras de estado
        font_estado = pygame.font.SysFont("Arial", 18)
        y_offset = panel_y + 60
        
        # Energía
        self._dibujar_barra(screen, "ENERGÍA", personaje.energy, 100, 
                           panel_x + 20, y_offset, 310, self._color_energia(personaje.energy))
        y_offset += 70
        
        # Comida
        self._dibujar_barra(screen, "COMIDA", personaje.food, 100, 
                           panel_x + 20, y_offset, 310, (255, 200, 80))
        y_offset += 70
        
        # Estamina
        self._dibujar_barra(screen, "ESTAMINA", personaje.instamina, 100, 
                           panel_x + 20, y_offset, 310, (80, 200, 255))
        
    def _dibujar_barra(self, screen, nombre, valor, max_valor, x, y, ancho, color):
        """Dibuja una barra de estado con su nombre y valor"""
        font = pygame.font.SysFont("Arial", 16)
        
        # Nombre
        texto_nombre = font.render(nombre, True, self.color_texto)
        screen.blit(texto_nombre, (x, y))
        
        # Valor numérico
        texto_valor = font.render(f"{int(valor)}/{max_valor}", True, self.color_texto)
        screen.blit(texto_valor, (x + ancho - 60, y))
        
        # Barra de fondo
        barra_y = y + 25
        pygame.draw.rect(screen, (40, 40, 50), (x, barra_y, ancho, 20), border_radius=5)
        
        # Barra de valor
        porcentaje = max(0, min(1, valor / max_valor))
        if porcentaje > 0:
            pygame.draw.rect(screen, color, (x, barra_y, int(ancho * porcentaje), 20), border_radius=5)
        
        # Borde
        pygame.draw.rect(screen, self.color_borde, (x, barra_y, ancho, 20), 2, border_radius=5)
        
    def _color_energia(self, energia):
        if energia > 60:
            return self.color_energia_alta
        elif energia > 30:
            return self.color_energia_media
        else:
            return self.color_energia_baja
            
    def _dibujar_inventario_resumido(self, screen, inventario):
        panel_x = 450
        panel_y = 150
        panel_w = 350
        panel_h = 300
        
        # Fondo del panel
        pygame.draw.rect(screen, self.color_panel, (panel_x, panel_y, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(screen, self.color_borde, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=10)
        
        # Título
        font_panel = pygame.font.SysFont("Arial", 24, bold=True)
        titulo = font_panel.render("RECURSOS", True, self.color_texto)
        screen.blit(titulo, (panel_x + 20, panel_y + 15))
        
        # Contar items
        recursos = {}
        for item in inventario.hotbar + inventario.slots_inventario:
            if item:
                if item.nombre in recursos:
                    recursos[item.nombre] += item.cantidad
                else:
                    recursos[item.nombre] = item.cantidad
        
        # Mostrar recursos
        font_recurso = pygame.font.SysFont("Arial", 16)
        y_offset = panel_y + 60
        
        if recursos:
            for nombre, cantidad in sorted(recursos.items()):
                texto = font_recurso.render(f"{nombre}: {cantidad}", True, self.color_texto)
                screen.blit(texto, (panel_x + 30, y_offset))
                y_offset += 30
                
                if y_offset > panel_y + panel_h - 30:
                    break
        else:
            texto = font_recurso.render("Sin recursos", True, (150, 150, 150))
            screen.blit(texto, (panel_x + 30, y_offset))
            
    def _dibujar_botones(self, screen):
       mouse_pos = pygame.mouse.get_pos()
       boton_y = self.screen_height - 120  # Dibuja los botones de la interfaz

    # Botón descansar (izquierda)
       self.boton_descansar = self._dibujar_boton(
       screen, "DESCANSAR", self.screen_width // 2 - 320, boton_y, 280, 60, mouse_pos,
       color_base=(40, 90, 60), color_hover=(60, 130, 80)
    )

    # Botón salir al mundo (derecha)
       self.boton_salir = self._dibujar_boton(screen, "SALIR AL EXTERIOR", self.screen_width // 2 + 40, boton_y, 280, 60,
        mouse_pos, color_base=texturas.rosa, color_hover=texturas.verde_suave
       )

    def _dibujar_boton(self, screen, texto, x, y, w, h, mouse_pos, color_base=None, color_hover=None):
        rect = pygame.Rect(x, y, w, h)
        base = color_base if color_base else self.color_boton
        hover = color_hover if color_hover else self.color_boton_hover
        color = hover if rect.collidepoint(mouse_pos) else base

        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, self.color_borde, rect, 3, border_radius=10)

        font = pygame.font.SysFont("Arial", 24, bold=True)
        texto_render = font.render(texto, True, self.color_texto)
        texto_rect = texto_render.get_rect(center=rect.center)
        screen.blit(texto_render, texto_rect)
        return rect
        
    def manejar_click(self, pos, personaje, inventario):
        # Maneja los clicks en la interfaz
        if self.boton_salir and self.boton_salir.collidepoint(pos):
            return 'salir'
        
        
        if self.boton_descansar and self.boton_descansar.collidepoint(pos):
            return 'descansar'
        
        return None