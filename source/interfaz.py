import sys
import psutil
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame)
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF

# --- 1. GRÁFICA ANIMADA (CON ZONA IA) ---
class GraficaAnimada(QWidget):
    def __init__(self, r_min=20, r_max=50):
        super().__init__()
        self.puntos = [random.randint(r_min, r_max) for _ in range(50)]
        self.r_min = r_min
        self.r_max = r_max
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_datos)
        self.timer.start(500)

    def actualizar_datos(self):
        nuevo_dato = random.randint(10, 95)
        self.puntos.append(nuevo_dato)
        if len(self.puntos) > 50: self.puntos.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ancho, alto = self.width(), self.height()
        paso_x = ancho / 49

        # Fondo de la gráfica (Ligeramente más claro que el negro puro)
        painter.fillRect(self.rect(), QColor("#151515"))

        # Zona Azul IA (Rango normal)
        y_max = alto - (self.r_max / 100 * alto)
        y_min = alto - (self.r_min / 100 * alto)
        painter.setBrush(QColor(52, 152, 219, 45))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, int(y_max), ancho, int(y_min - y_max))

        # Dibujar la línea de datos
        poly = QPolygonF()
        for i, valor in enumerate(self.puntos):
            poly.append(QPointF(i * paso_x, alto - (valor / 100 * alto)))

        ultimo = self.puntos[-1]
        color = QColor("#2ecc71") if self.r_min <= ultimo <= self.r_max else QColor("#e74c3c")
        painter.setPen(QPen(color, 3))
        painter.drawPolyline(poly)

# --- 2. BARRA DE PROCESO (CON TEXTO BLANCO) ---
class BarraProcesoPro(QWidget):
    def __init__(self, nombre, valor, r_min, r_max):
        super().__init__()
        self.nombre, self.valor, self.r_min, self.r_max = nombre, valor, r_min, r_max
        self.setMinimumHeight(65)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ancho, x_ini, y_ini = self.width() - 40, 10, 35
        
        dentro = self.r_min <= self.valor <= self.r_max
        color = QColor("#2ecc71") if dentro else QColor("#e74c3c")
        
        # Texto del proceso (Blanco)
        painter.setPen(QColor("white"))
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(x_ini, 20, f"{'✅' if dentro else '⚠️'} {self.nombre}: {self.valor}%")
        
        # Barra Blanca y Rango IA
        painter.setBrush(QColor("white"))
        painter.drawRect(x_ini, y_ini, ancho, 20)
        x_azul = x_ini + int((self.r_min / 100) * ancho)
        ancho_azul = int(((self.r_max - self.r_min) / 100) * ancho)
        painter.setBrush(QColor(52, 152, 219, 130))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x_azul, y_ini + 1, ancho_azul, 19)
        
        # Marcador de consumo actual
        painter.setPen(QPen(color, 4))
        x_v = x_ini + int((self.valor / 100) * ancho)
        painter.drawLine(x_v, y_ini - 4, x_v, y_ini + 24)

# --- 3. PANTALLA RECURSO (GRÁFICA + ALERTAS + SCORE) ---
class PantallaRecurso(QWidget):
    def __init__(self, titulo):
        super().__init__()
        self.setStyleSheet("background-color: #0b0b0b;")
        layout = QVBoxLayout(self)

        # Health Score arriba
        self.lbl_score = QLabel(f"Health Score: {random.randint(85, 99)}%")
        self.lbl_score.setStyleSheet("font-size: 30px; font-weight: bold; color: #2ecc71; margin-bottom: 5px;")
        layout.addWidget(self.lbl_score, alignment=Qt.AlignmentFlag.AlignCenter)

        content_h = QHBoxLayout()
        
        # Izquierda: Gráfica
        col_izq = QVBoxLayout()
        col_izq.addWidget(QLabel(f"Monitoreo: {titulo}", styleSheet="color: white; font-size: 18px;"))
        self.grafica = GraficaAnimada(35, 65)
        self.grafica.setMinimumHeight(350)
        self.grafica.setStyleSheet("border: 1px solid #333; border-radius: 12px;")
        col_izq.addWidget(self.grafica)

        # Derecha: Alertas
        alertas_w = QWidget()
        alertas_w.setFixedWidth(280)
        col_der = QVBoxLayout(alertas_w)
        lbl_a = QLabel("Alertas de procesos")
        lbl_a.setStyleSheet("color: white; font-weight: bold; font-size: 20px; margin-bottom: 10px;")
        col_der.addWidget(lbl_a)
        
        if "CPU" in titulo:
            col_der.addWidget(BarraProcesoPro("Firefox", 88, 10, 45))
            col_der.addWidget(BarraProcesoPro("System", 15, 5, 25))
        else:
            col_der.addWidget(BarraProcesoPro("Discord", 40, 10, 30))
            
        col_der.addStretch()

        content_h.addLayout(col_izq, stretch=3)
        content_h.addWidget(alertas_w)
        layout.addLayout(content_h)

