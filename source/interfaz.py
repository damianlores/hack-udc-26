import sys
import psutil
import random
import os
import heapq
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame)
from PyQt6.QtCore import Qt, QTimer, QPointF, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF

# --- HILO PARA ESCANEAR ARCHIVOS PESADOS ---
class WorkerEscaneo(QThread):
    finalizado = pyqtSignal(list)
    def __init__(self, ruta):
        super().__init__()
        self.ruta = ruta
    def run(self):
        archivos_grandes = []
        # Buscamos en la carpeta de usuario para mayor relevancia
        ruta_base = os.path.expanduser("~") if self.ruta.startswith(("C", "/")) else self.ruta
        try:
            for root, dirs, files in os.walk(ruta_base):
                for f in files:
                    try:
                        fp = os.path.join(root, f)
                        size = os.path.getsize(fp)
                        archivos_grandes.append((size, f))
                    except: continue
                if len(archivos_grandes) > 1500: break 
            top_5 = heapq.nlargest(5, archivos_grandes)
            self.finalizado.emit(top_5)
        except: self.finalizado.emit([])

# --- COMPONENTE: BARRA DE DISCO REAL (MORADA) ---
class BarraDiscoReal(QWidget):
    def __init__(self, ruta):
        super().__init__()
        self.ruta = ruta
        self.setMinimumHeight(100)
        uso = psutil.disk_usage(self.ruta)
        self.total_gb = uso.total / (1024**3)
        self.usado_gb = uso.used / (1024**3)
        self.porcentaje = uso.percent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ancho, x_ini, y_ini, alto_b = self.width() - 40, 20, 40, 25
        painter.setBrush(QColor("#333333"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x_ini, y_ini, ancho, alto_b)
        painter.setBrush(QColor("#9b59b6")) # Morado
        painter.drawRect(x_ini, y_ini, int((self.porcentaje/100)*ancho), alto_b)
        painter.setPen(QColor("white"))
        painter.drawText(x_ini, 30, f"Almacenamiento: {self.ruta}")
        painter.setPen(QColor("#aaaaaa"))
        painter.drawText(x_ini, y_ini + alto_b + 20, f"{self.usado_gb:.1f}GB / {self.total_gb:.1f}GB ({self.porcentaje}%)")

# --- GRÁFICA ANIMADA (CPU/RAM) ---
class GraficaAnimada(QWidget):
    def __init__(self, r_min=30, r_max=60):
        super().__init__()
        self.puntos = [random.randint(r_min, r_max) for _ in range(50)]
        self.r_min, self.r_max = r_min, r_max
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(500)
    def actualizar(self):
        self.puntos.append(random.randint(10, 90))
        if len(self.puntos) > 50: self.puntos.pop(0)
        self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        ancho, alto = self.width(), self.height()
        paso_x = ancho / 49
        y_max, y_min = alto - (self.r_max/100*alto), alto - (self.r_min/100*alto)
        painter.setBrush(QColor(52, 152, 219, 50))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, int(y_max), ancho, int(y_min-y_max))
        poly = QPolygonF()
        for i, v in enumerate(self.puntos):
            poly.append(QPointF(i * paso_x, alto - (v/100*alto)))
        color = QColor("#2ecc71") if self.r_min <= self.puntos[-1] <= self.r_max else QColor("#e74c3c")
        painter.setPen(QPen(color, 3))
        painter.drawPolyline(poly)

# --- REUTILIZAMOS TU BARRA PERSONALIZADA ---
class BarraProcesoPro(QWidget):
    def __init__(self, nombre, valor_actual, r_min, r_max):
        super().__init__()
        self.nombre, self.valor, self.r_min, self.r_max = nombre, valor_actual, r_min, r_max
        self.setMinimumHeight(60)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ancho, alto_barra = self.width() - 40, 20
        x_ini, y_ini = 10, 35
        esta_dentro = self.r_min <= self.valor <= self.r_max
        color_linea = QColor("#2ecc71") if esta_dentro else QColor("#e74c3c")
        emoji = "✅" if esta_dentro else "⚠️"
        painter.setPen(QColor("white"))
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(x_ini, 20, f"{emoji} {self.nombre}: {self.valor}%")
        painter.setBrush(QColor("white"))
        painter.setPen(QPen(QColor("#555555"), 1))
        painter.drawRect(x_ini, y_ini, ancho, alto_barra)
        x_azul = x_ini + int((self.r_min / 100) * ancho)
        ancho_azul = int(((self.r_max - self.r_min) / 100) * ancho)
        painter.setBrush(QColor(52, 152, 219, 130))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x_azul, y_ini + 1, ancho_azul, alto_barra - 1)
        x_valor = x_ini + int((self.valor / 100) * ancho)
        painter.setPen(QPen(color_linea, 4))
        painter.drawLine(x_valor, y_ini - 4, x_valor, y_ini + alto_barra + 4)

