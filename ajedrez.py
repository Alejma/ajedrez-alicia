import pygame
import sys
from enum import Enum
import copy

class Pieza(Enum):
    PEON = 1
    CABALLO = 2
    ALFIL = 3
    TORRE = 4
    DAMA = 5
    REY = 6

class Color(Enum):
    BLANCO = 0
    NEGRO = 1
class IA:
    def __init__(self, color, profundidad=3):
        self.color = color  # Color que juega la IA
        self.profundidad = profundidad
        
    def evaluar_tablero(self, tablero):
        """
        Función heurística para evaluar el estado del tablero
        Retorna un valor positivo si es favorable para la IA, negativo si es favorable para el oponente
        """
        valor = 0
        valores_piezas = {
            Pieza.PEON: 100,
            Pieza.CABALLO: 320,
            Pieza.ALFIL: 330,
            Pieza.TORRE: 500,
            Pieza.DAMA: 900,
            Pieza.REY: 20000
        }
        
        # Evaluar material en ambos tableros
        for tablero_num in [1, 2]:
            for fila in range(8):
                for columna in range(8):
                    pieza = tablero.obtener_pieza(tablero_num, fila, columna)
                    if pieza:
                        valor_base = valores_piezas[pieza[0]]
                        # Sumar para piezas de la IA, restar para piezas del oponente
                        multiplicador = 1 if pieza[1] == self.color else -1
                        valor += valor_base * multiplicador
                        
                        # Bonificaciones posicionales
                        if pieza[0] == Pieza.PEON:
                            # Peones más avanzados son mejores
                            avance = 7 - fila if self.color == Color.BLANCO else fila
                            valor += avance * 10 * multiplicador
                        elif pieza[0] in [Pieza.CABALLO, Pieza.ALFIL]:
                            # Piezas menores en el centro son mejores
                            centro_fila = 3.5 - abs(3.5 - fila)
                            centro_col = 3.5 - abs(3.5 - columna)
                            valor += (centro_fila + centro_col) * 10 * multiplicador
        
        return valor

    def minimax(self, tablero, profundidad, alfa, beta, es_maximizador):
        """
        Implementación del algoritmo Minimax con poda alfa-beta
        """
        if profundidad == 0:
            return self.evaluar_tablero(tablero)
            
        if es_maximizador:
            mejor_valor = float('-inf')
            for movimiento in self.obtener_todos_movimientos(tablero, self.color):
                tablero_temp = tablero.copiar_tablero()
                tablero_temp.realizar_movimiento(movimiento)
                valor = self.minimax(tablero_temp, profundidad - 1, alfa, beta, False)
                mejor_valor = max(mejor_valor, valor)
                alfa = max(alfa, mejor_valor)
                if beta <= alfa:
                    break
            return mejor_valor
        else:
            mejor_valor = float('inf')
            color_oponente = Color.NEGRO if self.color == Color.BLANCO else Color.BLANCO
            for movimiento in self.obtener_todos_movimientos(tablero, color_oponente):
                tablero_temp = tablero.copiar_tablero()
                tablero_temp.realizar_movimiento(movimiento)
                valor = self.minimax(tablero_temp, profundidad - 1, alfa, beta, True)
                mejor_valor = min(mejor_valor, valor)
                beta = min(beta, mejor_valor)
                if beta <= alfa:
                    break
            return mejor_valor

    def obtener_mejor_movimiento(self, tablero):
        """
        Encuentra el mejor movimiento usando Minimax con poda alfa-beta
        """
        mejor_movimiento = None
        mejor_valor = float('-inf')
        alfa = float('-inf')
        beta = float('inf')
        
        for movimiento in self.obtener_todos_movimientos(tablero, self.color):
            tablero_temp = tablero.copiar_tablero()
            tablero_temp.realizar_movimiento(movimiento)
            valor = self.minimax(tablero_temp, self.profundidad - 1, alfa, beta, False)
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = movimiento
                
        return mejor_movimiento

    def obtener_todos_movimientos(self, tablero, color):
        """
        Obtiene todos los movimientos posibles para un color dado
        """
        movimientos = []
        for tablero_num in [1, 2]:
            for fila in range(8):
                for columna in range(8):
                    pieza = tablero.obtener_pieza(tablero_num, fila, columna)
                    if pieza and pieza[1] == color:
                        movs = tablero.movimientos_pieza(pieza[0], (fila, columna), tablero_num)
                        for mov in movs:
                            movimientos.append((tablero_num, (fila, columna), mov))
        return movimientos

