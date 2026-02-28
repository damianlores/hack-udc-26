import sys
import psutil
import datetime
import os
import heapq
from dotenv import load_dotenv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame, QScrollArea, QTextEdit)
from PyQt6.QtCore import Qt, QTimer, QPointF, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF

from plyer import notification  # <--- Para las notificaciones de Windows/Linux

# --- HILO GLOBAL DE PROCESOS ---
class WorkerProcesos(QThread):
    processes_data = pyqtSignal(list, str) # Lista de procesos + mensaje IA
    
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def run(self):
        from resources import obtain_process_data, save_process_data, ResourceHistoric
        from ai import analyze_samples
        
        historic = ResourceHistoric(capacity=5)
        context = "Sin contexto previo."
        message = "Recopilando datos para análisis de comportamiento..."

        while True:
            try:
                # 1. Obtener datos ligeros para las barras de la interfaz
                processes_ui = obtain_process_data()
                
                # 2. Obtener datos detallados para el análisis de la IA
                # Nota: save_process_data realiza un muestreo interno
                processes_ai = save_process_data()
                historic.save_sample(processes_ai[:10])
                
                # 3. Procesar bloque de IA si el historial está lleno (5 muestras)
                if historic.is_ready():
                    samples = historic.build_samples()
                    # La función build_samples debe limpiar el historial tras generar el texto
                    response = analyze_samples(context, samples, self.api_key)
                    context = response
                    message = response

                    # Lógica de notificación de sistema ante alertas
                    if "ALERTA:" in message.upper():
                        from plyer import notification
                        try:
                            notification.notify(
                                title='Monitor de Sistema',
                                message=message[:100],
                                timeout=10
                            )
                        except:
                            pass

                # 4. Emitir datos a la interfaz gráfica
                self.processes_data.emit(processes_ui, message)
                
            except Exception as e:
                print(f"Error en WorkerProcesos: {e}")
            
            # Pausa ajustada para compensar el tiempo de muestreo de save_process_data
            self.msleep(2500)

# --- HILO PARA ESCANEAR ARCHIVOS PESADOS ---
class WorkerEscaneo(QThread):
    finished = pyqtSignal(list)
    def __init__(self, ruta):
        super().__init__()
        self.ruta = ruta
    def run(self):
        big_files = []
        ruta_base = self.ruta if os.path.exists(self.ruta) else os.path.expanduser("~")
        try:
            for root, dirs, files in os.walk(ruta_base):
                for f in files:
                    try:
                        fp = os.path.join(root, f)
                        size = os.path.getsize(fp)
                        big_files.append((size, f))
                    except: continue
                if len(big_files) > 1000: break 
            top_5 = heapq.nlargest(10, big_files)
            self.finished.emit(top_5)
        except: self.finished.emit([])

# --- COMPONENTE: BARRA DE DISCO REAL ---
class BarraDiscoReal(QWidget):
    def __init__(self, ruta):
        super().__init__()
        self.ruta = ruta
        self.setMinimumHeight(100)
        try:
            uso = psutil.disk_usage(self.ruta)
            self.total_gb = uso.total / (1024**3)
            self.usado_gb = uso.used / (1024**3)
            self.porcentaje = uso.percent
        except:
            self.total_gb, self.usado_gb, self.porcentaje = 0, 0, 0

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
    def __init__(self, tipo="CPU"):
        super().__init__()
        self.tipo = tipo
        self.puntos = [0.0 for _ in range(50)]
        self.r_min, self.r_max = 30, 70
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(500)

    def actualizar(self):
        # Las gráficas consultan directamente psutil para evitar latencia
        if self.tipo == "CPU":
            valor = psutil.cpu_percent(interval=None)
        else:
            valor = psutil.virtual_memory().percent
            
        self.puntos.append(valor)
        if len(self.puntos) > 50: self.puntos.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        ancho, alto = self.width(), self.height()
        paso_x = ancho / 49
        y_max, y_min = alto - (self.r_max/100*alto), alto - (self.r_min/100*alto)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, int(y_max), ancho, int(y_min - y_max))
        poly = QPolygonF()
        for i, v in enumerate(self.puntos):
            poly.append(QPointF(i * paso_x, alto - (v / 100 * alto)))
        color = QColor("#2ecc71") if self.puntos[-1] <= self.r_max else QColor("#e74c3c")
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