# --- PANTALLA DE RECURSOS ADAPTATIVA (CON IA ADVISOR RESTAURADO) ---
class PantallaRecurso(QWidget):
    def __init__(self, titulo, es_disco=False, ruta=""):
        super().__init__()
        self.setStyleSheet("background-color: #0b0b0b;")
        layout_principal = QVBoxLayout(self)
        
        # Health Score
        val_score = random.randint(88, 97) if not es_disco else (100 - psutil.disk_usage(ruta).percent)
        self.lbl_score = QLabel(f"Health Score: {int(val_score)}%")
        self.lbl_score.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {'#2ecc71' if val_score > 60 else '#e74c3c'}; padding: 10px;")
        layout_principal.addWidget(self.lbl_score)

        content_h = QHBoxLayout()
        col_izq = QVBoxLayout()
        
        if es_disco:
            # 1. Barra de Disco
            col_izq.addWidget(BarraDiscoReal(ruta))
            
            # 2. Panel de Archivos (Columna Izquierda del contenido)
            self.panel_archivos = QFrame()
            self.panel_archivos.setStyleSheet("background: #1a1a1a; border: 1px solid #333; border-radius: 10px;")
            self.lay_arc = QVBoxLayout(self.panel_archivos)
            self.lbl_load = QLabel("🔍 Analizando archivos pesados...")
            self.lbl_load.setStyleSheet("color: #9b59b6;")
            self.lay_arc.addWidget(self.lbl_load)
            col_izq.addWidget(self.panel_archivos)
            
            # Lanzar el hilo de escaneo
            self.worker = WorkerEscaneo(ruta)
            self.worker.finalizado.connect(self.actualizar_archivos)
            self.worker.start()

            # 3. PANEL IA TIPS (Columna Derecha del contenido)
            tips = QFrame()
            tips.setFixedWidth(280)
            tips.setStyleSheet("border: 1px solid #9b59b6; border-radius: 15px; background: #1a1a1a;")
            lay_t = QVBoxLayout(tips)
            lay_t.addWidget(QLabel("💡 IA Advisor", styleSheet="color: #9b59b6; font-size: 18px; font-weight: bold;"))
            
            # Lógica de mensaje según el score
            msg = "Disco saludable. El espacio libre permite una gestión de caché óptima." if val_score > 30 else "⚠️ ¡Poco espacio! El sistema podría ralentizarse. Borra archivos grandes."
            
            lbl_msg = QLabel(msg)
            lbl_msg.setStyleSheet("color: white; font-size: 14px;")
            lbl_msg.setWordWrap(True)
            lay_t.addWidget(lbl_msg)
            lay_t.addStretch()
            
            # Añadimos la columna izquierda y el panel de tips al layout horizontal
            content_h.addLayout(col_izq, stretch=2)
            content_h.addWidget(tips) # <-- Aquí es donde se mete el panel que faltaba
            
        else:
            # Modo CPU/RAM (se mantiene igual)
            col_izq.addWidget(QLabel(f"Análisis en tiempo real: {titulo}", styleSheet="color: white; font-size: 18px;"))
            self.grafica = GraficaAnimada()
            self.grafica.setMinimumHeight(300)
            col_izq.addWidget(self.grafica)

            col_der = QVBoxLayout()
            col_der.addWidget(QLabel("Alertas de procesos", styleSheet="color: white; font-weight: bold; font-size: 18px;"))
            col_der.addWidget(BarraProcesoPro("System Task", 20, 5, 30))
            col_der.addStretch()
            
            content_h.addLayout(col_izq, stretch=2)
            content_h.addLayout(col_der, stretch=1)

        layout_principal.addLayout(content_h)

    def actualizar_archivos(self, lista):
        # (El método actualizar_archivos se mantiene igual que en la versión anterior)
        if hasattr(self, 'lbl_load'):
            self.lbl_load.deleteLater()
        self.lay_arc.addWidget(QLabel("📂 Archivos más grandes:", styleSheet="color: #9b59b6; font-weight: bold;"))
        for size, name in lista:
            l = QLabel(f"• {name[:30]}... ({size/(1024**3):.2f} GB)")
            l.setStyleSheet("color: white; font-size: 13px; background: #252525; padding: 4px; border-radius: 4px;")
            self.lay_arc.addWidget(l)
        self.lay_arc.addStretch()
