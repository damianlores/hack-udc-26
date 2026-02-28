import sys
import psutil
import datetime
import os
import heapq
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QPointF, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF

# --- HILO GLOBAL DE PROCESOS ---
class WorkerProcesos(QThread):
    datos_actualizados = pyqtSignal(list)

    def run(self):
        try:
            from resources import obtain_process_data
        except ImportError:
            def obtain_process_data(): return []

        while True:
            try:
                procesos = obtain_process_data()
                self.datos_actualizados.emit(procesos[:10])
            except Exception as e:
                print(f"Error en escaneo de procesos: {e}")
            self.msleep(3000)

# --- HILO PARA ESCANEAR ARCHIVOS PESADOS ---
class WorkerEscaneo(QThread):
    finalizado = pyqtSignal(list)
    def __init__(self, ruta):
        super().__init__()
        self.ruta = ruta
    def run(self):
        archivos_grandes = []
        ruta_base = os.path.expanduser("~") if self.ruta.startswith(("C", "/")) else self.ruta
        try:
            for root, dirs, files in os.walk(ruta_base):
                for f in files:
                    try:
                        fp = os.path.join(root, f)
                        size = os.path.getsize(fp)
                        archivos_grandes.append((size, f))
                    except: continue
                if len(archivos_grandes) > 1000: break 
            top_5 = heapq.nlargest(5, archivos_grandes)
            self.finalizado.emit(top_5)
        except: self.finalizado.emit([])

# --- COMPONENTE: BARRA DE DISCO REAL ---
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
        painter.setBrush(QColor("#9b59b6")) 
        painter.drawRect(x_ini, y_ini, int((self.porcentaje/100)*ancho), alto_b)
        painter.setPen(QColor("white"))
        painter.drawText(x_ini, 30, f"Almacenamiento: {self.ruta}")
        painter.setPen(QColor("#aaaaaa"))
        painter.drawText(x_ini, y_ini + alto_b + 20, f"{self.usado_gb:.1f}GB / {self.total_gb:.1f}GB ({self.porcentaje}%)")

# --- GRÁFICA ANIMADA ---
class GraficaAnimada(QWidget):
    def __init__(self):
        super().__init__()
        self.puntos = [0.0 for _ in range(50)]
        self.r_min, self.r_max = 30, 70
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(500)

    def actualizar(self):
        uso_cpu = psutil.cpu_percent(interval=None)
        self.puntos.append(uso_cpu)
        if len(self.puntos) > 50: self.puntos.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        ancho, alto = self.width(), self.height()
        paso_x = ancho / 49
        y_max = alto - (self.r_max / 100 * alto)
        y_min = alto - (self.r_min / 100 * alto)
        painter.setBrush(QColor(52, 152, 219, 40))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, int(y_max), ancho, int(y_min - y_max))
        poly = QPolygonF()
        for i, v in enumerate(self.puntos):
            y_pos = alto - (v / 100 * alto)
            poly.append(QPointF(i * paso_x, y_pos))
        ultimo_valor = self.puntos[-1]
        color = QColor("#2ecc71") if ultimo_valor <= self.r_max else QColor("#e74c3c")
        painter.setPen(QPen(color, 3))
        painter.drawPolyline(poly)

