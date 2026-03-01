import sys
import psutil
import datetime
import os
import heapq
from dotenv import load_dotenv
from plyer import notification
from collections import deque
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QPushButton, QStackedWidget, 
                             QFrame, QScrollArea, QTextEdit, QDialog)
from PyQt6.QtCore import Qt, QTimer, QPointF, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF

class WorkerProcesses(QThread):
    
    # Process list, AI generated response and the full historic text fo popup
    processes_data = pyqtSignal(list, str, str)
    
    def __init__(self, api_key):
        super().__init__()
        # set the API key for the worker to use in AI analysis
        self.api_key = api_key
        # max 10 entries of historic AI responses
        self.historic_ai = deque(maxlen=10)

    def run(self):
        from resources import obtain_processes_data, save_processes_data, ResourceHistoric
        from ai import analyze_samples
        
        resource_historic = ResourceHistoric(capacity=5)
        context = "Sin contexto previo."
        message = "Recopilando datos para análisis de comportamiento..."
        response_historic = ""

        while True:
            try:
                # "light" data used for UI updates (top 10 processes)
                processes_ui = obtain_processes_data()
                # data collection for AI analysis
                processes_ai = save_processes_data()
                # call sample saving method of ResourceHistoric to store the current top 10 processes for AI analysis
                resource_historic.save_sample(processes_ai[:10])
                
                # process historic of samples when ready (capacity reached)
                if resource_historic.is_ready():
                    # create sample set to send with AI prompt
                    samples = resource_historic.build_samples()
                
                    # build AI analysis
                    response = analyze_samples(context, samples, self.api_key)
                    context = response  # save context for next analysis to create a chain of insights based on behavior evolution
                    message = response
                    
                    # get timestamp for response historic and join
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    self.historic_ai.append(f"[{timestamp}] {response}")
                    
                    # append joinage to full historic (popup)
                    response_historic = "\n\n---\n\n".join(reversed(self.historic_ai))

                    # notification system (detect ALERTA keyword in AI response to trigger a desktop notification, this is a simple implementation that can be expanded with more complex rules based on the content of the message)
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

                # emit signal with the data for UI update, AI message and full historic for popup
                self.processes_data.emit(processes_ui, message, response_historic)
                
            except Exception as e:
                print(f"Error en WorkerProcesos: {e}")
            
            self.msleep(5000)

# Thread for big files scan
class WorkerScan(QThread):
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

# disk bar widget
class bar_disk(QWidget):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.setMinimumHeight(100)
        try:
            usage = psutil.disk_usage(self.path)
            self.total_gb = usage.total / (1024**3)
            self.used_gb = usage.used / (1024**3)
            self.percentage = usage.percent
        except:
            self.total_gb, self.used_gb, self.percentage = 0, 0, 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width, x_ini, y_ini, height_b = self.width() - 40, 20, 40, 25
        painter.setBrush(QColor("#333333"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x_ini, y_ini, width, height_b)
        painter.setBrush(QColor("#9b59b6")) 
        painter.drawRect(x_ini, y_ini, int((self.percentage/100)*width), height_b)
        painter.setPen(QColor("white"))
        painter.drawText(x_ini, 30, f"Almacenamiento: {self.path}")
        painter.setPen(QColor("#aaaaaa"))
        painter.drawText(x_ini, y_ini + height_b + 20, f"{self.used_gb:.1f}GB / {self.total_gb:.1f}GB ({self.percentage}%)")

# graph widget for CPU and RAM
class AnimatedGraph(QWidget):
    def __init__(self, tipo="CPU"):
        super().__init__()
        self.tipo = tipo
        self.points = [0.0 for _ in range(50)]
        self.r_min, self.r_max = 30, 70
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(1000)

    def actualizar(self):
        if self.tipo == "CPU":
            value = psutil.cpu_percent(interval=None)
        else:
            value = psutil.virtual_memory().percent
            
        self.points.append(value)
        if len(self.points) > 50: self.points.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        width, height = self.width(), self.height()
        paso_x = width / 49
        y_max, y_min = height - (self.r_max/100*height), height - (self.r_min/100*height)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, int(y_max), width, int(y_min - y_max))
        poly = QPolygonF()
        for i, v in enumerate(self.points):
            poly.append(QPointF(i * paso_x, height - (v / 100 * height)))
        color = QColor("#2ecc71") if self.points[-1] <= self.r_max else QColor("#e74c3c")
        painter.setPen(QPen(color, 3))
        painter.drawPolyline(poly)
        