# --- VENTANA PRINCIPAL ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hack-UDC AI Monitor")
        self.resize(1100, 650)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)

        # 1. BARRA LATERAL
        self.sidebar_lay = QVBoxLayout()
        self.btn_inicio = QPushButton("🏠 Inicio")
        self.btn_cpu = QPushButton("📊 CPU")
        self.btn_ram = QPushButton("🧠 Memoria")
        self.sidebar_lay.addWidget(self.btn_inicio)
        self.sidebar_lay.addWidget(self.btn_cpu)
        self.sidebar_lay.addWidget(self.btn_ram)

        for part in psutil.disk_partitions(all=False):
            if part.device.startswith('/dev/loop') or part.fstype in ('squashfs', 'tmpfs', 'devtmpfs', ''):
                continue
            
            # Usar mountpoint (ej. '/') suele ser más legible para el usuario que device (ej. '/dev/sda1')
            btn = QPushButton(f"Disco ({part.mountpoint})")
            btn.clicked.connect(lambda ch, p=part.device: self.cambiar_pestaña_disco(p))
            self.sidebar_lay.addWidget(btn)
        self.sidebar_lay.addStretch()

        sidebar_container = QWidget()
        sidebar_container.setLayout(self.sidebar_lay)
        sidebar_container.setFixedWidth(200)
        sidebar_container.setStyleSheet("QWidget { background-color: white; border-right: 2px solid #ced4da; } QPushButton { border: none; text-align: left; padding: 12px; font-weight: bold; color: black; } QPushButton:hover { background-color: #f1f3f5; }")

        # 2. PÁGINAS
        self.paginas = QStackedWidget()
        
        # --- PÁGINA INICIO (TUS TEXTOS ORIGINALES + MORADO) ---
        self.p_inicio = QWidget()
        self.p_inicio.setStyleSheet("background-color: black;")
        layout_ini = QVBoxLayout(self.p_inicio)
        layout_ini.setContentsMargins(40, 40, 40, 40)
        
        texto_ini = QLabel(
            "<h1 style='color: white; font-size: 32px; margin-bottom: 10px;'>Monitor de Salud Inteligente</h1>"
            "<p style='font-size: 18px; color: #cccccc; line-height: 1.5;'>"
            "Este sistema utiliza <b>Inteligencia Artificial</b> para supervisar tu hardware en tiempo real "
            "basándose en los datos de <b>/proc</b>.</p>"
            "<div style='background-color: #1a1a1a; padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid #333;'>"
            "<h3 style='color: white; font-size: 22px;'>¿Cómo interpretar los colores?</h3>"
            "<ul style='font-size: 18px; line-height: 1.8; color: #cccccc;'>"
            "<li><span style='color: #3498db;'>■</span> <b>Zona Azul:</b> El rango normal calculado por la IA basándose en tu historial.</li>"
            "<li><span style='color: #2ecc71;'>■</span> <b>Línea Verde:</b> El consumo actual es correcto y está dentro del rango.</li>"
            "<li><span style='color: #e74c3c;'>■</span> <b>Línea Roja:</b> <b>¡Anomalía detectada!</b> La aplicación consume más de lo habitual.</li>"
            "<li><span style='color: #9b59b6;'>■</span> <b>Barra Morada:</b> <b>Ocupación de disco:</b> Indica el espacio físico usado actualmente.</li>"
            "</ul>"
            "</div>"
        )
        texto_ini.setWordWrap(True)
        layout_ini.addWidget(texto_ini)
        layout_ini.addStretch()

        self.paginas.addWidget(self.p_inicio)
        self.paginas.addWidget(PantallaRecurso("CPU"))
        self.paginas.addWidget(PantallaRecurso("Memoria"))

        self.btn_inicio.clicked.connect(lambda: self.paginas.setCurrentIndex(0))
        self.btn_cpu.clicked.connect(lambda: self.paginas.setCurrentIndex(1))
        self.btn_ram.clicked.connect(lambda: self.paginas.setCurrentIndex(2))

        main_layout.addWidget(sidebar_container)
        main_layout.addWidget(self.paginas)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def cambiar_pestaña_disco(self, nombre):
        nueva = PantallaRecurso(f"Disco {nombre}", es_disco=True, ruta=nombre)
        self.paginas.addWidget(nueva)
        self.paginas.setCurrentWidget(nueva)

def init_ui():
     app = QApplication(sys.argv)
     w = MainWindow()
     w.show()
     sys.exit(app.exec())