# --- BARRA DE PROCESO INDIVIDUAL ---
class BarraProcesoPro(QWidget):
    def __init__(self, nombre, valor_actual, r_min, r_max):
        super().__init__()
        self.nombre, self.valor, self.r_min, self.r_max = nombre, valor_actual, r_min, r_max
        self.setMinimumHeight(50)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ancho = self.width() - 40
        alto_barra = 15
        x_ini, y_ini = 10, 30
        esta_dentro = self.valor <= self.r_max
        color_linea = QColor("#2ecc71") if esta_dentro else QColor("#e74c3c")
        painter.setPen(QColor("white"))
        painter.drawText(x_ini, 20, f"{self.nombre}: {self.valor}%")
        painter.setBrush(QColor("#333333"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x_ini, y_ini, ancho, alto_barra)
        x_valor = x_ini + int((min(self.valor, 100) / 100) * ancho)
        painter.setBrush(color_linea)
        painter.drawRect(x_ini, y_ini, x_valor - x_ini, alto_barra)

# --- PANTALLA DE RECURSOS (MODIFICADA CON DATOS REALES) ---
class PantallaRecurso(QWidget):
    def __init__(self, titulo, es_disco=False, ruta=""):
        super().__init__()
        self.titulo = titulo
        self.setStyleSheet("background-color: #0b0b0b;")
        layout_principal = QVBoxLayout(self)
        content_h = QHBoxLayout()
        col_izq = QVBoxLayout()
        
        if es_disco:
            col_izq.addWidget(BarraDiscoReal(ruta))
            self.panel_archivos = QFrame()
            self.panel_archivos.setStyleSheet("background: #1a1a1a; border: 1px solid #333; border-radius: 10px;")
            self.lay_arc = QVBoxLayout(self.panel_archivos)
            self.lbl_load = QLabel("Analizando archivos pesados...")
            self.lbl_load.setStyleSheet("color: #9b59b6;")
            self.lay_arc.addWidget(self.lbl_load)
            col_izq.addWidget(self.panel_archivos)
            
            self.worker_disk = WorkerEscaneo(ruta)
            self.worker_disk.finalizado.connect(self.actualizar_archivos)
            self.worker_disk.start()

            tips = QFrame()
            tips.setFixedWidth(280)
            tips.setStyleSheet("border: 1px solid #9b59b6; border-radius: 15px; background: #1a1a1a;")
            lay_t = QVBoxLayout(tips)
            lay_t.addWidget(QLabel("IA Advisor", styleSheet="color: #9b59b6; font-size: 18px; font-weight: bold;"))
            
            porcentaje_uso = psutil.disk_usage(ruta).percent
            msg = "Disco saludable. El espacio libre permite una gestión de caché óptima." if porcentaje_uso < 70 else "Poco espacio libre detectado. Se recomienda limpieza."
            
            lbl_msg = QLabel(msg)
            lbl_msg.setStyleSheet("color: white; font-size: 14px;")
            lbl_msg.setWordWrap(True)
            lay_t.addWidget(lbl_msg)
            lay_t.addStretch()
            
            content_h.addLayout(col_izq, stretch=2)
            content_h.addWidget(tips)
            
        else:
            col_izq.addWidget(QLabel(f"Monitor de {titulo}", styleSheet="color: white; font-size: 22px; font-weight: bold; margin-bottom: 5px;"))
            
            # Panel de KPIs
            panel_kpi = QFrame()
            panel_kpi.setStyleSheet("background-color: #1a1a1a; border-radius: 12px; border: 1px solid #333;")
            lay_kpi = QHBoxLayout(panel_kpi)
            lay_kpi.setContentsMargins(20, 15, 20, 15)
            
            # Cálculo de Uptime (Tiempo de uso del sistema)
            uptime_seconds = int(datetime.datetime.now().timestamp() - psutil.boot_time())
            uptime_str = str(datetime.timedelta(seconds=uptime_seconds))

            if titulo == "CPU":
                val_principal = f"{psutil.cpu_percent()}%"
                val_hardware = f"{psutil.cpu_count(logical=False)} núcleos / {psutil.cpu_count()} hilos"
                lbl_desc = "Carga Total"
            else:
                mem = psutil.virtual_memory()
                val_principal = f"{mem.percent}%"
                
                # --- CAMBIO AQUÍ: Uso Real / Total ---
                usado = mem.used / (1024**3)
                total = mem.total / (1024**3)
                val_hardware = f"{usado:.1f} / {total:.1f} GB"
                # -------------------------------------
                
                lbl_desc = "Uso de RAM"

            # Tarjeta 1: Carga/Uso
            card1 = QVBoxLayout(); card1.addWidget(QLabel(lbl_desc, styleSheet="color: #888; font-size: 12px;"))
            card1.addWidget(QLabel(val_principal, styleSheet="color: white; font-size: 26px; font-weight: bold;"))
            
            # Tarjeta 2: Hardware (Núcleos/Hilos o RAM Total)
            card2 = QVBoxLayout(); card2.addWidget(QLabel("Hardware", styleSheet="color: #888; font-size: 12px;"))
            card2.addWidget(QLabel(val_hardware, styleSheet="color: #3498db; font-size: 15px; font-weight: bold;"))
            
            # Tarjeta 3: Tiempo de uso (Uptime)
            card3 = QVBoxLayout(); card3.addWidget(QLabel("Tiempo de Uso", styleSheet="color: #888; font-size: 12px;"))
            card3.addWidget(QLabel(uptime_str, styleSheet="color: #f1c40f; font-size: 15px; font-weight: bold;"))

            lay_kpi.addLayout(card1); lay_kpi.addLayout(card2); lay_kpi.addLayout(card3)
            col_izq.addWidget(panel_kpi)

            lbl_graph = QLabel("Histórico de rendimiento:")
            lbl_graph.setStyleSheet("color: #666; font-size: 12px; margin-top: 10px;")
            col_izq.addWidget(lbl_graph)
            col_izq.addWidget(GraficaAnimada())

            col_der = QVBoxLayout()
            col_der.addWidget(QLabel("Procesos Activos", styleSheet="color: white; font-weight: bold; font-size: 16px;"))
            self.scroll = QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
            self.container_procesos = QWidget()
            self.lay_procesos = QVBoxLayout(self.container_procesos)
            self.scroll.setWidget(self.container_procesos)
            col_der.addWidget(self.scroll)
            
            content_h.addLayout(col_izq, stretch=2)
            content_h.addLayout(col_der, stretch=1)

        layout_principal.addLayout(content_h)

    def refrescar_lista_procesos(self, lista):
        if not hasattr(self, 'lay_procesos'): return
        while self.lay_procesos.count():
            item = self.lay_procesos.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        for p in lista:
            barra = BarraProcesoPro(p['name'][:15], p['cpu_percent'], 0, 20)
            self.lay_procesos.addWidget(barra)
        self.lay_procesos.addStretch()

    def actualizar_archivos(self, lista):
        if hasattr(self, 'lbl_load'): self.lbl_load.deleteLater()
        self.lay_arc.addWidget(QLabel("Archivos más grandes:", styleSheet="color: #9b59b6; font-weight: bold;"))
        for size, name in lista:
            l = QLabel(f"- {name[:20]} ({size/(1024**3):.2f} GB)")
            l.setStyleSheet("color: white; font-size: 12px; background: #252525; padding: 3px; border-radius: 4px;")
            self.lay_arc.addWidget(l)
        self.lay_arc.addStretch()

# --- VENTANA PRINCIPAL ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hack-UDC AI Monitor")
        self.resize(1100, 650)
        self.worker_global = WorkerProcesos()

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)

        # 1. BARRA LATERAL
        self.sidebar_lay = QVBoxLayout()
        self.btn_inicio = QPushButton("Inicio")
        self.btn_cpu = QPushButton("CPU")
        self.btn_ram = QPushButton("Memoria")
        self.sidebar_lay.addWidget(self.btn_inicio)
        self.sidebar_lay.addWidget(self.btn_cpu)
        self.sidebar_lay.addWidget(self.btn_ram)

        for part in psutil.disk_partitions(all=False):
            if part.fstype in ('squashfs', 'tmpfs', ''): continue
            btn = QPushButton(f"Disco ({part.mountpoint})")
            btn.clicked.connect(lambda ch, p=part.mountpoint: self.cambiar_pestaña_disco(p))
            self.sidebar_lay.addWidget(btn)
        self.sidebar_lay.addStretch()

        sidebar_container = QWidget()
        sidebar_container.setLayout(self.sidebar_lay)
        sidebar_container.setFixedWidth(200)
        sidebar_container.setStyleSheet("""
            QWidget { background-color: white; border-right: 1px solid #ced4da; } 
            QPushButton { border: none; text-align: left; padding: 12px; font-weight: bold; color: black; } 
            QPushButton:hover { background-color: #f1f3f5; }
        """)

        # 2. PÁGINAS
        self.paginas = QStackedWidget()
        self.p_inicio = self.crear_inicio()
        self.p_cpu = PantallaRecurso("CPU")
        self.p_ram = PantallaRecurso("Memoria")

        self.worker_global.datos_actualizados.connect(self.p_cpu.refrescar_lista_procesos)
        self.worker_global.datos_actualizados.connect(self.p_ram.refrescar_lista_procesos)

        self.paginas.addWidget(self.p_inicio)
        self.paginas.addWidget(self.p_cpu)
        self.paginas.addWidget(self.p_ram)

        self.btn_inicio.clicked.connect(lambda: self.paginas.setCurrentIndex(0))
        self.btn_cpu.clicked.connect(lambda: self.paginas.setCurrentIndex(1))
        self.btn_ram.clicked.connect(lambda: self.paginas.setCurrentIndex(2))

        main_layout.addWidget(sidebar_container)
        main_layout.addWidget(self.paginas)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.worker_global.start()

    def crear_inicio(self):
        w = QWidget()
        w.setStyleSheet("background-color: black;")
        layout_ini = QVBoxLayout(w)
        layout_ini.setContentsMargins(40, 40, 40, 40)
        
        texto_ini = QLabel(
            "<h1 style='color: white; font-size: 32px; margin-bottom: 10px;'>Monitor de Salud Inteligente</h1>"
            "<p style='font-size: 18px; color: #cccccc; line-height: 1.5;'>"
            "Bienvenido al panel de control. Este sistema supervisa tu hardware en tiempo real "
            "evaluando el impacto de cada proceso en tu sistema.</p>"
            "<div style='background-color: #1a1a1a; padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid #333;'>"
            "<h3 style='color: white; font-size: 22px;'>Guía de Colores y Alertas</h3>"
            "<ul style='font-size: 18px; line-height: 1.8; color: #cccccc;'>"
            "<li><span style='color: #2ecc71;'>■</span> <b>Verde (Procesos):</b> El consumo del proceso es estable y predecible.</li>"
            "<li><span style='color: #e74c3c;'>■</span> <b>Rojo (Procesos):</b> ¡Alerta! El proceso está consumiendo más recursos de los recomendados.</li>"
            "<li><span style='color: #9b59b6;'>■</span> <b>Morado (Discos):</b> Representa la ocupación física actual de tus unidades de almacenamiento.</li>"
            "</ul>"
            "</div>"
        )
        texto_ini.setWordWrap(True)
        layout_ini.addWidget(texto_ini)
        layout_ini.addStretch()
        return w

    def cambiar_pestaña_disco(self, ruta):
        nueva = PantallaRecurso(f"Disco {ruta}", es_disco=True, ruta=ruta)
        self.paginas.addWidget(nueva)
        self.paginas.setCurrentWidget(nueva)