# individual process bar widget
class BarraProcesoPro(QWidget):
    def __init__(self, name, value, r_min, r_max):
        super().__init__()
        self.nombre, self.value, self.r_min, self.r_max = name, value, r_min, r_max
        self.setMinimumHeight(50)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width = self.width() - 40
        bar_height = 15
        x_ini, y_ini = 10, 30
        in_range = self.value <= self.r_max
        color_line = QColor("#2ecc71") if in_range else QColor("#e74c3c")
        painter.setPen(QColor("white"))
        painter.drawText(x_ini, 20, f"{self.nombre}: {self.value}%")
        painter.setBrush(QColor("#333333"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x_ini, y_ini, width, bar_height)
        x_valor = x_ini + int((min(self.value, 100) / 100) * width)
        painter.setBrush(color_line)
        painter.drawRect(x_ini, y_ini, x_valor - x_ini, bar_height)

# resource screen
class ScreenResource(QWidget):
    def __init__(self, title, is_disk=False, path=""):
        super().__init__()
        self.title = title
        self.setStyleSheet("background-color: #0b0b0b;")
        layout_main = QVBoxLayout(self)
        
        content_h = QHBoxLayout()
        col_izq = QVBoxLayout()
        col_der = QVBoxLayout()
        
        if is_disk:
            col_izq.addWidget(bar_disk(path))
            self.panel_files = QFrame()
            self.panel_files.setStyleSheet("background: #1a1a1a; border: 1px solid #333; border-radius: 10px;")
            self.lay_arc = QVBoxLayout(self.panel_files)
            self.lbl_load = QLabel("Analizando archivos pesados...")
            self.lbl_load.setStyleSheet("color: #9b59b6;")
            self.lay_arc.addWidget(self.lbl_load)
            col_izq.addWidget(self.panel_files)

            panel_status = QFrame()
            panel_status.setStyleSheet("background: #1a1a1a; border: 1px solid #333; border-radius: 10px;")
            layout_status = QVBoxLayout(panel_status)
            usage = psutil.disk_usage(path).percent
            text_status = "ESTADO: ÓPTIMO" if usage < 80 else "ESTADO: CRÍTICO"
            color_status = "#2ecc71" if usage < 80 else "#e74c3c"
            message_status = "Tienes espacio suficiente." if usage < 80 else "Debes vaciar espacio pronto."
            
            layout_status.addWidget(QLabel(text_status, styleSheet=f"color: {color_status}; font-weight: bold; font-size: 16px;"))
            layout_status.addWidget(QLabel(message_status, styleSheet="color: white;"))
            layout_status.addStretch()
            col_der.addWidget(panel_status)

            self.worker_disk = WorkerScan(path)
            self.worker_disk.finished.connect(self.actualizar_archivos)
            self.worker_disk.start()
        else:            
            # title label
            lbl_tit = QLabel(f"Monitor: {title}")
            lbl_tit.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 5px;")
            lbl_tit.setMaximumHeight(35)
            col_izq.addWidget(lbl_tit)
            
            panel_kpi = QFrame()
            panel_kpi.setStyleSheet("background-color: #1a1a1a; border-radius: 12px; border: 1px solid #333;")
            panel_kpi.setMaximumHeight(80) 
            layout_kpi = QHBoxLayout(panel_kpi)
            layout_kpi.setContentsMargins(15, 5, 15, 5) 

            self.lbl_val_principal = QLabel("--")
            self.lbl_val_hardware = QLabel("--")
            self.lbl_val_uptime = QLabel("--")
            
            lbl_desc_text = "Carga Total" if title == "CPU" else "Uso de RAM"
            
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
                layout_kpi.addLayout(v_lay)
                
            col_izq.addWidget(panel_kpi)

            self.graph = AnimatedGraph(tipo=title)
            self.graph.setFixedHeight(180)
            col_izq.addWidget(self.graph)
            col_izq.addStretch()

            # right column
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
        layout_main.addLayout(content_h)

        # AI bottom panel
        self.panel_ai = QFrame()
        self.panel_ai.setStyleSheet("background-color: #121212; border: 1px solid #9b59b6; border-radius: 12px;")
        self.panel_ai.setFixedHeight(150)
        
        lay_ia = QVBoxLayout(self.panel_ai)
        
        self.label_ai = QTextEdit() 
        self.label_ai.setReadOnly(True)
        self.label_ai.setPlainText("Esperando análisis de comportamiento...")
        
        self.label_ai.setStyleSheet("""
            background: transparent; 
            border: none; 
            color: #9b59b6; 
            font-size: 14px; 
            font-style: italic;
        """)
        
        self.label_ai.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        lay_ia.addWidget(self.label_ai)
        layout_main.addWidget(self.panel_ai)

    def refresh_process_list(self, lista, message):
        if not hasattr(self, 'lay_procesos'): return
        
        uptime_seconds = int(datetime.datetime.now().timestamp() - psutil.boot_time())
        uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
        self.lbl_val_uptime.setText(uptime_str)

        if self.title == "CPU":
            val_principal = f"{psutil.cpu_percent(interval=None)}%"
            val_hardware = f"{psutil.cpu_count(logical=False)} núcleos / {psutil.cpu_count()} hilos"
        else:
            mem = psutil.virtual_memory()
            val_principal = f"{mem.percent}%"
            val_hardware = f"{mem.used/(1024**3):.1f} / {mem.total/(1024**3):.1f} GB"
        
        self.lbl_val_principal.setText(val_principal)
        self.lbl_val_hardware.setText(val_hardware)

        # update process list in UI
        while self.lay_procesos.count():
            item = self.lay_procesos.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for p in lista:
            self.lay_procesos.addWidget(BarraProcesoPro(p['name'][:15], p['cpu_percent'], 0, 20))
        self.lay_procesos.addStretch()
        
        # update AI message panel
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

# historic response popup
class WindowHistoric(QDialog):
    def __init__(self, texto_historial, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historial de Análisis")
        self.resize(600, 450)
        self.setStyleSheet("background-color: #0b0b0b; color: white;")
        
        layout = QVBoxLayout(self)
        
        self.texto = QTextEdit()
        self.texto.setReadOnly(True)
        self.texto.setPlainText(texto_historial)
        self.texto.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 1px solid #9b59b6;
                border-radius: 5px;
                color: #ccc;
                font-family: 'Courier New';
                font-size: 13px;
            }
        """)
        
        cursor = self.texto.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self.texto.setTextCursor(cursor)
        
        layout.addWidget(self.texto)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        btn_cerrar.setStyleSheet("background-color: #333; padding: 8px; color: white; border-radius: 5px;")
        layout.addWidget(btn_cerrar)
        
# main window 
class MainWindow(QMainWindow):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.alert_historic = ""
        self.worker_global = WorkerProcesses(self.api_key)
        self.worker_global.processes_data.connect(self.update_alert_historic)
        
        self.setWindowTitle("Hack-UDC AI Monitor")
        self.resize(1100, 650)

        layout_main = QHBoxLayout()
        layout_main.setSpacing(0)

        self.layout_sidebar = QVBoxLayout()
        self.button_inicio = QPushButton("Inicio")
        self.button_cpu = QPushButton("CPU")
        self.button_ram = QPushButton("Memoria")
        
        self.layout_sidebar.addWidget(self.button_inicio)
        self.layout_sidebar.addWidget(self.button_cpu)
        self.layout_sidebar.addWidget(self.button_ram)
        
        for part in psutil.disk_partitions(all=False):
            if part.fstype in ('squashfs', 'tmpfs', ''): 
                continue
            # MacOS system volumes ignore
            if "/System/Volumes" in part.mountpoint and not part.mountpoint.endswith("/Data"):
                continue
            button = QPushButton(f"Disco ({part.mountpoint})")
            button.clicked.connect(lambda ch, p=part.mountpoint: self.disk_window(p))
            self.layout_sidebar.addWidget(button)
            
        # 1. EL ESPACIADOR VA PRIMERO: Empuja las particiones hacia arriba
        self.layout_sidebar.addStretch()
        
        self.button_historic = QPushButton("Historial de Alertas")
        self.button_historic.setMinimumHeight(40)
        self.button_historic.setStyleSheet("""
            QPushButton {
                color: #9b59b6; 
                border: 2px solid #9b59b6;
                border-radius: 8px;
                background-color: #ffffff;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #9b59b6;
                color: white;
            }
        """)
        self.button_historic.clicked.connect(self.historic_popup)
        self.layout_sidebar.addWidget(self.button_historic)

        sidebar_container = QWidget()
        sidebar_container.setLayout(self.layout_sidebar)
        sidebar_container.setFixedWidth(200)
        sidebar_container.setStyleSheet("""
            QWidget { background-color: white; border-right: 1px solid #ced4da; } 
            QPushButton { border: none; text-align: left; padding: 12px; font-weight: bold; color: black; } 
            QPushButton:hover { background-color: #f1f3f5; }
        """)

        self.pages = QStackedWidget()
        self.p_inicio = self.create_inicio()
        self.p_cpu = ScreenResource("CPU")
        self.p_ram = ScreenResource("Memoria")

        self.worker_global.processes_data.connect(self.p_cpu.refresh_process_list)
        self.worker_global.processes_data.connect(self.p_ram.refresh_process_list)

        self.pages.addWidget(self.p_inicio)
        self.pages.addWidget(self.p_cpu)
        self.pages.addWidget(self.p_ram)

        self.button_inicio.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.button_cpu.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.button_ram.clicked.connect(lambda: self.pages.setCurrentIndex(2))

        layout_main.addWidget(sidebar_container)
        layout_main.addWidget(self.pages)
        
        container = QWidget()
        container.setLayout(layout_main)
        self.setCentralWidget(container)
        self.worker_global.start()

    def create_inicio(self):
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

    def disk_window(self, ruta):
        nueva = ScreenResource(f"Disco {ruta}", is_disk=True, path=ruta)
        self.pages.addWidget(nueva)
        self.pages.setCurrentWidget(nueva)
        
    def update_alert_historic(self, lista, message, alert_historic):
        """Guarda el mensaje recibido en la variable local para el pop-up."""
        self.alert_historic = alert_historic
        # También actualiza las pantallas activas (CPU/RAM) como antes
        self.p_cpu.refresh_process_list(lista, message)
        self.p_ram.refresh_process_list(lista, message)

    def historic_popup(self):
        """Crea y muestra la ventana emergente con el contenido actual."""
        if not self.alert_historic:
            contenido = "No hay registros en el historial todavía."
        else:
            contenido = self.alert_historic
            
        popup = WindowHistoric(contenido, self)
        popup.exec() # .exec() hace que sea modal (bloquea la principal hasta cerrar)

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
