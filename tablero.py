import copy
from enum import Enum
from constantes import *


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

class TableroAlice:
    def __init__(self):
        # Inicializar tableros vacíos
        self.tablero1 = [[None for _ in range(8)] for _ in range(8)]
        self.tablero2 = [[None for _ in range(8)] for _ in range(8)]
        
        # Inicializar piezas
        # Piezas negras
        self.tablero1[0][0] = (Pieza.TORRE, Color.NEGRO)
        self.tablero1[0][1] = (Pieza.CABALLO, Color.NEGRO)
        self.tablero1[0][2] = (Pieza.ALFIL, Color.NEGRO)
        self.tablero1[0][3] = (Pieza.REY, Color.NEGRO)  # Rey en d8
        self.tablero1[0][4] = (Pieza.DAMA, Color.NEGRO)  # Dama en e8
        self.tablero1[0][5] = (Pieza.ALFIL, Color.NEGRO)
        self.tablero1[0][6] = (Pieza.CABALLO, Color.NEGRO)
        self.tablero1[0][7] = (Pieza.TORRE, Color.NEGRO)
        
        # Peones negros
        for col in range(8):
            self.tablero1[1][col] = (Pieza.PEON, Color.NEGRO)
        
        # Piezas blancas
        self.tablero1[7][0] = (Pieza.TORRE, Color.BLANCO)
        self.tablero1[7][1] = (Pieza.CABALLO, Color.BLANCO)
        self.tablero1[7][2] = (Pieza.ALFIL, Color.BLANCO)
        self.tablero1[7][3] = (Pieza.REY, Color.BLANCO)  # Rey en d1
        self.tablero1[7][4] = (Pieza.DAMA, Color.BLANCO)  # Dama en e1
        self.tablero1[7][5] = (Pieza.ALFIL, Color.BLANCO)
        self.tablero1[7][6] = (Pieza.CABALLO, Color.BLANCO)
        self.tablero1[7][7] = (Pieza.TORRE, Color.BLANCO)
        
        # Peones blancos
        for col in range(8):
            self.tablero1[6][col] = (Pieza.PEON, Color.BLANCO)
        
        # Inicializar variables para el enroque
        self.reyes_movidos = {Color.BLANCO: False, Color.NEGRO: False}
        self.torres_movidas = {
            Color.BLANCO: {'kingside': False, 'queenside': False},
            Color.NEGRO: {'kingside': False, 'queenside': False}
        }
        
        # Historial de movimientos
        self.historial_movimientos = []

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
        else:
            # Para cualquier movimiento (incluyendo capturas)
            tablero_destino = 2 if tablero_origen == 1 else 1
            
            # Limpiar posición original en el tablero de origen
            if tablero_origen == 1:
                self.tablero1[desde_fila][desde_col] = None
                # Realizar el movimiento en el tablero destino
                self.tablero2[hasta_fila][hasta_col] = pieza
                # Si es captura, limpiar la pieza capturada en el otro tablero
                if es_captura:
                    self.tablero1[hasta_fila][hasta_col] = None
            else:
                self.tablero2[desde_fila][desde_col] = None
                # Realizar el movimiento en el tablero destino
                self.tablero1[hasta_fila][hasta_col] = pieza
                # Si es captura, limpiar la pieza capturada en el otro tablero
                if es_captura:
                    self.tablero2[hasta_fila][hasta_col] = None
        
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

    def hay_pieza_en_camino(self, desde_pos, hasta_pos, tablero_num):
        """Verifica si hay piezas en el camino entre dos posiciones"""
        desde_fila, desde_col = desde_pos
        hasta_fila, hasta_col = hasta_pos
        
        # Si es un movimiento de caballo, no verificar el camino
        if max(abs(hasta_fila - desde_fila), abs(hasta_col - desde_col)) == 2 and \
           min(abs(hasta_fila - desde_fila), abs(hasta_col - desde_col)) == 1:
            return False
        
        # Determinar la dirección del movimiento
        delta_fila = hasta_fila - desde_fila
        delta_col = hasta_col - desde_col
        
        # Si es un movimiento de una casilla, no hay necesidad de verificar el camino
        if abs(delta_fila) <= 1 and abs(delta_col) <= 1:
            return False
        
        # Normalizar la dirección
        if delta_fila != 0:
            paso_fila = delta_fila // abs(delta_fila)
        else:
            paso_fila = 0
        if delta_col != 0:
            paso_col = delta_col // abs(delta_col)
        else:
            paso_col = 0
        
        # Verificar solo las casillas intermedias
        fila_actual = desde_fila + paso_fila
        col_actual = desde_col + paso_col
        
        while (fila_actual, col_actual) != (hasta_fila, hasta_col):
            if self.obtener_pieza(tablero_num, fila_actual, col_actual):
                return True
            fila_actual += paso_fila
            col_actual += paso_col
        
        return False

    def movimientos_pieza(self, tipo_pieza, pos, tablero_num):
        fila, columna = pos
        movimientos = []
        movimientos_captura = []
        
        pieza_actual = self.obtener_pieza(tablero_num, fila, columna)
        if not pieza_actual:
            return movimientos
            
        color_actual = pieza_actual[1]
        
        if tipo_pieza == Pieza.PEON:
            direccion = -1 if color_actual == Color.BLANCO else 1
            
            # Movimiento hacia adelante
            if 0 <= fila + direccion < 8:
                if self.obtener_pieza(tablero_num, fila + direccion, columna) is None:
                    if not self.hay_pieza_en_camino((fila, columna), (fila + direccion, columna), tablero_num):
                        movimientos.append((fila + direccion, columna))
                        
                        # Movimiento doble inicial
                        if ((direccion == -1 and fila == 6) or (direccion == 1 and fila == 1)):
                            if self.obtener_pieza(tablero_num, fila + 2*direccion, columna) is None:
                                if not self.hay_pieza_en_camino((fila, columna), (fila + 2*direccion, columna), tablero_num):
                                    movimientos.append((fila + 2*direccion, columna))
            
            # Capturas diagonales
            for dc in [-1, 1]:
                if 0 <= fila + direccion < 8 and 0 <= columna + dc < 8:
                    pieza_destino = self.obtener_pieza(tablero_num, fila + direccion, columna + dc)
                    if pieza_destino and pieza_destino[1] != color_actual:
                        movimientos_captura.append((fila + direccion, columna + dc))
                        
        elif tipo_pieza == Pieza.CABALLO:
            # El caballo puede saltar, así que no necesita verificación de piezas en el camino
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
                        movimientos_captura.append((nueva_fila, nueva_col))

        elif tipo_pieza in [Pieza.ALFIL, Pieza.TORRE, Pieza.DAMA]:
            direcciones = []
            if tipo_pieza in [Pieza.TORRE, Pieza.DAMA]:
                direcciones.extend([(0, 1), (0, -1), (1, 0), (-1, 0)])
            if tipo_pieza in [Pieza.ALFIL, Pieza.DAMA]:
                direcciones.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
                
            for df, dc in direcciones:
                nueva_fila = fila + df
                nueva_col = columna + dc
                while 0 <= nueva_fila < 8 and 0 <= nueva_col < 8:
                    if not self.hay_pieza_en_camino((fila, columna), (nueva_fila, nueva_col), tablero_num):
                        pieza_destino = self.obtener_pieza(tablero_num, nueva_fila, nueva_col)
                        if pieza_destino is None:
                            movimientos.append((nueva_fila, nueva_col))
                        elif pieza_destino[1] != color_actual:
                            movimientos_captura.append((nueva_fila, nueva_col))
                            break
                        else:
                            break
                    else:
                        break
                    nueva_fila += df
                    nueva_col += dc

        elif tipo_pieza == Pieza.REY:
            # Movimientos normales del rey
            direcciones = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
            ]
            for df, dc in direcciones:
                nueva_fila = fila + df
                nueva_col = columna + dc
                if 0 <= nueva_fila < 8 and 0 <= nueva_col < 8:
                    pieza_destino = self.obtener_pieza(tablero_num, nueva_fila, nueva_col)
                    if pieza_destino is None:
                        if not self.esta_casilla_bajo_ataque(nueva_fila, nueva_col, tablero_num, color_actual):
                            movimientos.append((nueva_fila, nueva_col))
                    elif pieza_destino[1] != color_actual:
                        if not self.esta_casilla_bajo_ataque(nueva_fila, nueva_col, tablero_num, color_actual):
                            movimientos_captura.append((nueva_fila, nueva_col))

            # Verificar enroque si el rey no se ha movido
            if not self.reyes_movidos[color_actual]:
                fila_rey = 7 if color_actual == Color.BLANCO else 0
                
                # Enroque corto (lado del rey)
                if not self.torres_movidas[color_actual]['kingside']:
                    puede_enrocar = True
                    # Verificar que las casillas entre el rey y la torre estén vacías
                    for col in range(5, 7):
                        # Verificar que las casillas estén vacías en ambos tableros
                        if (self.obtener_pieza(tablero_num, fila_rey, col) is not None or
                            self.obtener_pieza(3-tablero_num, fila_rey, col) is not None or
                            self.esta_casilla_bajo_ataque(fila_rey, col, tablero_num, color_actual)):
                            puede_enrocar = False
                            break
                    
                    # Verificar que el rey no esté en jaque y que la torre exista
                    if (puede_enrocar and 
                        not self.esta_casilla_bajo_ataque(fila_rey, 4, tablero_num, color_actual) and
                        self.obtener_pieza(tablero_num, fila_rey, 7) == (Pieza.TORRE, color_actual)):
                        movimientos.append((fila_rey, 6))
                
                # Enroque largo (lado de la dama)
                if not self.torres_movidas[color_actual]['queenside']:
                    puede_enrocar = True
                    # Verificar que las casillas entre el rey y la torre estén vacías
                    for col in range(1, 4):
                        # Verificar que las casillas estén vacías en ambos tableros
                        if (self.obtener_pieza(tablero_num, fila_rey, col) is not None or
                            self.obtener_pieza(3-tablero_num, fila_rey, col) is not None or
                            self.esta_casilla_bajo_ataque(fila_rey, col, tablero_num, color_actual)):
                            puede_enrocar = False
                            break
                    
                    # Verificar que el rey no esté en jaque y que la torre exista
                    if (puede_enrocar and 
                        not self.esta_casilla_bajo_ataque(fila_rey, 4, tablero_num, color_actual) and
                        self.obtener_pieza(tablero_num, fila_rey, 0) == (Pieza.TORRE, color_actual)):
                        movimientos.append((fila_rey, 2))
        
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

    def copiar_tablero(self):
        nuevo_tablero = TableroAlice()
        nuevo_tablero.tablero1 = copy.deepcopy(self.tablero1)
        nuevo_tablero.tablero2 = copy.deepcopy(self.tablero2)
        nuevo_tablero.reyes_movidos = copy.deepcopy(self.reyes_movidos)
        nuevo_tablero.torres_movidas = copy.deepcopy(self.torres_movidas)
        return nuevo_tablero 