def init_ui():
     app = QApplication(sys.argv)
     w = MainWindow(); w.show()
     sys.exit(app.exec())



# interfaz.py
class WorkerProcesos(QThread):
    datos_actualizados = pyqtSignal(list, str)

    def __init__(self):
        super().__init__()
        from resources import HistorialRecursos
        self.historial = HistorialRecursos(capacidad=5)

    def run(self):
        from resources import save_process_data
        from prompt import generate_response
        
        while True:
            # 1. Recopila los datos usando save_process_data
            datos_completos = save_process_data()
            top_10 = datos_completos[:10]
            
            # 2. Almacena el sample actual
            self.historial.registrar_muestreo(top_10)
            
            analisis_ia = "Recopilando datos iniciales (Muestreo {}/5)...".format(len(self.historial.muestreos))
            
            # 3. Solo pide el prompt si ya hay 5 samples
            if self.historial.esta_listo():
                prompt_input = self.historial.formatear_para_ia()
                instruccion = (
                    f"Analiza estos 5 samples de procesos:\n{prompt_input}\n"
                    "Determina si hay algún proceso cuya CPU o RAM esté aumentando constantemente. "
                    "Responde brevemente."
                )
                analisis_ia = generate_response(instruccion)
            
            # 4. Actualiza la UI con los 10 procesos y el estado de la IA
            self.datos_actualizados.emit(top_10, analisis_ia)
            
            # Pausa de 3 segundos entre capturas
            self.msleep(3000)