# --- 4. VENTANA PRINCIPAL ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hack-UDC AI System Monitor")
        self.resize(1150, 700)

        # Contenedor central
        self.central_w = QWidget()
        self.setCentralWidget(self.central_w)
        self.main_layout = QHBoxLayout(self.central_w)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # BARRA LATERAL (Blanca)
        self.sidebar_w = QWidget()
        self.sidebar_w.setFixedWidth(220)
        self.sidebar_w.setStyleSheet("background-color: white; border-right: 2px solid #ced4da;")
        self.sidebar_lay = QVBoxLayout(self.sidebar_w)
        self.sidebar_lay.setContentsMargins(10, 30, 10, 30)
        
        self.btn_inicio = self.crear_nav_btn("🏠 Inicio")
        self.btn_cpu = self.crear_nav_btn("📊 CPU")
        self.btn_ram = self.crear_nav_btn("🧠 Memoria")
        
        self.sidebar_lay.addWidget(self.btn_inicio)
        self.sidebar_lay.addWidget(self.btn_cpu)
        self.sidebar_lay.addWidget(self.btn_ram)
        
        for part in psutil.disk_partitions():
            if 'fixed' in part.opts or part.fstype:
                btn = self.crear_nav_btn(f"💾 Disco ({part.mountpoint})")
                btn.clicked.connect(lambda ch, p=part.mountpoint: self.add_disco(p))
                self.sidebar_lay.addWidget(btn)

        self.sidebar_lay.addStretch()

        # ÁREA DE CONTENIDO (Stacked)
        self.paginas = QStackedWidget()
        
        # --- PANTALLA INICIO RESTAURADA ---
        self.p_inicio = QWidget()
        self.p_inicio.setStyleSheet("background-color: black;")
        ini_lay = QVBoxLayout(self.p_inicio)
        ini_lay.setContentsMargins(50, 50, 50, 50)
        
        texto_bienvenida = QLabel(
            "<h1 style='color: white; font-size: 36px; margin-bottom: 10px;'>Monitor de Salud Inteligente</h1>"
            "<p style='font-size: 19px; color: #aaaaaa; line-height: 1.5;'>"
            "Sistema avanzado de supervisión basado en <b>Inteligencia Artificial</b> y telemetría de <b>/proc</b>.</p>"
            "<div style='background-color: #1a1a1a; padding: 25px; border-radius: 12px; border: 1px solid #333; margin-top: 30px;'>"
            "<h3 style='color: white; font-size: 24px;'>Leyenda de Análisis IA</h3>"
            "<ul style='font-size: 18px; color: #cccccc; line-height: 2.2;'>"
            "<li><span style='color: #3498db;'>■</span> <b>Zona Azul:</b> Rango de normalidad calculado por la IA.</li>"
            "<li><span style='color: #2ecc71;'>■</span> <b>Línea Verde:</b> El consumo actual es estable y correcto.</li>"
            "<li><span style='color: #e74c3c;'>■</span> <b>Línea Roja:</b> ⚠️ <b>¡Anomalía detectada!</b> Fuera de rango habitual.</li>"
            "</ul></div>"
        )
        texto_bienvenida.setWordWrap(True)
        ini_lay.addWidget(texto_bienvenida)
        ini_lay.addStretch()
        
        # Añadir al Stacked
        self.paginas.addWidget(self.p_inicio)
        self.paginas.addWidget(PantallaRecurso("CPU"))
        self.paginas.addWidget(PantallaRecurso("Memoria"))

        # Navegación
        self.btn_inicio.clicked.connect(lambda: self.paginas.setCurrentIndex(0))
        self.btn_cpu.clicked.connect(lambda: self.paginas.setCurrentIndex(1))
        self.btn_ram.clicked.connect(lambda: self.paginas.setCurrentIndex(2))

        # Unir todo
        self.main_layout.addWidget(self.sidebar_w)
        self.main_layout.addWidget(self.paginas)

    def crear_nav_btn(self, t):
        b = QPushButton(t)
        b.setStyleSheet("""
            QPushButton { border: none; color: black; text-align: left; padding: 15px; font-size: 15px; font-weight: bold; border-radius: 8px; }
            QPushButton:hover { background-color: #f1f3f5; }
        """)
        return b

    def add_disco(self, p):
        nueva = PantallaRecurso(f"Disco {p}")
        self.paginas.addWidget(nueva)
        self.paginas.setCurrentWidget(nueva)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())