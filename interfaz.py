import pygame
import sys
from enum import Enum
import copy
from IA import IA
from tablero import TableroAlice, Color, Pieza


class JuegoAlice:
    def __init__(self):
        pygame.init()
        self.ANCHO_VENTANA = 1450
        self.ALTO_VENTANA = 600
        self.TAMANO_CASILLA = 60
        self.ESPACIO_ENTRE_TABLEROS = 100
        self.OFFSET_X = 50
        
        self.pantalla = pygame.display.set_mode((self.ANCHO_VENTANA, self.ALTO_VENTANA))
        pygame.display.set_caption('Proyecto II IA - Ajedrez Alice')
        
        # Colores
        self.COLOR_PANEL = (200, 200, 200)
        self.COLOR_TEXTO = (0, 0, 0)
        
        self.tablero = TableroAlice()
        self.pieza_seleccionada = None
        self.tablero_seleccionado = None
        self.movimientos_validos = []
        self.turno_actual = Color.BLANCO
        self.ia = IA(Color.NEGRO)
        
        # Lista para almacenar piezas capturadas
        self.piezas_capturadas_blancas = []
        self.piezas_capturadas_negras = []
        
        # Cargar imágenes una sola vez
        self.cargar_imagenes()
        
        # Fuente para texto
        self.font = pygame.font.Font(None, 36)
        self.font_pequeño = pygame.font.Font(None, 24)  # Para las coordenadas
        
        # Cargar imagen de fondo
        try:
            self.imagen_fondo = pygame.image.load('imagenes/alice.jpg')
            self.imagen_fondo = pygame.transform.scale(self.imagen_fondo, (self.ANCHO_VENTANA, self.ALTO_VENTANA))
        except:
            print("Error al cargar la imagen de fondo")
            self.imagen_fondo = None
        
        self.ganador = None  # Nuevo atributo para almacenar el ganador

    def cargar_imagenes(self):
        self.imagenes = {}
        mapeo_nombre = {
            Pieza.PEON: 'peon',
            Pieza.TORRE: 'torre',
            Pieza.ALFIL: 'alfil',
            Pieza.CABALLO: 'caballo',
            Pieza.DAMA: 'dama',
            Pieza.REY: 'rey'
        }
        mapeo_color = {
            Color.BLANCO: 'blanco',
            Color.NEGRO: 'negro'
        }
        
        for pieza in [Pieza.PEON, Pieza.TORRE, Pieza.ALFIL, Pieza.CABALLO, Pieza.DAMA, Pieza.REY]:
            for color in [Color.BLANCO, Color.NEGRO]:
                nombre_archivo = f'imagenes/{mapeo_nombre[pieza]}_{mapeo_color[color]}.png'
                try:
                    imagen = pygame.image.load(nombre_archivo)
                    imagen = pygame.transform.scale(imagen, (self.TAMANO_CASILLA, self.TAMANO_CASILLA))
                    self.imagenes[(pieza, color)] = imagen
                except Exception as e:
                    print(f"Error cargando {nombre_archivo}: {e}")

    def ejecutar(self):
        reloj = pygame.time.Clock()
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.MOUSEBUTTONDOWN and not self.ganador:
                    if evento.button == 1:  # Click izquierdo
                        self.manejar_click()
                elif evento.type == pygame.KEYDOWN and self.ganador:
                    if evento.key == pygame.K_SPACE:  # Tecla espacio
                        self.reiniciar_juego()

            self.dibujar_tablero()
            if self.ganador:
                self.mostrar_mensaje_victoria()
            pygame.display.flip()
            reloj.tick(60)

    def dibujar_tablero(self):
        # Dibujar fondo primero
        if self.imagen_fondo:
            self.pantalla.blit(self.imagen_fondo, (0, 0))
        else:
            self.pantalla.fill((50, 50, 50))
        
        # Dibujar tableros
        for tablero_num in [1, 2]:
            # Calcular offset para cada tablero
            offset_x = self.OFFSET_X if tablero_num == 1 else self.OFFSET_X + self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS
            
            # Dibujar coordenadas de letras (a-h)
            letras = 'abcdefgh'
            for i, letra in enumerate(letras):
                # Texto de la letra con borde negro
                # Primero dibujamos el texto en negro en las 8 direcciones
                texto = self.font_pequeño.render(letra, True, (0, 0, 0))
                for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                    # Posición abajo
                    x = offset_x + i * self.TAMANO_CASILLA + (self.TAMANO_CASILLA - texto.get_width()) // 2
                    y = 8 * self.TAMANO_CASILLA + 5
                    self.pantalla.blit(texto, (x + dx, y + dy))
                    # Posición arriba
                    y = -20
                    self.pantalla.blit(texto, (x + dx, y + dy))
                
                # Luego dibujamos el texto blanco en el centro
                texto = self.font_pequeño.render(letra, True, (255, 255, 255))
                # Posición abajo
                x = offset_x + i * self.TAMANO_CASILLA + (self.TAMANO_CASILLA - texto.get_width()) // 2
                y = 8 * self.TAMANO_CASILLA + 5
                self.pantalla.blit(texto, (x, y))
                # Posición arriba
                y = -20
                self.pantalla.blit(texto, (x, y))

            # Dibujar coordenadas de números (1-8)
            numeros = '87654321'
            for i, numero in enumerate(numeros):
                # Texto del número con borde negro
                # Primero dibujamos el texto en negro en las 8 direcciones
                texto = self.font_pequeño.render(numero, True, (0, 0, 0))
                for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                    # Posición izquierda
                    x = offset_x - 20
                    y = i * self.TAMANO_CASILLA + (self.TAMANO_CASILLA - texto.get_height()) // 2
                    self.pantalla.blit(texto, (x + dx, y + dy))
                    # Posición derecha
                    x = offset_x + 8 * self.TAMANO_CASILLA + 10
                    self.pantalla.blit(texto, (x + dx, y + dy))
                
                # Luego dibujamos el texto blanco en el centro
                texto = self.font_pequeño.render(numero, True, (255, 255, 255))
                # Posición izquierda
                x = offset_x - 20
                y = i * self.TAMANO_CASILLA + (self.TAMANO_CASILLA - texto.get_height()) // 2
                self.pantalla.blit(texto, (x, y))
                # Posición derecha
                x = offset_x + 8 * self.TAMANO_CASILLA + 10
                self.pantalla.blit(texto, (x, y))
            
            # Dibujar el tablero
            for fila in range(8):
                for columna in range(8):
                    x = offset_x + columna * self.TAMANO_CASILLA
                    y = fila * self.TAMANO_CASILLA
                    color = (238, 238, 210) if (fila + columna) % 2 == 0 else (118, 150, 86)
                    pygame.draw.rect(self.pantalla, color, (x, y, self.TAMANO_CASILLA, self.TAMANO_CASILLA))
                    
                    # Resaltar casilla seleccionada
                    if self.pieza_seleccionada and self.tablero_seleccionado == tablero_num:
                        fila_sel, col_sel = self.pieza_seleccionada
                        if fila == fila_sel and columna == col_sel:
                            s = pygame.Surface((self.TAMANO_CASILLA, self.TAMANO_CASILLA))
                            s.set_alpha(128)
                            s.fill((186, 202, 43))
                            self.pantalla.blit(s, (x, y))
                    
                    # Resaltar movimientos válidos
                    if (fila, columna) in self.movimientos_validos and tablero_num == self.tablero_seleccionado:
                        s = pygame.Surface((self.TAMANO_CASILLA, self.TAMANO_CASILLA))
                        s.set_alpha(128)
                        pieza_destino = self.tablero.obtener_pieza(tablero_num, fila, columna)
                        if pieza_destino:
                            s.fill((255, 0, 0))
                        else:
                            s.fill((246, 246, 105))
                        self.pantalla.blit(s, (x, y))
                    
                    # Dibujar pieza
                    pieza = self.tablero.obtener_pieza(tablero_num, fila, columna)
                    if pieza:
                        imagen = self.imagenes.get(pieza)
                        if imagen:
                            self.pantalla.blit(imagen, (x, y))

        # Dibujar panel de capturas (ajustado a la nueva posición)
        panel_rect = pygame.Rect(2 * self.OFFSET_X + 2 * self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS, 0, 
                               300, self.ALTO_VENTANA)
        pygame.draw.rect(self.pantalla, self.COLOR_PANEL, panel_rect)
        
        # Dibujar piezas capturadas y texto
        self.dibujar_panel_capturas()
        
        # Dibujar indicador de turno
        self.dibujar_indicador_turno()
        
        pygame.display.flip()

    def dibujar_panel_capturas(self):
        # Títulos
        texto_blancas = self.font.render("Capturadas Blancas:", True, self.COLOR_TEXTO)
        texto_negras = self.font.render("Capturadas Negras:", True, self.COLOR_TEXTO)
        self.pantalla.blit(texto_blancas, (2 * self.OFFSET_X + 2 * self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS + 20, 20))
        self.pantalla.blit(texto_negras, (2 * self.OFFSET_X + 2 * self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS + 20, 300))

        # Dibujar piezas capturadas
        y_blancas = 60
        x_blancas = 2 * self.OFFSET_X + 2 * self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS + 40
        for pieza in self.piezas_capturadas_blancas:
            imagen = self.imagenes.get(pieza)
            if imagen:
                imagen_mini = pygame.transform.scale(imagen, (30, 30))
                self.pantalla.blit(imagen_mini, (x_blancas, y_blancas))
                x_blancas += 35
                if x_blancas > 2 * self.OFFSET_X + 2 * self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS + 240:  # Nueva fila
                    x_blancas = 2 * self.OFFSET_X + 2 * self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS + 40
                    y_blancas += 35

        y_negras = 340
        x_negras = 2 * self.OFFSET_X + 2 * self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS + 40
        for pieza in self.piezas_capturadas_negras:
            imagen = self.imagenes.get(pieza)
            if imagen:
                imagen_mini = pygame.transform.scale(imagen, (30, 30))
                self.pantalla.blit(imagen_mini, (x_negras, y_negras))
                x_negras += 35
                if x_negras > 2 * self.OFFSET_X + 2 * self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS + 240:  # Nueva fila
                    x_negras = 2 * self.OFFSET_X + 2 * self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS + 40
                    y_negras += 35

    def obtener_casilla_desde_mouse(self, pos_mouse):
        """Convierte la posición del mouse en coordenadas del tablero"""
        x, y = pos_mouse
        
        # Verificar en qué tablero se hizo clic
        if x < self.OFFSET_X:  # Click antes del primer tablero
            return None, -1, -1
        elif x < self.OFFSET_X + self.TAMANO_CASILLA * 8:  # Click en el primer tablero
            tablero = 1
            columna = (x - self.OFFSET_X) // self.TAMANO_CASILLA
        elif x < self.OFFSET_X + self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS:  # Click en el espacio entre tableros
            return None, -1, -1
        elif x < self.OFFSET_X + self.TAMANO_CASILLA * 16 + self.ESPACIO_ENTRE_TABLEROS:  # Click en el segundo tablero
            tablero = 2
            columna = (x - (self.OFFSET_X + self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS)) // self.TAMANO_CASILLA
        else:  # Click después del segundo tablero
            return None, -1, -1
        
        fila = y // self.TAMANO_CASILLA
        
        # Verificar que las coordenadas estén dentro del tablero
        if 0 <= fila < 8 and 0 <= columna < 8:
            return tablero, fila, columna
        return None, -1, -1

    def manejar_click(self):
        pos_mouse = pygame.mouse.get_pos()
        resultado = self.obtener_casilla_desde_mouse(pos_mouse)
        
        if resultado[0] is None:  # Si el clic fue fuera de los tableros
            return
        
        tablero, fila, columna = resultado
        letras = 'abcdefgh'
        numeros = '87654321'
        notacion = f"{letras[columna]}{numeros[fila]}"
        
        if self.pieza_seleccionada is None:
            # Mostrar información de la selección
            pieza = self.tablero.obtener_pieza(tablero, fila, columna)
            if pieza and pieza[1] == self.turno_actual:
                print(f"Pieza seleccionada en: Tablero {tablero}, {notacion}")
                self.pieza_seleccionada = (fila, columna)
                self.tablero_seleccionado = tablero
                self.movimientos_validos = self.tablero.movimientos_pieza(pieza[0], (fila, columna), tablero)
        else:
            # Mover pieza y mostrar información del movimiento
            desde_fila, desde_col = self.pieza_seleccionada
            desde_notacion = f"{letras[desde_col]}{numeros[desde_fila]}"
            
            if (fila, columna) in self.movimientos_validos:
                print(f"\nMovimiento realizado:")
                print(f"Desde: Tablero {self.tablero_seleccionado}, {desde_notacion}")
                print(f"Hasta: Tablero {tablero}, {notacion}")
                
                # Verificar si hay captura
                pieza_destino = self.tablero.obtener_pieza(tablero, fila, columna)
                if pieza_destino:
                    print(f"¡Captura! Pieza capturada: {pieza_destino[0]}")
                    if pieza_destino[1] == Color.BLANCO:
                        self.piezas_capturadas_blancas.append(pieza_destino)
                    else:
                        self.piezas_capturadas_negras.append(pieza_destino)

                # Realizar movimiento
                self.tablero.realizar_movimiento((
                    self.tablero_seleccionado,
                    (desde_fila, desde_col),
                    (fila, columna)
                ))
                
                print("------------------------")
                
                # Cambiar turno
                self.turno_actual = Color.NEGRO if self.turno_actual == Color.BLANCO else Color.BLANCO
                
                # Turno de la IA
                if self.turno_actual == Color.NEGRO:
                    print("\nTurno de la IA...")
                    self.manejar_turno_ia()
            
            # Limpiar selección
            self.pieza_seleccionada = None
            self.tablero_seleccionado = None
            self.movimientos_validos = []
        
        if self.verificar_victoria():
            color, motivo = self.ganador
            if color == "Negras":
                print("\n¡La IA ha ganado por", motivo, "!")
            else:
                print("\n¡Has ganado por", motivo, "!")
            print("Presiona ESPACIO para jugar de nuevo")
            return

    def dibujar_indicador_turno(self):
        """Dibuja el indicador de turno actual debajo de los tableros"""
        jugador_actual = "IA (Negras)" if self.turno_actual == Color.NEGRO else "Jugador (Blancas)"
        texto = f"Turno actual: {jugador_actual}"
        texto_surface = self.font.render(texto, True, self.COLOR_TEXTO)
        
        # Centrar el texto debajo de los tableros
        x = (2 * self.OFFSET_X + 2 * self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS - texto_surface.get_width()) // 2  # 960 es el ancho de los dos tableros
        y = 520 # Posición vertical debajo de los tableros
        
        # Dibujar un fondo para el texto
        padding = 10
        fondo_rect = pygame.Rect(
            x - padding, 
            y - padding, 
            texto_surface.get_width() + 2*padding, 
            texto_surface.get_height() + 2*padding
        )
        pygame.draw.rect(self.pantalla, self.COLOR_PANEL, fondo_rect)
        self.pantalla.blit(texto_surface, (x, y))

    def manejar_turno_ia(self):
        """Maneja el turno de la IA Y la animación"""
        if self.turno_actual == self.ia.color:
            mejor_movimiento = self.ia.obtener_mejor_movimiento(self.tablero)
            if mejor_movimiento:
                tablero_origen, desde_pos, hasta_pos = mejor_movimiento
                # Verificar si hay captura antes de mover
                pieza_destino = self.tablero.obtener_pieza(tablero_origen, hasta_pos[0], hasta_pos[1])
                
                # Animar el movimiento
                self.animar_movimiento(tablero_origen, desde_pos, hasta_pos)
                
                # Realizar el movimiento en el tablero
                if self.tablero.realizar_movimiento(mejor_movimiento):
                    # Si había una pieza en el destino, registrar la captura
                    if pieza_destino:
                        if pieza_destino[1] == Color.BLANCO:
                            self.piezas_capturadas_blancas.append(pieza_destino)
                        else:
                            self.piezas_capturadas_negras.append(pieza_destino)
                    
                    # Cambiar turno
                    self.turno_actual = Color.BLANCO if self.turno_actual == Color.NEGRO else Color.NEGRO
                    return True
        return False

    def animar_movimiento(self, tablero_num, desde_pos, hasta_pos):
        """Anima el movimiento de una pieza"""
        FPS = 60
        DURACION_ANIMACION = 0.5  # segundos
        frames_totales = int(FPS * DURACION_ANIMACION)
        
        # Obtener posiciones iniciales y finales en píxeles
        offset_x = self.OFFSET_X if tablero_num == 1 else self.OFFSET_X + self.TAMANO_CASILLA * 8 + self.ESPACIO_ENTRE_TABLEROS
        
        x1 = offset_x + desde_pos[1] * self.TAMANO_CASILLA
        y1 = desde_pos[0] * self.TAMANO_CASILLA
        x2 = offset_x + hasta_pos[1] * self.TAMANO_CASILLA
        y2 = hasta_pos[0] * self.TAMANO_CASILLA
        
        # Obtener la pieza que se va a mover
        pieza = self.tablero.obtener_pieza(tablero_num, desde_pos[0], desde_pos[1])
        imagen_pieza = self.imagenes.get(pieza)
        
        if not imagen_pieza:
            return
        
        reloj = pygame.time.Clock()
        
        # Realizar la animación
        for frame in range(frames_totales + 1):
            # Calcular posición actual
            progreso = frame / frames_totales
            x_actual = x1 + (x2 - x1) * progreso
            y_actual = y1 + (y2 - y1) * progreso
            
            # Redibujar el tablero
            self.dibujar_tablero()
            
            # Dibujar la pieza en su posición actual
            self.pantalla.blit(imagen_pieza, (x_actual, y_actual))
            
            pygame.display.flip()
            reloj.tick(FPS)

    def verificar_victoria(self):
        """Verifica si hay un ganador por captura del rey o jaque"""
        # Verificar si algún rey ha sido capturado
        reyes_blancos = self.contar_reyes(Color.BLANCO)
        reyes_negros = self.contar_reyes(Color.NEGRO)
        
        if reyes_blancos == 0:
            self.ganador = ("Negras", "captura")
            return True
        elif reyes_negros == 0:
            self.ganador = ("Blancas", "captura")
            return True
        
        # Verificar jaque
        for tablero_num in [1, 2]:
            for fila in range(8):
                for columna in range(8):
                    pieza = self.tablero.obtener_pieza(tablero_num, fila, columna)
                    if pieza and pieza[0] == Pieza.REY:
                        if self.tablero.esta_en_jaque(fila, columna, tablero_num):
                            if pieza[1] == Color.BLANCO:
                                self.ganador = ("Negras", "jaque")
                                return True
                            else:
                                self.ganador = ("Blancas", "jaque")
                                return True
        return False
        
    def contar_reyes(self, color):
        """Cuenta cuántos reyes quedan de un color específico"""
        contador = 0
        for tablero_num in [1, 2]:
            for fila in range(8):
                for columna in range(8):
                    pieza = self.tablero.obtener_pieza(tablero_num, fila, columna)
                    if pieza and pieza[0] == Pieza.REY and pieza[1] == color:
                        contador += 1
        return contador
        
    def mostrar_mensaje_victoria(self):
        """Muestra el mensaje de victoria y la opción de reiniciar"""
        if self.ganador:
            color, motivo = self.ganador
            if color == "Negras":
                mensaje_ganador = "¡La IA ha ganado"
            else:
                mensaje_ganador = "¡Has ganado"
            
            if motivo == "captura":
                mensaje = f"{mensaje_ganador} por captura del rey!"
            else:  # jaque
                mensaje = f"{mensaje_ganador} por jaque!"
            
            # Mensaje principal
            texto_victoria = self.font.render(mensaje, True, (255, 215, 0))
            
            # Mensaje para reiniciar
            texto_reiniciar = self.font.render("Presiona ESPACIO para jugar de nuevo", True, (255, 255, 255))
            
            # Crear un fondo semi-transparente para ambos mensajes
            altura_total = texto_victoria.get_height() + texto_reiniciar.get_height() + 20
            ancho = max(texto_victoria.get_width(), texto_reiniciar.get_width()) + 40
            
            fondo = pygame.Surface((ancho, altura_total + 30))
            fondo.fill((0, 0, 0))
            fondo.set_alpha(180)
            
            # Centrar en la pantalla
            pos_x = (self.ANCHO_VENTANA - ancho) // 2
            pos_y = (self.ALTO_VENTANA - altura_total) // 2
            
            # Dibujar fondo y mensajes
            self.pantalla.blit(fondo, (pos_x, pos_y))
            self.pantalla.blit(texto_victoria, 
                              (pos_x + (ancho - texto_victoria.get_width())//2, pos_y + 10))
            self.pantalla.blit(texto_reiniciar, 
                              (pos_x + (ancho - texto_reiniciar.get_width())//2, pos_y + texto_victoria.get_height() + 20))

    def reiniciar_juego(self):
        """Reinicia el juego a su estado inicial"""
        self.tablero = TableroAlice()
        self.pieza_seleccionada = None
        self.tablero_seleccionado = None
        self.movimientos_validos = []
        self.turno_actual = Color.BLANCO
        self.ganador = None
        self.piezas_capturadas_blancas = []
        self.piezas_capturadas_negras = []


if __name__ == "__main__":
    juego = JuegoAlice()
    juego.ejecutar() # Iniciar el juego