class TableroAlice:
    def __init__(self):
        self.tablero1 = [[None for _ in range(8)] for _ in range(8)]
        self.tablero2 = [[None for _ in range(8)] for _ in range(8)]
        self.historial_movimientos = []
        self.reyes_movidos = {Color.BLANCO: False, Color.NEGRO: False}
        self.torres_movidas = {
            Color.BLANCO: {'kingside': False, 'queenside': False},
            Color.NEGRO: {'kingside': False, 'queenside': False}
        }
        self.inicializar_tablero()
    def realizar_movimiento(self, movimiento):
        tablero_origen, desde_pos, hasta_pos = movimiento
        desde_fila, desde_col = desde_pos
        hasta_fila, hasta_col = hasta_pos
        
        # Obtener la pieza a mover
        pieza = self.obtener_pieza(tablero_origen, desde_fila, desde_col)
        if not pieza:
            return False
            
        # Verificar si es una captura
        pieza_destino = self.obtener_pieza(tablero_origen, hasta_fila, hasta_col)
        es_captura = pieza_destino is not None and pieza_destino[1] != pieza[1]
        
        # Verificar si es enroque
        es_enroque = (pieza[0] == Pieza.REY and abs(desde_col - hasta_col) == 2)
        
        if es_enroque:
            # Mover el rey
            if tablero_origen == 1:
                self.tablero1[desde_fila][desde_col] = None
                self.tablero1[hasta_fila][hasta_col] = pieza
                # Mover la torre
                if hasta_col == 6:  # Enroque corto
                    self.tablero1[desde_fila][7] = None
                    self.tablero1[desde_fila][5] = (Pieza.TORRE, pieza[1])
                else:  # Enroque largo
                    self.tablero1[desde_fila][0] = None
                    self.tablero1[desde_fila][3] = (Pieza.TORRE, pieza[1])
            else:
                self.tablero2[desde_fila][desde_col] = None
                self.tablero2[hasta_fila][hasta_col] = pieza
                # Mover la torre
                if hasta_col == 6:  # Enroque corto
                    self.tablero2[desde_fila][7] = None
                    self.tablero2[desde_fila][5] = (Pieza.TORRE, pieza[1])
                else:  # Enroque largo
                    self.tablero2[desde_fila][0] = None
                    self.tablero2[desde_fila][3] = (Pieza.TORRE, pieza[1])
        elif es_captura:
            # Realizar captura en el mismo tablero
            if tablero_origen == 1:
                self.tablero1[desde_fila][desde_col] = None
                self.tablero1[hasta_fila][hasta_col] = pieza
            else:
                self.tablero2[desde_fila][desde_col] = None
                self.tablero2[hasta_fila][hasta_col] = pieza
        else:
            # Movimiento normal al tablero opuesto
            if tablero_origen == 1:
                self.tablero1[desde_fila][desde_col] = None
                self.tablero2[hasta_fila][hasta_col] = pieza
            else:
                self.tablero2[desde_fila][desde_col] = None
                self.tablero1[hasta_fila][hasta_col] = pieza
        
        # Actualizar historial y estado de piezas especiales
        self.historial_movimientos.append((tablero_origen, desde_pos, hasta_pos))
        if pieza[0] == Pieza.REY:
            self.reyes_movidos[pieza[1]] = True
        elif pieza[0] == Pieza.TORRE:
            if desde_col == 0:
                self.torres_movidas[pieza[1]]['queenside'] = True
            elif desde_col == 7:
                self.torres_movidas[pieza[1]]['kingside'] = True
                
        return True    

    def inicializar_tablero(self):
        # Inicializar piezas negras
        self.tablero1[0] = [
            (Pieza.TORRE, Color.NEGRO), (Pieza.CABALLO, Color.NEGRO),
            (Pieza.ALFIL, Color.NEGRO), (Pieza.DAMA, Color.NEGRO),
            (Pieza.REY, Color.NEGRO), (Pieza.ALFIL, Color.NEGRO),
            (Pieza.CABALLO, Color.NEGRO), (Pieza.TORRE, Color.NEGRO)
        ]
        for i in range(8):
            self.tablero1[1][i] = (Pieza.PEON, Color.NEGRO)
            
        # Inicializar piezas blancas
        self.tablero1[7] = [
            (Pieza.TORRE, Color.BLANCO), (Pieza.CABALLO, Color.BLANCO),
            (Pieza.ALFIL, Color.BLANCO), (Pieza.DAMA, Color.BLANCO),
            (Pieza.REY, Color.BLANCO), (Pieza.ALFIL, Color.BLANCO),
            (Pieza.CABALLO, Color.BLANCO), (Pieza.TORRE, Color.BLANCO)
        ]
        for i in range(8):
            self.tablero1[6][i] = (Pieza.PEON, Color.BLANCO)

    def copiar_tablero(self):
        nuevo_tablero = TableroAlice()
        nuevo_tablero.tablero1 = copy.deepcopy(self.tablero1)
        nuevo_tablero.tablero2 = copy.deepcopy(self.tablero2)
        nuevo_tablero.reyes_movidos = copy.deepcopy(self.reyes_movidos)
        nuevo_tablero.torres_movidas = copy.deepcopy(self.torres_movidas)
        return nuevo_tablero

    def obtener_pieza(self, tablero_num, fila, columna):
        """
        Obtiene la pieza en una posición específica del tablero indicado
        tablero_num: 1 o 2 (indica qué tablero)
        fila, columna: coordenadas de la posición
        """
        if tablero_num == 1:
            return self.tablero1[fila][columna]
        else:
            return self.tablero2[fila][columna]

    def movimientos_pieza(self, tipo_pieza, pos, tablero_num):
        fila, columna = pos
        movimientos = []
        movimientos_captura = []  # Lista separada para movimientos de captura
        
        pieza_actual = self.obtener_pieza(tablero_num, fila, columna)
        if not pieza_actual:
            return movimientos
            
        color_actual = pieza_actual[1]
        
        if tipo_pieza == Pieza.PEON:
            direccion = -1 if color_actual == Color.BLANCO else 1
            
            # Movimiento hacia adelante (sin captura)
            if 0 <= fila + direccion < 8:
                if self.obtener_pieza(tablero_num, fila + direccion, columna) is None:
                    # Verificar tablero espejo para movimientos normales
                    tablero_espejo = 2 if tablero_num == 1 else 1
                    if self.obtener_pieza(tablero_espejo, fila + direccion, columna) is None:
                        movimientos.append((fila + direccion, columna))
                        # Movimiento doble inicial
                        if (direccion == -1 and fila == 6) or (direccion == 1 and fila == 1):
                            if self.obtener_pieza(tablero_num, fila + 2*direccion, columna) is None:
                                if self.obtener_pieza(tablero_espejo, fila + 2*direccion, columna) is None:
                                    movimientos.append((fila + 2*direccion, columna))
            
            # Capturas diagonales (en el mismo tablero)
            for dc in [-1, 1]:
                if 0 <= fila + direccion < 8 and 0 <= columna + dc < 8:
                    pieza_destino = self.obtener_pieza(tablero_num, fila + direccion, columna + dc)
                    if pieza_destino and pieza_destino[1] != color_actual:
                        movimientos_captura.append((fila + direccion, columna + dc))
                        
        elif tipo_pieza == Pieza.CABALLO:
            movimientos_caballo = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            
            for df, dc in movimientos_caballo:
                nueva_fila = fila + df
                nueva_col = columna + dc
                if 0 <= nueva_fila < 8 and 0 <= nueva_col < 8:
                    pieza_destino = self.obtener_pieza(tablero_num, nueva_fila, nueva_col)
                    if pieza_destino is None:
                        # Verificar tablero espejo para movimientos normales
                        tablero_espejo = 2 if tablero_num == 1 else 1
                        if self.obtener_pieza(tablero_espejo, nueva_fila, nueva_col) is None:
                            movimientos.append((nueva_fila, nueva_col))
                    elif pieza_destino[1] != color_actual:
                        # Captura en el mismo tablero
                        movimientos_captura.append((nueva_fila, nueva_col))

        elif tipo_pieza in [Pieza.ALFIL, Pieza.TORRE, Pieza.DAMA]:
            direcciones = []
            if tipo_pieza in [Pieza.ALFIL, Pieza.DAMA]:
                direcciones.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
            if tipo_pieza in [Pieza.TORRE, Pieza.DAMA]:
                direcciones.extend([(0, 1), (0, -1), (1, 0), (-1, 0)])
                
            for dir_f, dir_c in direcciones:
                nueva_fila, nueva_col = fila + dir_f, columna + dir_c
                while 0 <= nueva_fila < 8 and 0 <= nueva_col < 8:
                    pieza_destino = self.obtener_pieza(tablero_num, nueva_fila, nueva_col)
                    if pieza_destino is None:
                        # Verificar tablero espejo para movimientos normales
                        tablero_espejo = 2 if tablero_num == 1 else 1
                        if self.obtener_pieza(tablero_espejo, nueva_fila, nueva_col) is None:
                            movimientos.append((nueva_fila, nueva_col))
                    elif pieza_destino[1] != color_actual:
                        # Captura en el mismo tablero
                        movimientos_captura.append((nueva_fila, nueva_col))
                        break
                    else:
                        break
                    nueva_fila += dir_f
                    nueva_col += dir_c

        elif tipo_pieza == Pieza.REY:
            # Movimientos básicos del rey (una casilla en cualquier dirección)
            direcciones = [
                (-1, -1), (-1, 0), (-1, 1),  # Arriba
                (0, -1),           (0, 1),   # Lados
                (1, -1),  (1, 0),  (1, 1)    # Abajo
            ]
            
            for df, dc in direcciones:
                nueva_fila = fila + df
                nueva_col = columna + dc
                
                if 0 <= nueva_fila < 8 and 0 <= nueva_col < 8:
                    pieza_destino = self.obtener_pieza(tablero_num, nueva_fila, nueva_col)
                    
                    if pieza_destino is None:
                        # Movimiento normal - verificar tablero espejo
                        tablero_espejo = 2 if tablero_num == 1 else 1
                        if self.obtener_pieza(tablero_espejo, nueva_fila, nueva_col) is None:
                            # Verificar que el movimiento no ponga al rey en jaque
                            if not self.esta_casilla_bajo_ataque(nueva_fila, nueva_col, tablero_num, color_actual):
                                movimientos.append((nueva_fila, nueva_col))
                    elif pieza_destino[1] != color_actual:
                        # Captura en el mismo tablero
                        if not self.esta_casilla_bajo_ataque(nueva_fila, nueva_col, tablero_num, color_actual):
                            movimientos_captura.append((nueva_fila, nueva_col))
            
            # Verificar enroque si el rey no se ha movido
            if not self.reyes_movidos[color_actual]:
                fila_rey = 7 if color_actual == Color.BLANCO else 0
                
                # Enroque corto
                if not self.torres_movidas[color_actual]['kingside']:
                    puede_enrocar = True
                    # Verificar casillas vacías entre rey y torre
                    for col in range(5, 7):
                        # Verificar que las casillas estén vacías en ambos tableros
                        if (self.obtener_pieza(tablero_num, fila_rey, col) is not None or
                            self.obtener_pieza(3-tablero_num, fila_rey, col) is not None):
                            puede_enrocar = False
                            break
                        # Verificar que las casillas no estén bajo ataque
                        if self.esta_casilla_bajo_ataque(fila_rey, col, tablero_num, color_actual):
                            puede_enrocar = False
                            break
                    
                    if puede_enrocar:
                        movimientos.append((fila_rey, 6))  # Posición final del rey
                
                # Enroque largo
                if not self.torres_movidas[color_actual]['queenside']:
                    puede_enrocar = True
                    # Verificar casillas vacías entre rey y torre
                    for col in range(1, 4):
                        # Verificar que las casillas estén vacías en ambos tableros
                        if (self.obtener_pieza(tablero_num, fila_rey, col) is not None or
                            self.obtener_pieza(3-tablero_num, fila_rey, col) is not None):
                            puede_enrocar = False
                            break
                        # Verificar que las casillas no estén bajo ataque
                        if self.esta_casilla_bajo_ataque(fila_rey, col, tablero_num, color_actual):
                            puede_enrocar = False
                            break
                    
                    if puede_enrocar:
                        movimientos.append((fila_rey, 2))  # Posición final del rey
        
        # Combinar movimientos normales y capturas
        return movimientos + movimientos_captura
    
    def esta_en_jaque(self, fila, columna, tablero_num):
        """
        Verifica si el rey en la posición dada está en jaque
        """
        pieza = self.obtener_pieza(tablero_num, fila, columna)
        if not pieza or pieza[0] != Pieza.REY:
            return False
            
        color_rey = pieza[1]
        return self.esta_casilla_bajo_ataque(fila, columna, tablero_num, color_rey)

    def esta_casilla_bajo_ataque(self, fila, columna, tablero_num, color_defensor):
        """
        Verifica si una casilla está bajo ataque por piezas del color opuesto
        """
        color_atacante = Color.NEGRO if color_defensor == Color.BLANCO else Color.BLANCO
        
        # Verificar ataques de peón
        direcciones_peon = [(-1, -1), (-1, 1)] if color_defensor == Color.BLANCO else [(1, -1), (1, 1)]
        for df, dc in direcciones_peon:
            nueva_fila, nueva_col = fila + df, columna + dc
            if 0 <= nueva_fila < 8 and 0 <= nueva_col < 8:
                pieza = self.obtener_pieza(tablero_num, nueva_fila, nueva_col)
                if pieza and pieza[0] == Pieza.PEON and pieza[1] == color_atacante:
                    return True

        # Verificar ataques de caballo
        movimientos_caballo = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                             (1, -2), (1, 2), (2, -1), (2, 1)]
        for df, dc in movimientos_caballo:
            nueva_fila, nueva_col = fila + df, columna + dc
            if 0 <= nueva_fila < 8 and 0 <= nueva_col < 8:
                pieza = self.obtener_pieza(tablero_num, nueva_fila, nueva_col)
                if pieza and pieza[0] == Pieza.CABALLO and pieza[1] == color_atacante:
                    return True

        # Verificar ataques en líneas rectas y diagonales (torre, alfil, dama)
        direcciones = [(0, 1), (0, -1), (1, 0), (-1, 0),  # Direcciones de torre
                      (-1, -1), (-1, 1), (1, -1), (1, 1)] # Direcciones de alfil
        for df, dc in direcciones:
            nueva_fila, nueva_col = fila + df, columna + dc
            while 0 <= nueva_fila < 8 and 0 <= nueva_col < 8:
                pieza = self.obtener_pieza(tablero_num, nueva_fila, nueva_col)
                if pieza:
                    if pieza[1] == color_atacante:
                        # Verificar si la pieza puede atacar en esta dirección
                        if (df, dc) in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # Direcciones de torre
                            if pieza[0] in [Pieza.TORRE, Pieza.DAMA]:
                                return True
                        else:  # Direcciones diagonales
                            if pieza[0] in [Pieza.ALFIL, Pieza.DAMA]:
                                return True
                    break
                nueva_fila += df
                nueva_col += dc

        # Verificar ataques del rey enemigo
        direcciones_rey = [(-1, -1), (-1, 0), (-1, 1),
                         (0, -1),            (0, 1),
                         (1, -1),  (1, 0),   (1, 1)]
        for df, dc in direcciones_rey:
            nueva_fila, nueva_col = fila + df, columna + dc
            if 0 <= nueva_fila < 8 and 0 <= nueva_col < 8:
                pieza = self.obtener_pieza(tablero_num, nueva_fila, nueva_col)
                if pieza and pieza[0] == Pieza.REY and pieza[1] == color_atacante:
                    return True

        return False