# --- PANTALLA DE RECURSOS ---
class PantallaRecurso(QWidget):
    def __init__(self, titulo, es_disco=False, ruta=""):
        super().__init__()
        self.titulo = titulo
        self.setStyleSheet("background-color: #0b0b0b;")
        layout_principal = QVBoxLayout(self)
        
        content_h = QHBoxLayout()
        col_izq = QVBoxLayout()
        col_der = QVBoxLayout()
        
        if es_disco:
            col_izq.addWidget(BarraDiscoReal(ruta))
            self.panel_archivos = QFrame()
            self.panel_archivos.setStyleSheet("background: #1a1a1a; border: 1px solid #333; border-radius: 10px;")
            self.lay_arc = QVBoxLayout(self.panel_archivos)
            self.lbl_load = QLabel("Analizando archivos pesados...")
            self.lbl_load.setStyleSheet("color: #9b59b6;")
            self.lay_arc.addWidget(self.lbl_load)
            col_izq.addWidget(self.panel_archivos)

            panel_status = QFrame()
            panel_status.setStyleSheet("background: #1a1a1a; border: 1px solid #333; border-radius: 10px;")
            lay_status = QVBoxLayout(panel_status)
            uso = psutil.disk_usage(ruta).percent
            txt_status = "ESTADO: ÓPTIMO" if uso < 80 else "ESTADO: CRÍTICO"
            col_status = "#2ecc71" if uso < 80 else "#e74c3c"
            msg_status = "Tienes espacio suficiente." if uso < 80 else "Debes vaciar espacio pronto."
            
            lay_status.addWidget(QLabel(txt_status, styleSheet=f"color: {col_status}; font-weight: bold; font-size: 16px;"))
            lay_status.addWidget(QLabel(msg_status, styleSheet="color: white;"))
            lay_status.addStretch()
            col_der.addWidget(panel_status)

            self.worker_disk = WorkerEscaneo(ruta)
            self.worker_disk.finished.connect(self.actualizar_archivos)
            self.worker_disk.start()
        else:            
            # --- TÍTULO ARRIBA ---
            lbl_tit = QLabel(f"Monitor: {titulo}")
            lbl_tit.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 5px;")
            lbl_tit.setMaximumHeight(35)
            col_izq.addWidget(lbl_tit)
            
            # --- PANEL KPI COMPACTO ---
            panel_kpi = QFrame()
            panel_kpi.setStyleSheet("background-color: #1a1a1a; border-radius: 12px; border: 1px solid #333;")
            panel_kpi.setMaximumHeight(80) 
            lay_kpi = QHBoxLayout(panel_kpi)
            lay_kpi.setContentsMargins(15, 5, 15, 5) 

            # Creamos las etiquetas vacías primero para guardarlas como atributos
            self.lbl_val_principal = QLabel("--")
            self.lbl_val_hardware = QLabel("--")
            self.lbl_val_uptime = QLabel("--")
            
            # Etiquetas de descripción
            lbl_desc_text = "Carga Total" if titulo == "CPU" else "Uso de RAM"
            
            # Estructura del panel KPI
            for t_tit, t_widget, t_col in [
                (lbl_desc_text, self.lbl_val_principal, "white"),
                ("Hardware", self.lbl_val_hardware, "#3498db"),
                ("Tiempo de Uso", self.lbl_val_uptime, "#f1c40f")
            ]:
                v_lay = QVBoxLayout()
                v_lay.setSpacing(0)
                v_lay.addWidget(QLabel(t_tit, styleSheet="color: #bbb; font-size: 11px;"))
                t_widget.setStyleSheet(f"color: {t_col}; font-size: 16px; font-weight: bold;")
                v_lay.addWidget(t_widget)
                lay_kpi.addLayout(v_lay)
                
            col_izq.addWidget(panel_kpi)

            self.grafica = GraficaAnimada(tipo=titulo)
            self.grafica.setFixedHeight(180)
            col_izq.addWidget(self.grafica)
            col_izq.addStretch()

            # --- COLUMNA DERECHA (PROCESOS) ---
            lbl_proc_tit = QLabel("Procesos Activos")
            lbl_proc_tit.setStyleSheet("color: white; font-weight: bold; margin-top: 5px;")
            col_der.addWidget(lbl_proc_tit)
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

        # Panel inferior para la IA
        self.panel_ai = QFrame()
        self.panel_ai.setStyleSheet("background-color: #121212; border: 1px solid #9b59b6; border-radius: 12px;")
        self.panel_ai.setFixedHeight(150)
        
        lay_ia = QVBoxLayout(self.panel_ai)
        
        self.label_ai = QTextEdit() 
        self.label_ai.setReadOnly(True) # Impide que el usuario edite el contenido
        self.label_ai.setPlainText("Esperando análisis de comportamiento...")
        
        # 3. Estilo para simular un Label (sin bordes y fondo transparente)
        self.label_ai.setStyleSheet("""
            background: transparent; 
            border: none; 
            color: #9b59b6; 
            font-size: 14px; 
            font-style: italic;
        """)
        
        # Eliminar la barra de desplazamiento horizontal si no es necesaria
        self.label_ai.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        lay_ia.addWidget(self.label_ai)
        layout_principal.addWidget(self.panel_ai)

    def refresh_process_list(self, lista, message):
        if not hasattr(self, 'lay_procesos'): return
        
        # --- 1. ACTUALIZAR PANEL KPI ---
        uptime_seconds = int(datetime.datetime.now().timestamp() - psutil.boot_time())
        uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
        self.lbl_val_uptime.setText(uptime_str)

        if self.titulo == "CPU":
            # Usamos interval=None para no bloquear la interfaz
            val_principal = f"{psutil.cpu_percent(interval=None)}%"
            val_hardware = f"{psutil.cpu_count(logical=False)} núcleos / {psutil.cpu_count()} hilos"
        else:
            mem = psutil.virtual_memory()
            val_principal = f"{mem.percent}%"
            val_hardware = f"{mem.used/(1024**3):.1f} / {mem.total/(1024**3):.1f} GB"
        
        self.lbl_val_principal.setText(val_principal)
        self.lbl_val_hardware.setText(val_hardware)

        # --- 2. ACTUALIZAR LISTADO DE PROCESOS ---
        while self.lay_procesos.count():
            item = self.lay_procesos.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for p in lista:
            # Importante: Asegúrate de usar la clase correcta para las barras
            self.lay_procesos.addWidget(BarraProcesoPro(p['name'][:15], p['cpu_percent'], 0, 20))
        self.lay_procesos.addStretch()
        
        # --- 3. ACTUALIZAR TEXTO DE LA IA ---
        if hasattr(self, 'label_ai'):
            self.label_ai.setPlainText(message)
            if "ALERTA:" in message.upper():
                self.label_ai.setStyleSheet("color: #ff4c4c; font-size: 14px; font-weight: bold;")
            else:
                self.label_ai.setStyleSheet("color: #9b59b6; font-size: 14px; font-style: italic;")

    def actualizar_archivos(self, lista):
        if hasattr(self, 'lbl_load'): self.lbl_load.deleteLater()
        self.lay_arc.addWidget(QLabel("Archivos más grandes:", styleSheet="color: #9b59b6; font-weight: bold;"))
        for size, name in lista:
            l = QLabel(f"- {name[:25]} ({size/(1024**3):.2f} GB)")
            l.setStyleSheet("color: white; font-size: 12px; background: #252525; padding: 4px; border-radius: 4px;")
            self.lay_arc.addWidget(l)
        self.lay_arc.addStretch()

