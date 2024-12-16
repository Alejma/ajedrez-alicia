from constantes import Pieza, Color

class IA:
    def __init__(self, color, profundidad=4):
        """
        Constructor de la clase IA (Inteligencia Artificial).
        :param color: El color de la IA (BLANCO o NEGRO).
        :param profundidad: La profundidad máxima para la búsqueda Minimax.
        """
        self.color = color
        self.profundidad = profundidad
        # Tablas de posición para evaluar la ubicación de las piezas
        self.tablas_posicion = {
            Pieza.PEON: [
                [0,  0,  0,  0,  0,  0,  0,  0],
                [50, 50, 50, 50, 50, 50, 50, 50],
                [10, 10, 20, 30, 30, 20, 10, 10],
                [5,  5, 10, 25, 25, 10,  5,  5],
                [0,  0,  0, 20, 20,  0,  0,  0],
                [5, -5,-10,  0,  0,-10, -5,  5],
                [5, 10, 10,-20,-20, 10, 10,  5],
                [0,  0,  0,  0,  0,  0,  0,  0]
            ],
            Pieza.CABALLO: [
                [-50,-40,-30,-30,-30,-30,-40,-50],
                [-40,-20,  0,  0,  0,  0,-20,-40],
                [-30,  0, 10, 15, 15, 10,  0,-30],
                [-30,  5, 15, 20, 20, 15,  5,-30],
                [-30,  0, 15, 20, 20, 15,  0,-30],
                [-30,  5, 10, 15, 15, 10,  5,-30],
                [-40,-20,  0,  5,  5,  0,-20,-40],
                [-50,-40,-30,-30,-30,-30,-40,-50]
            ],
            Pieza.ALFIL: [
                [-20,-10,-10,-10,-10,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5, 10, 10,  5,  0,-10],
                [-10,  5,  5, 10, 10,  5,  5,-10],
                [-10,  0, 10, 10, 10, 10,  0,-10],
                [-10, 10, 10, 10, 10, 10, 10,-10],
                [-10,  5,  0,  0,  0,  0,  5,-10],
                [-20,-10,-10,-10,-10,-10,-10,-20]
            ],
            Pieza.TORRE: [
                [0,  0,  0,  0,  0,  0,  0,  0],
                [5, 10, 10, 10, 10, 10, 10,  5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [0,  0,  0,  5,  5,  0,  0,  0]
            ],
            Pieza.DAMA: [
                [-20,-10,-10, -5, -5,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5,  5,  5,  5,  0,-10],
                [-5,  0,  5,  5,  5,  5,  0, -5],
                [0,  0,  5,  5,  5,  5,  0, -5],
                [-10,  5,  5,  5,  5,  5,  0,-10],
                [-10,  0,  5,  0,  0,  0,  0,-10],
                [-20,-10,-10, -5, -5,-10,-10,-20]
            ],
            Pieza.REY: [
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-20,-30,-30,-40,-40,-30,-30,-20],
                [-10,-20,-20,-20,-20,-20,-20,-10],
                [20, 20,  0,  0,  0,  0, 20, 20],
                [20, 30, 10,  0,  0, 10, 30, 20]
            ]
        }

    def evaluar_tablero(self, tablero):
        """
        Evalúa el estado del tablero para determinar qué tan favorable es para la IA.
        :param tablero: El estado actual del tablero de ajedrez.
        :return: Un valor numérico que representa la calidad del tablero desde la perspectiva de la IA.
        """
        valor = 0
        # Valores de las piezas (aproximados por su poder relativo)
        valores_piezas = {
            Pieza.PEON: 100,
            Pieza.CABALLO: 320,
            Pieza.ALFIL: 330,
            Pieza.TORRE: 500,
            Pieza.DAMA: 900,
            Pieza.REY: 20000
        }
        
        # Evaluación del material y la posición de las piezas en el tablero
        for tablero_num in [1, 2]:  # Iterar por ambos tableros (uno para cada jugador)
            for fila in range(8):  # Iterar sobre las filas
                for columna in range(8):  # Iterar sobre las columnas
                    pieza = tablero.obtener_pieza(tablero_num, fila, columna)  # Obtener la pieza en la posición
                    if pieza:
                        valor_base = valores_piezas[pieza[0]]  # Obtener el valor base de la pieza
                        multiplicador = 1 if pieza[1] == self.color else -1  # Determinar si la pieza es aliada o enemiga
                        
                        # Evaluar el valor material
                        valor += valor_base * multiplicador
                        
                        # Evaluar el valor posicional de la pieza
                        fila_eval = fila if pieza[1] == Color.BLANCO else 7 - fila  # Ajustar fila según el color
                        valor_posicion = self.tablas_posicion[pieza[0]][fila_eval][columna]
                        valor += valor_posicion * multiplicador
                        
                        # Bonificaciones adicionales para el peón
                        if pieza[0] == Pieza.PEON:
                            # Penalización por peones doblados
                            peones_columna = sum(1 for f in range(8) 
                                              if tablero.obtener_pieza(tablero_num, f, columna) == pieza)
                            if peones_columna > 1:
                                valor -= 20 * multiplicador
                            
                            # Penalización por peones aislados
                            peones_adyacentes = False
                            for c in [columna-1, columna+1]:
                                if 0 <= c < 8:
                                    for f in range(8):
                                        if tablero.obtener_pieza(tablero_num, f, c) == pieza:
                                            peones_adyacentes = True
                                            break
                            if not peones_adyacentes:
                                valor -= 30 * multiplicador

        # Evaluar la seguridad del rey
        for tablero_num in [1, 2]:
            rey_encontrado = False
            for fila in range(8):
                for columna in range(8):
                    pieza = tablero.obtener_pieza(tablero_num, fila, columna)
                    if pieza and pieza[0] == Pieza.REY and pieza[1] == self.color:
                        rey_encontrado = True
                        # Penalizar si el rey está en jaque
                        if tablero.esta_en_jaque(fila, columna, tablero_num):
                            valor -= 100
                        break
                if rey_encontrado:
                    break
                    
        return valor

    def minimax(self, tablero, profundidad, alfa, beta, es_maximizador, movimiento_anterior=None):
        # Verificación de estado terminal
        if profundidad == 0:
            return self.evaluar_tablero(tablero)
        
        # Ordenar movimientos para mejorar la poda
        movimientos = self.obtener_todos_movimientos(tablero, 
                     self.color if es_maximizador else 
                     (Color.NEGRO if self.color == Color.BLANCO else Color.BLANCO))
        
        # Ordenar movimientos (capturas primero)
        movimientos = self.ordenar_movimientos(tablero, movimientos)
        
        if es_maximizador:
            mejor_valor = float('-inf')
            for movimiento in movimientos:
                tablero_temp = tablero.copiar_tablero()
                if tablero_temp.realizar_movimiento(movimiento):
                    valor = self.minimax(tablero_temp, profundidad - 1, alfa, beta, False, movimiento)
                    mejor_valor = max(mejor_valor, valor)
                    alfa = max(alfa, mejor_valor)
                    if beta <= alfa:
                        break  # Poda beta
            return mejor_valor
        else:
            mejor_valor = float('inf')
            for movimiento in movimientos:
                tablero_temp = tablero.copiar_tablero()
                if tablero_temp.realizar_movimiento(movimiento):
                    valor = self.minimax(tablero_temp, profundidad - 1, alfa, beta, True, movimiento)
                    mejor_valor = min(mejor_valor, valor)
                    beta = min(beta, mejor_valor)
                    if beta <= alfa:
                        break  # Poda alfa
            return mejor_valor

    def ordenar_movimientos(self, tablero, movimientos):
        """Ordena los movimientos para mejorar la eficiencia de la poda"""
        movimientos_valorados = []
        for mov in movimientos:
            valor = 0
            # Priorizar capturas
            pieza_destino = tablero.obtener_pieza(mov[0], mov[2][0], mov[2][1])
            if pieza_destino:
                valor += 10
            # Priorizar movimientos al centro
            centro_fila = abs(3.5 - mov[2][0])
            centro_col = abs(3.5 - mov[2][1])
            valor += (7 - (centro_fila + centro_col)) / 2
            movimientos_valorados.append((mov, valor))
        
        return [x[0] for x in sorted(movimientos_valorados, key=lambda x: x[1], reverse=True)]

    def obtener_mejor_movimiento(self, tablero):
        mejor_movimiento = None
        mejor_valor = float('-inf')
        alfa = float('-inf')
        beta = float('inf')
        
        movimientos = self.obtener_todos_movimientos(tablero, self.color)
        movimientos = self.ordenar_movimientos(tablero, movimientos)
        
        for movimiento in movimientos:
            tablero_temp = tablero.copiar_tablero()
            if tablero_temp.realizar_movimiento(movimiento):
                valor = self.minimax(tablero_temp, self.profundidad - 1, alfa, beta, False, movimiento)
                if valor > mejor_valor:
                    mejor_valor = valor
                    mejor_movimiento = movimiento
                alfa = max(alfa, mejor_valor)
        print(mejor_movimiento)
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