class JuegoAlice:
    def __init__(self):
        pygame.init()
        self.TAMANO_CASILLA = 60
        self.ANCHO = self.TAMANO_CASILLA * 16  # Para dos tableros
        self.ALTO = self.TAMANO_CASILLA * 8
        self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO))
        pygame.display.set_caption('Ajedrez Alice')
        self.tablero = TableroAlice()
        self.cargar_imagenes()
        self.ia = IA(Color.NEGRO)  # La IA juega con las negras
        self.jugador_vs_ia = True  # Activar modo jugador vs IA
        
        # Variables para el manejo de movimientos
        self.pieza_seleccionada = None
        self.tablero_seleccionado = None
        self.turno_actual = Color.BLANCO
        self.movimientos_validos = []

    def cargar_imagenes(self):
        try:
            self.imagenes = {}
            piezas = {
                Pieza.PEON: 'peon',
                Pieza.CABALLO: 'caballo', 
                Pieza.ALFIL: 'alfil',
                Pieza.TORRE: 'torre',
                Pieza.DAMA: 'dama',
                Pieza.REY: 'rey'
            }
            colores = {
                Color.BLANCO: 'blanco',
                Color.NEGRO: 'negro'
            }
            
            for pieza in Pieza:
                for color in Color:
                    ruta = f"imagenes/{piezas[pieza]}_{colores[color]}.png"
                    try:
                        imagen = pygame.image.load(ruta)
                        imagen = pygame.transform.scale(imagen, (self.TAMANO_CASILLA, self.TAMANO_CASILLA))
                        self.imagenes[(pieza, color)] = imagen
                        print("Imagien cargada con exito:" + ruta)
                    except pygame.error as e:
                        print(f"Error al cargar la imagen: {ruta}")
                        print(f"Error específico: {e}")
                        
        except Exception as e:
            print(f"Error general al cargar imágenes: {e}")

    def dibujar_tablero(self):
        # Dibujar tableros base
        for tablero in range(2):
            offset_x = tablero * self.TAMANO_CASILLA * 8
            for fila in range(8):
                for columna in range(8):
                    # Dibujar las casillas
                    color = (255, 206, 158) if (fila + columna) % 2 == 0 else (209, 139, 71)
                    pygame.draw.rect(self.pantalla, color,
                                   (offset_x + columna * self.TAMANO_CASILLA,
                                    fila * self.TAMANO_CASILLA,
                                    self.TAMANO_CASILLA, self.TAMANO_CASILLA))

        # Resaltar casilla seleccionada
        if self.pieza_seleccionada:
            fila, columna = self.pieza_seleccionada
            offset_x = 0 if self.tablero_seleccionado == 1 else self.TAMANO_CASILLA * 8
            pygame.draw.rect(self.pantalla, (255, 255, 0),
                           (offset_x + columna * self.TAMANO_CASILLA,
                            fila * self.TAMANO_CASILLA,
                            self.TAMANO_CASILLA, self.TAMANO_CASILLA), 3)

        # Resaltar movimientos válidos
        for fila, columna in self.movimientos_validos:
            offset_x = 0 if self.tablero_seleccionado == 1 else self.TAMANO_CASILLA * 8
            pygame.draw.circle(self.pantalla, (0, 255, 0),
                             (offset_x + columna * self.TAMANO_CASILLA + self.TAMANO_CASILLA // 2,
                              fila * self.TAMANO_CASILLA + self.TAMANO_CASILLA // 2),
                             10)

    def obtener_casilla_desde_mouse(self, pos_mouse):
        x, y = pos_mouse
        # Determinar en qué tablero se hizo clic
        if x < self.TAMANO_CASILLA * 8:
            tablero = 1
            columna = x // self.TAMANO_CASILLA
        else:
            tablero = 2
            columna = (x - self.TAMANO_CASILLA * 8) // self.TAMANO_CASILLA
        
        fila = y // self.TAMANO_CASILLA
        return tablero, fila, columna

    def manejar_click(self):
        pos_mouse = pygame.mouse.get_pos()
        tablero, fila, columna = self.obtener_casilla_desde_mouse(pos_mouse)
        
        # Si está fuera del tablero, ignorar el click
        if not (0 <= fila < 8 and 0 <= columna < 8):
            return

        print(f"Click en tablero {tablero}, fila {fila}, columna {columna}")  # Debug

        # Si no hay pieza seleccionada
        if self.pieza_seleccionada is None:
            pieza = self.tablero.obtener_pieza(tablero, fila, columna)
            if pieza and pieza[1] == self.turno_actual:
                print(f"Seleccionando pieza: {pieza}")  # Debug
                self.pieza_seleccionada = (fila, columna)
                self.tablero_seleccionado = tablero
                self.movimientos_validos = self.tablero.movimientos_pieza(
                    pieza[0], (fila, columna), tablero)
        
        # Si hay una pieza seleccionada
        else:
            desde_fila, desde_col = self.pieza_seleccionada
            if (fila, columna) in self.movimientos_validos:
                print(f"Moviendo pieza a {fila}, {columna}")
                self.tablero.realizar_movimiento((
                    self.tablero_seleccionado,
                    (desde_fila, desde_col),
                    (fila, columna)
                ))
                self.turno_actual = Color.NEGRO if self.turno_actual == Color.BLANCO else Color.BLANCO
            
            self.pieza_seleccionada = None
            self.tablero_seleccionado = None
            self.movimientos_validos = []

        # Después de realizar el movimiento del jugador
        if self.turno_actual == self.ia.color and self.jugador_vs_ia:
            # Hacer que la IA realice su movimiento
            movimiento_ia = self.ia.obtener_mejor_movimiento(self.tablero)
            if movimiento_ia:
                self.tablero.realizar_movimiento(movimiento_ia)
                self.turno_actual = Color.BLANCO  # Cambiar el turno al jugador

    def dibujar_piezas(self):
        # Dibujar piezas en tablero 1
        for fila in range(8):
            for columna in range(8):
                pieza = self.tablero.tablero1[fila][columna]
                if pieza:  # Si hay una pieza en esta posición
                    imagen = self.imagenes.get(pieza)  # Obtener la imagen correspondiente
                    if imagen:
                        self.pantalla.blit(imagen,
                                         (columna * self.TAMANO_CASILLA,
                                          fila * self.TAMANO_CASILLA))
                      
        # Dibujar piezas en tablero 2
        for fila in range(8):
            for columna in range(8):
                pieza = self.tablero.tablero2[fila][columna]
                if pieza:  # Si hay una pieza en esta posición
                    imagen = self.imagenes.get(pieza)  # Obtener la imagen correspondiente
                    if imagen:
                        self.pantalla.blit(imagen,
                                         ((columna + 8) * self.TAMANO_CASILLA,
                                          fila * self.TAMANO_CASILLA))

    def ejecutar(self):
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:  # Click izquierdo
                        self.manejar_click()

            self.dibujar_tablero()
            self.dibujar_piezas()  # Asegurarnos de que se llame a dibujar_piezas
            pygame.display.flip()

if __name__ == "__main__":
    juego = JuegoAlice()
    juego.ejecutar()    