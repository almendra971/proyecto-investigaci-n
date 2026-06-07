import pygame
import json
import texturas

class Item:
    def __init__(self, nombre, tipo, max_stack=999, icono=None, descripcion="", simbolo=None):
        self.nombre = nombre
        self.tipo = tipo  
        self.max_stack = max_stack
        self.icono = icono
        self.descripcion = descripcion
        self.cantidad = 1
        self.simbolo = simbolo if simbolo else nombre[0]
         
    def copy(self):
        nuevo = Item(self.nombre, self.tipo, self.max_stack, self.icono, self.descripcion, self.simbolo)
        nuevo.cantidad = self.cantidad
        return nuevo

class Inventory:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # crafteo
        self.crafting_grid = [[None for _ in range(texturas.craft_grid_size)] for _ in range(texturas.craft_grid_size)]
        self.craft_result = None
        
        # Definición de recetas (Patrón 3x3)
        self.recetas_crafting = {
            'combustible': {
                'patron': [
                    ['hierro', 'cristal', None],
                    [None, None, None],
                    [None, None, None]
                ],
                'resultado': 'Combustible',
                'cantidad': 1
            }
        }

        # --- INVENTARIO Y UI ---
        self.slots_inventario = [None] * 40
        self.hotbar = [None] * 10
        self.hotbar_seleccionado = 0
        self.visible = False
        self.slot_size = 25
        self.padding = 4
        self.slots_por_fila = 10
        
        # Drag & Drop
        self.dragging = False
        self.dragged_item = None
        self.dragged_from = None  
        
        # Tooltip
        self.tooltip_item = None
        self.tooltip_pos = (0, 0)
        
        # Colores
        self.color_fondo = (40, 40, 60)
        self.color_slot = (26, 26, 46)
        self.color_slot_hover = (52, 52, 76)
        self.color_borde = (88, 88, 116)
        self.color_texto = (255, 255, 255)
        self.color_cantidad = (220, 220, 220)
        self.color_hotbar_selected = (255, 215, 0)
        
        self.items_database = self._crear_items_database()
        
    def agregar_item(self, nombre, cantidad=1):
        if nombre not in self.items_database:
            print(f"Error: El ítem '{nombre}' no existe.")
            return False

        # Intentar stackear en slots ocupados (Hotbar e Inventario)
        for lista_slots in [self.hotbar, self.slots_inventario]:
            for i in range(len(lista_slots)):
                slot = lista_slots[i]
                if slot and slot.nombre == nombre:
                    espacio_libre = slot.max_stack - slot.cantidad
                    if espacio_libre > 0:
                        sumar = min(espacio_libre, cantidad)
                        slot.cantidad += sumar
                        cantidad -= sumar
                        if cantidad <= 0: return True

        # Si sobra cantidad, buscar el primer slot vacío
        for lista_slots in [self.hotbar, self.slots_inventario]:
            for i in range(len(lista_slots)):
                if lista_slots[i] is None:
                    nuevo_item = self.items_database[nombre].copy()
                    nuevo_item.cantidad = cantidad
                    lista_slots[i] = nuevo_item
                    return True
        
        return False

    def _crear_items_database(self):
        db = {}
        db["Roca"] = Item("Roca", "material", 15, None, "Roca común", "R")
        db["Calcita"] = Item("Calcita", "material", 15, None, "Mineral", "Ca")
        db["Hierro"] = Item("Hierro", "material", 15, None, "Metal", "Fe")
        db["Cristal"] = Item("Cristal", "material", 15, None, "Energía", "Cr")
        db["Silicio"] = Item("Silicio", "material", 15, None, "Pureza", "Si")
        db["Combustible"] = Item("Combustible", "consumible", 15, None, "+25% energía", "C")
        db["Kit Reparación"] = Item("Kit Reparación", "consumible", 20, None, "Repara", "KR")
        db["Pico"] = Item("Pico", "herramienta", 1, None, "Mina", "P")
        db["Scanner"] = Item("Scanner", "herramienta", 1, None, "Analiza", "S")
        return db

    # --- LÓGICA DE CRAFTEO ---
    def verificar_recetas(self):
        """Convierte la rejilla a nombres y busca coincidencias en recetas"""
        grid_nombres = []
        for fila in self.crafting_grid:
            fila_n = [i.nombre.lower() if i else None for i in fila]
            grid_nombres.append(fila_n)

        self.craft_result = None
        for nombre_receta, datos in self.recetas_crafting.items():
            if datos['patron'] == grid_nombres:
                res_item = self.items_database[datos['resultado']].copy()
                res_item.cantidad = datos['cantidad']
                self.craft_result = res_item

    def _consumir_materiales(self):
        for r in range(texturas.craft_grid_size):
            for c in range(texturas.craft_grid_size):
                self.crafting_grid[r][c] = None

    def draw(self, screen):
        self._draw_hotbar(screen)
        if self.visible:
            self._draw_inventario_completo(screen)
            self._draw_crafting(screen)
        if self.dragging and self.dragged_item:
            self._draw_dragged_item(screen)
        if self.tooltip_item and not self.dragging:
            self._draw_tooltip(screen)

    def _draw_crafting(self, screen):
        for row in range(texturas.craft_grid_size):
            for col in range(texturas.craft_grid_size):
                x = texturas.craft_grid_x + col * (texturas.craft_slot_size + texturas.craft_slot_margin)
                y = texturas.craft_grid_y + row * (texturas.craft_slot_size + texturas.craft_slot_margin)
                item = self.crafting_grid[row][col]
                self._draw_slot(screen, x, y, item, ("craft", (row, col)))
        
        # Slot de resultado
        res_x, res_y = texturas.craft_grid_x - 60, texturas.craft_grid_y + 40
        self._draw_slot(screen, res_x, res_y, self.craft_result, ("result", 0))

    def _draw_slot(self, screen, x, y, item, slot_id):
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
        color = self.color_slot_hover if rect.collidepoint(mouse_pos) and not self.dragging else self.color_slot
        
        if rect.collidepoint(mouse_pos) and item:
            self.tooltip_item = item
            self.tooltip_pos = mouse_pos

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, self.color_borde, rect, 2)

        if item:
            font = pygame.font.SysFont("Arial", 18, bold=True)
            # CAMBIO: Usar el símbolo personalizado en lugar de nombre[0]
            text = font.render(item.simbolo, True, (200, 200, 200))
            screen.blit(text, text.get_rect(center=rect.center))
            if item.cantidad > 1:
                f_cant = pygame.font.SysFont("Arial", 11, bold=True)
                c_txt = f_cant.render(str(item.cantidad), True, self.color_cantidad)
                screen.blit(c_txt, (x + self.slot_size - c_txt.get_width() - 2, y + self.slot_size - c_txt.get_height() - 2))

    def _get_slot_at_pos(self, pos):
        mx, my = pos
        # hotbar
        hw = self.slots_por_fila * (self.slot_size + self.padding) + self.padding
        hx, hy = (self.screen_width - hw) // 1, self.screen_height - self.slot_size - 550
        for i in range(10):
            if pygame.Rect(hx + i * (self.slot_size + self.padding), hy, self.slot_size, self.slot_size).collidepoint(pos):
                return ("hot", i)
        
        if self.visible:
            #Inventario Principal
            iw = self.slots_por_fila * (self.slot_size + self.padding) + 40
            ix, iy = (self.screen_width - iw) // 2, (self.screen_height - (5 * (self.slot_size + self.padding) + 100)) // 2
            for i in range(40):
                r, c = i // self.slots_por_fila, i % self.slots_por_fila
                if pygame.Rect(ix + 20 + c * (self.slot_size + self.padding), iy + 80 + r * (self.slot_size + self.padding), self.slot_size, self.slot_size).collidepoint(pos):
                    return ("inv", i)
            
            # Rejilla de Crafteo
            grid_tot = texturas.craft_grid_size * (texturas.craft_slot_size + texturas.craft_slot_margin)
            if (texturas.craft_grid_x <= mx < texturas.craft_grid_x + grid_tot and texturas.craft_grid_y <= my < texturas.craft_grid_y + grid_tot):
                cc = (mx - texturas.craft_grid_x) // (texturas.craft_slot_size + texturas.craft_slot_margin)
                rr = (my - texturas.craft_grid_y) // (texturas.craft_slot_size + texturas.craft_slot_margin)
                if 0 <= rr < texturas.craft_grid_size and 0 <= cc < texturas.craft_grid_size:
                    return ("craft", (rr, cc))
            
            #  Slot Resultado
            if pygame.Rect(texturas.craft_grid_x - 60, texturas.craft_grid_y + 40, self.slot_size, self.slot_size).collidepoint(pos):
                return ("result", 0)
        return None

    def _handle_click(self, pos):
        slot = self._get_slot_at_pos(pos)
        if slot:
            tipo, idx = slot
            item = None
            if tipo == "hot": item = self.hotbar[idx]
            elif tipo == "inv": item = self.slots_inventario[idx]
            elif tipo == "craft": item = self.crafting_grid[idx[0]][idx[1]]
            elif tipo == "result": item = self.craft_result

            if item:
                # hacer la copia, luego eliminar del slot
                item_copiado = item.copy()
                self.dragging = True
                self.dragged_item = item_copiado
                self.dragged_from = slot
                
                # Solo eliminar del slot original si NO es el resultado
                if tipo == "hot": 
                    self.hotbar[idx] = None
                elif tipo == "inv": 
                    self.slots_inventario[idx] = None
                elif tipo == "craft": 
                    self.crafting_grid[idx[0]][idx[1]] = None
                    self.verificar_recetas()
               
    def _handle_release(self, pos):
        if not self.dragging: return
        
        dest = self._get_slot_at_pos(pos)
        if dest == self.dragged_from:
            self._devolver_al_origen()
            self.verificar_recetas()
            self.cancelar_drag()
            return
        
        # Si venimos del resultado y soltamos en lugar válido (no resultado)
        if self.dragged_from[0] == "result" and dest and dest[0] != "result":
            # Consumir materiales solo si colocamos exitosamente el resultado
            tipo_d, idx_d = dest
            
            # Verificar si podemos colocar el item
            if tipo_d == "hot": 
                item_dest = self.hotbar[idx_d]
            elif tipo_d == "inv": 
                item_dest = self.slots_inventario[idx_d]
            elif tipo_d == "craft": 
                item_dest = self.crafting_grid[idx_d[0]][idx_d[1]]
            
            # Solo si el destino está vacío o es apilable
            puede_colocar = False
            if item_dest is None:
                puede_colocar = True
            elif item_dest.nombre == self.dragged_item.nombre and item_dest.cantidad < item_dest.max_stack:
                puede_colocar = True
            
            if puede_colocar:
                # Colocar el item
                if item_dest and item_dest.nombre == self.dragged_item.nombre:
                    # Stackear
                    espacio_libre = item_dest.max_stack - item_dest.cantidad
                    sumar = min(espacio_libre, self.dragged_item.cantidad)
                    item_dest.cantidad += sumar
                else:
                    # Colocar nuevo
                    if tipo_d == "hot": 
                        self.hotbar[idx_d] = self.dragged_item
                    elif tipo_d == "inv": 
                        self.slots_inventario[idx_d] = self.dragged_item
                    elif tipo_d == "craft": 
                        self.crafting_grid[idx_d[0]][idx_d[1]] = self.dragged_item
                
                # Ahora sí consumir materiales y limpiar resultado
                self._consumir_materiales()
                self.craft_result = None
                self.verificar_recetas()

        
        elif dest and dest[0] != "result":
            tipo_d, idx_d = dest
            
            # obtener itemv
            if tipo_d == "hot": item_dest = self.hotbar[idx_d]
            elif tipo_d == "inv": item_dest = self.slots_inventario[idx_d]
            elif tipo_d == "craft": item_dest = self.crafting_grid[idx_d[0]][idx_d[1]]
            
            # stackeo
            if item_dest and item_dest.nombre == self.dragged_item.nombre:
                espacio_libre = item_dest.max_stack - item_dest.cantidad
                if espacio_libre > 0:
                    sumar = min(espacio_libre, self.dragged_item.cantidad)
                    item_dest.cantidad += sumar
                    self.dragged_item.cantidad -= sumar
                
                # Si aún sobra cantidad después de stackear, devolver al origen
                if self.dragged_item.cantidad > 0:
                    self._devolver_al_origen()

            # intercambio
            else:
                # Guardamos lo que había en el destino para no perderlo
                item_temporal = item_dest 
                
                # Ponemos el que arrastramos en el destino
                if tipo_d == "hot": self.hotbar[idx_d] = self.dragged_item
                elif tipo_d == "inv": self.slots_inventario[idx_d] = self.dragged_item
                elif tipo_d == "craft": self.crafting_grid[idx_d[0]][idx_d[1]] = self.dragged_item
                
                # Devolvemos el que "pisamos" al lugar de donde vino el primero
                t_orig, i_orig = self.dragged_from
                if t_orig == "hot": self.hotbar[i_orig] = item_temporal
                elif t_orig == "inv": self.slots_inventario[i_orig] = item_temporal
                elif t_orig == "craft": self.crafting_grid[i_orig[0]][i_orig[1]] = item_temporal
        
        else:
            # Si soltamos al aire o lugar inválido, devolver al origen
            if self.dragged_from[0] != "result":
                self._devolver_al_origen()
        
        self.verificar_recetas()
        self.cancelar_drag()

    def _devolver_al_origen(self):
        t_orig, i_orig = self.dragged_from
        if t_orig == "hot": self.hotbar[i_orig] = self.dragged_item
        elif t_orig == "inv": self.slots_inventario[i_orig] = self.dragged_item
        elif t_orig == "craft": self.crafting_grid[i_orig[0]][i_orig[1]] = self.dragged_item

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9: self.hotbar_seleccionado = event.key - pygame.K_1
            elif event.key == pygame.K_0: self.hotbar_seleccionado = 9
            elif event.key == pygame.K_i: self.toggle()
        if event.type == pygame.MOUSEWHEEL: self.hotbar_seleccionado = (self.hotbar_seleccionado - event.y) % 10
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: self._handle_click(event.pos)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1: self._handle_release(event.pos)

    def toggle(self):
        self.visible = not self.visible
        if not self.visible: self.cancelar_drag()

    def cancelar_drag(self):
        self.dragging = False
        self.dragged_item = None
        self.dragged_from = None

    def _draw_hotbar(self, screen):
        hw = self.slots_por_fila * (self.slot_size + self.padding) + self.padding
        x, y = (self.screen_width - hw) // 1, self.screen_height - self.slot_size - 550
        s = pygame.Surface((hw, self.slot_size + 10)); s.set_alpha(180); s.fill(self.color_fondo)
        screen.blit(s, (x - 5, y - 5))
        for i in range(10):
            if i == self.hotbar_seleccionado:
                pygame.draw.rect(screen, self.color_hotbar_selected, (x + i * (self.slot_size + self.padding) - 2, y - 2, self.slot_size + 4, self.slot_size + 4), 3)
            self._draw_slot(screen, x + i * (self.slot_size + self.padding), y, self.hotbar[i], ("hot", i))

    def _draw_inventario_completo(self, screen):
        iw, ih = self.slots_por_fila * (self.slot_size + self.padding) + 40, 5 * (self.slot_size + self.padding) + 100
        x, y = (self.screen_width - iw) // 2, (self.screen_height - ih) // 2
        s = pygame.Surface((iw, ih)); s.set_alpha(240); s.fill(self.color_fondo); screen.blit(s, (x, y))
        pygame.draw.rect(screen, self.color_borde, (x, y, iw, ih), 3)
        for i in range(40):
            r, c = i // self.slots_por_fila, i % self.slots_por_fila
            self._draw_slot(screen, x + 20 + c * (self.slot_size + self.padding), y + 80 + r * (self.slot_size + self.padding), self.slots_inventario[i], ("inv", i))

    def _draw_dragged_item(self, screen):
        mp = pygame.mouse.get_pos()
        x, y = mp[0] - self.slot_size//2, mp[1] - self.slot_size//2
        pygame.draw.rect(screen, self.color_slot, (x, y, self.slot_size, self.slot_size))
        f = pygame.font.SysFont("Arial", 18, bold=True)
        # CAMBIO: Usar símbolo personalizado
        t = f.render(self.dragged_item.simbolo, True, (255, 255, 255))
        screen.blit(t, t.get_rect(center=(x+self.slot_size//2, y+self.slot_size//2)))

    def _draw_tooltip(self, screen):
        if not self.tooltip_item: return
        f_n = pygame.font.SysFont("Arial", 16, bold=True)
        txt = f_n.render(self.tooltip_item.nombre, True, self.color_texto)
        s = pygame.Surface((txt.get_width()+20, 40)); s.set_alpha(240); s.fill((20, 20, 30))
        screen.blit(s, (self.tooltip_pos[0]+15, self.tooltip_pos[1]-10))
        screen.blit(txt, (self.tooltip_pos[0]+25, self.tooltip_pos[1]))
        self.tooltip_item = None

    def guardar_inventario(self, archivo="inventario.json"):
        data = {"hotbar": [], "inventario": []}
        for i in self.hotbar: data["hotbar"].append({"nombre": i.nombre, "cantidad": i.cantidad} if i else None)
        for i in self.slots_inventario: data["inventario"].append({"nombre": i.nombre, "cantidad": i.cantidad} if i else None)
        with open(archivo, 'w') as f: json.dump(data, f, indent=2)

    def cargar_inventario(self, archivo="inventario.json"):
        try:
            with open(archivo, 'r') as f: data = json.load(f)
            for i, d in enumerate(data.get("hotbar", [])):
                if d: 
                    self.hotbar[i] = self.items_database[d["nombre"]].copy()
                    self.hotbar[i].cantidad = d["cantidad"]
            for i, d in enumerate(data.get("inventario", [])):
                if d: 
                    self.slots_inventario[i] = self.items_database[d["nombre"]].copy()
                    self.slots_inventario[i].cantidad = d["cantidad"]
            return True
        except: return False
 
    def get_item_seleccionado(self):
        return self.hotbar[self.hotbar_seleccionado]

    def usar_consumible(self):
        item = self.get_item_seleccionado()
        if item and item.tipo == "consumible":
            nombre_item = item.nombre
            item.cantidad -= 1
            if item.cantidad <= 0:
                self.hotbar[self.hotbar_seleccionado] = None
            return nombre_item
        return None