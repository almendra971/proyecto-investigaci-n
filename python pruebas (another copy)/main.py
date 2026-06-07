import pygame 
import sys
from personajes_infinito import Personaje
import texturas
from mundo_infinito import WorldInfinito
from inventario import Inventory  
import personajes_infinito 
import objetos
from interfaz_nave import InterfazNave
from sistema_disparos import GestorDisparos
from personajes_infinito import GestorEnemigos    
pygame.init()
ventana = pygame.display.set_mode((texturas.width, texturas.height))
pygame.display.set_caption("Mi Juego - Mundo Infinito")

def dibujar_texto(surface, texto, tamaño, x, y, color=texturas.blanco):
    font = pygame.font.SysFont(None, tamaño)
    render = font.render(texto, True, color)
    rect = render.get_rect(center=(x, y))
    surface.blit(render, rect)

def dibujar_boton(surface, texto, x, y, w, h, color=texturas.azul, texto_color=texturas.blanco):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, color, rect, border_radius=10)
    font = pygame.font.SysFont("Arial", 30)
    render = font.render(texto, True, texto_color)
    texto_rect = render.get_rect(center=rect.center)
    surface.blit(render, texto_rect)
    return rect

def main():
    clock = pygame.time.Clock()
    mundo = WorldInfinito(texturas.width, texturas.height)
    
    # Posición fija de la nave en el mundo
    nave = objetos.Nave(world_x=500, world_y=500)
    
    # ← CAMBIADO: El personaje aparece junto a la nave
    personaje = Personaje(nave.world_x + 50, nave.world_y + 50)  # Ligeramente desplazado de la nave
    
    inventario = Inventory(texturas.width, texturas.height)
    interfaz_nave = InterfazNave(texturas.width, texturas.height)
    gestor_disparos = GestorDisparos()
    gestor_enemigos = GestorEnemigos()  # ← NUEVO
    
    # Items iniciales
    inventario.agregar_item("Pico", 1)
    inventario.agregar_item("Combustible", 10)
    inventario.agregar_item("Calcita", 5)  # Para pruebas

    dialogos = [
        "Escribe tu nombre (usa ENTER para continuar)...",
        "Soy , la IA que te guiará en tu misión.",
        "Has sido elegido para pilotar hacia XH-3892...",
        "Debes encontrar rastros del anterior viaje de exploración.",
        "¿Deseas dirigir la misión?",
        "Usa n para NO   |   y para SI"
    ]

    indice = 0
    mostrar_dialogos = True
    capturando_nombre = True
    mostrar_nave = False
    mostrar_mundo = False
    nombre = ""
    boton_panel = None
    state_update_timer = 0

    while True:
        dt = clock.tick(60) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                inventario.guardar_inventario("partida_guardada.json")
                pygame.quit()
                sys.exit()

            # interfaz de la nave
            if mostrar_nave and not mostrar_mundo:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    resultado = interfaz_nave.manejar_click(event.pos, personaje, inventario)
                    if resultado == 'salir':
                        mostrar_nave = False
                        mostrar_mundo = True
                    elif resultado == 'descansar':
                        personaje.energy = 100
                        personaje.food = 100
                        personaje.instamina = 100
                        mundo.tiempo_inicio_dia = pygame.time.get_ticks() 

            # Mundo
            elif mostrar_mundo:
                inventario.handle_event(event)
    
                if event.type == pygame.KEYDOWN:
                    # Minar (Tecla E)
                    if event.key == pygame.K_e:
                        item_en_mano = inventario.get_item_seleccionado()
                        pico_equipado = item_en_mano is not None and item_en_mano.nombre == "Pico"
                        objetos_cercanos = mundo.obtener_objetos_cercanos(personaje.world_x, personaje.world_y, radio=60)
  
                        # Calcita (Necesita Pico)
                        for c in objetos_cercanos['calcita']:
                            if personaje.esta_cerca(c, mundo):
                                if pico_equipado:
                                    if inventario.agregar_item("Calcita", 1):
                                        mundo.remover_objeto(c)
                                        print("✓ Calcita minada")
                                    else: print("⚠ Inventario lleno")
                                else: print("¡Necesitas el Pico!")
                                break
                            
                        else:
                            # Rocas
                            for r in objetos_cercanos['rocas']:
                                if personaje.esta_cerca(r, mundo):
                                    if pico_equipado:
                                        inventario.agregar_item("Roca", 1)
                                        mundo.remover_objeto(r)
                                    else: print("Necesitas un pico")
                                    break
                            else: 
                            #hierro 
                                for h in objetos_cercanos['hierros']:
                                    if personaje.esta_cerca(h, mundo):
                                        if pico_equipado:
                                            inventario.agregar_item("Hierro", 1)
                                            mundo.remover_objeto(h)
                                    break
                                else: 
                                #cristal 
                                    for cr in objetos_cercanos['cristales']:
                                        if personaje.esta_cerca(cr, mundo):
                                            if pico_equipado:
                                                inventario.agregar_item("Cristal", 1)
                                                mundo.remover_objeto(cr)
                                                                    
                        personaje_rect = pygame.Rect(texturas.width // 2, texturas.height // 2, personaje.size, personaje.size)
                        if personaje_rect.colliderect(nave.puerta_rect.move(-mundo.camera_x, -mundo.camera_y)):
                            mostrar_mundo = False
                            mostrar_nave = True
       
                    
                    # usar combustible (Tecla R)
                    if event.key == pygame.K_r:
                        # Usamos el método que descuenta 1 del inventario
                        item_usado = inventario.usar_consumible()
                        if item_usado == "Combustible":
                            personaje.update_energy(25) # Recarga 25 de energía
                        

                    # gastar comida o instamina para regenerar energía (Teclas F y T)
                    if event.key == pygame.K_f:
                        personaje.update_food(20)
                    if event.key == pygame.K_t:
                        personaje.update_instamina(20)
                    
                    # ← NUEVO: Cambiar arma con teclas 1, 2, 3
                    if event.key == pygame.K_1:
                        gestor_disparos.cambiar_arma("Pistola")
                        print("Arma: Pistola")
                    if event.key == pygame.K_2:
                        gestor_disparos.cambiar_arma("Laser")
                        print("Arma: Láser")
                    if event.key == pygame.K_3:
                        gestor_disparos.cambiar_arma("Plasma")
                        print("Arma: Plasma")
                
                # ← NUEVO: Disparar con click del mouse
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Click izquierdo
                        mouse_x, mouse_y = event.pos
                        gestor_disparos.disparar(
                            personaje.world_x, 
                            personaje.world_y,
                            mouse_x, 
                            mouse_y,
                            mundo.camera_x,
                            mundo.camera_y,
                            personaje  # Pasamos el personaje para gastar energía
                        )
            
            # Lógica de Diálogos
            if mostrar_dialogos:
                if capturando_nombre:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if len(nombre.strip()) > 0:
                                capturando_nombre = False
                                indice = 1
                        elif event.key == pygame.K_BACKSPACE:
                            nombre = nombre[:-1]
                        else:
                            nombre += event.unicode
                elif 1 <= indice <= 4:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        indice += 1
                elif indice == 5:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_n:
                            pygame.quit()
                            sys.exit()
                        elif event.key == pygame.K_y:
                            mostrar_dialogos = False
                            mostrar_nave = True

        # --- DIBUJO ---
        if mostrar_dialogos:
            ventana.fill((0, 0, 0))
            if capturando_nombre:
                dibujar_texto(ventana, dialogos[0], 35, texturas.width // 2, texturas.height // 2 - 40)
                dibujar_texto(ventana, nombre, 40, texturas.width // 2, texturas.height // 2)
            else:
                # Insertar nombre en el diálogo de la IA
                texto_actual = dialogos[indice].replace("Soy ,", f"Soy {nombre},") if indice == 1 else dialogos[indice]
                dibujar_texto(ventana, texto_actual, 35, texturas.width // 2, texturas.height // 2)

        elif mostrar_nave and not mostrar_mundo:
            # ===== NUEVA INTERFAZ DE NAVE =====
            interfaz_nave.dibujar(ventana, personaje, inventario)
        
        
        elif mostrar_mundo:
            ventana.fill((0, 0, 0))
            mundo.actualizar(personaje.world_x, personaje.world_y)
            mundo.draw(ventana, personaje.world_x, personaje.world_y)
            nave.draw(ventana, mundo.camera_x, mundo.camera_y)
            personaje.draw(ventana)
            
            # Actualizar sistema de disparos
            gestor_disparos.actualizar()
            
            # Actualizar enemigos
            gestor_enemigos.actualizar(personaje.world_x, personaje.world_y, personaje, mundo)
            
            # Verificar colisiones con rocas
            objetos_cercanos = mundo.obtener_objetos_cercanos(personaje.world_x, personaje.world_y, radio=800)
            rocas_destruidas = gestor_disparos.verificar_colisiones_objetos(objetos_cercanos['rocas'], mundo)
            
            # colisiones proyectiles vs enemigos
            enemigos_muertos = gestor_enemigos.verificar_colisiones_proyectiles(gestor_disparos, inventario)
            
            #Dibujar proyectiles
            gestor_disparos.draw(ventana, mundo.camera_x, mundo.camera_y)
            
            # Dibujar enemigos
            gestor_enemigos.draw(ventana, mundo.camera_x, mundo.camera_y)

            # Movimiento
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            paso = 5
            if keys[pygame.K_a]: dx -= paso
            if keys[pygame.K_d]: dx += paso
            if keys[pygame.K_w]: dy -= paso
            if keys[pygame.K_s]: dy += paso
            if dx != 0 or dy != 0:
                personaje.move(dx, dy, mundo)
            
            
            # Actualización de estado (Hambre/Estamina)
            state_update_timer += dt
            if state_update_timer >= texturas.interval_update:
                personaje.update_food(-1)
                personaje.update_instamina(-1)
                state_update_timer = 0

            if personaje.energy <= 0 or personaje.food <= 0 or personaje.instamina <= 0:
                print("Game Over")
                pygame.quit()
                sys.exit()

            # UI e Instrucciones
            font_instruc = pygame.font.SysFont("Arial", 14)
            ventana.blit(font_instruc.render("1-0: Hotbar | R: Usar Combustible", True, (150, 255, 150)), (570, 565))
            ventana.blit(font_instruc.render("E: Recoger | I: Inventario", True, (150, 255, 150)), (570, 550))
            ventana.blit(font_instruc.render("Click: Disparar | 1,2,3: Cambiar arma", True, (255, 150, 150)), (570, 535))  # ← NUEVO
            
            # Debug Info
            font_coords = pygame.font.SysFont("Arial", 12)
            ventana.blit(font_coords.render(f"Pos: ({int(personaje.world_x)}, {int(personaje.world_y)})", True, (255, 255, 255)), (10, 10))
            
            # ← NUEVO: Indicador de arma actual
            font_arma = pygame.font.SysFont("Arial", 16, bold=True)
            texto_arma = f"Arma: {gestor_disparos.arma_actual}"
            ventana.blit(font_arma.render(texto_arma, True, texturas.amarillo), (10, 80))
            
            # ← NUEVO: Estadísticas de enemigos
            stats = gestor_enemigos.get_stats()
            ventana.blit(font_coords.render(f"Enemigos: {stats['enemigos_activos']}", True, (255, 100, 100)), (10, 100))
            ventana.blit(font_coords.render(f"Eliminados: {stats['enemigos_eliminados']}", True, (100, 255, 100)), (10, 115))
            ventana.blit(font_coords.render(f"Oleada: {stats['oleada']}", True, (100, 200, 255)), (10, 130))
            ventana.blit(font_coords.render(f"Dificultad: {stats['dificultad']:.1f}x", True, (255, 200, 100)), (10, 145))
            
            # Reloj funcional
            tiempo_actual = pygame.time.get_ticks() - mundo.tiempo_inicio_dia
            segundos_totales = tiempo_actual // 1000
            horas = (segundos_totales // 3600) % 24
            minutos = (segundos_totales // 60) % 60
            segundos = segundos_totales % 60
            ventana.blit(font_coords.render(f"Reloj: {horas:02}:{minutos:02}:{segundos:02}", True, (255, 255, 255)), (10, 40))

            inventario.draw(ventana)
      
        pygame.display.flip()

if __name__ == "__main__":
    main()