# --- VENTANA PRINCIPAL ---
class MainWindow(QMainWindow):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.worker_global = WorkerProcesos(self.api_key)
        
        self.setWindowTitle("Hack-UDC AI Monitor")
        self.resize(1100, 650)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)

        self.sidebar_lay = QVBoxLayout()
        self.btn_inicio = QPushButton("Inicio")
        self.btn_cpu = QPushButton("CPU")
        self.btn_ram = QPushButton("Memoria")
        self.sidebar_lay.addWidget(self.btn_inicio)
        self.sidebar_lay.addWidget(self.btn_cpu)
        self.sidebar_lay.addWidget(self.btn_ram)

        for part in psutil.disk_partitions(all=False):
            if part.fstype in ('squashfs', 'tmpfs', ''): 
                continue
            # MacOS system volumes ignore
            if "/System/Volumes" in part.mountpoint and not part.mountpoint.endswith("/Data"):
                continue
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

        self.paginas = QStackedWidget()
        self.p_inicio = self.crear_inicio()
        self.p_cpu = PantallaRecurso("CPU")
        self.p_ram = PantallaRecurso("Memoria")

        self.worker_global.processes_data.connect(self.p_cpu.refresh_process_list)
        self.worker_global.processes_data.connect(self.p_ram.refresh_process_list)

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
        
        texto_html = (
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
        
        lbl_inicio = QLabel(texto_html)
        lbl_inicio.setWordWrap(True)
        layout_ini.addWidget(lbl_inicio)
        layout_ini.addStretch()
        
        return w

    def cambiar_pestaña_disco(self, ruta):
        nueva = PantallaRecurso(f"Disco {ruta}", es_disco=True, ruta=ruta)
        self.paginas.addWidget(nueva)
        self.paginas.setCurrentWidget(nueva)

def init_ui():
     app = QApplication(sys.argv)
     load_dotenv()
     api_key = os.getenv("GROQ_API_KEY")
     
     if not api_key:
         print(
             f"Error: La variable de entorno GROQ_API_KEY no está configurada.\n"
             f"Crea un archivo .env con la línea: GROQ_API_KEY=api_key_aqui\n"
             f"Obten tu API Key en https://console.groq.com/home"
             )
         sys.exit(1)
         
     w = MainWindow(api_key); w.show()
     sys.exit(app.exec())
