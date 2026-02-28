import sys
import psutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen

# 1. IMPORTAR TU BASE DE DATOS
import database 

# --- REUTILIZAMOS TU BARRA PERSONALIZADA ---
class BarraProcesoPro(QWidget):
    def __init__(self, nombre, valor_actual, r_min, r_max):
        super().__init__()
        self.nombre = nombre
        self.valor = valor_actual
        self.r_min = r_min
        self.r_max = r_max
        self.setMinimumHeight(65) 

    # Método nuevo para actualizar sin recrear el widget
    def actualizar_valores(self, valor, r_min, r_max):
        self.valor = valor
        self.r_min = r_min
        self.r_max = r_max
        self.update() # Fuerza el repintado (llama a paintEvent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        ancho = self.width() - 40
        alto_barra = 20
        x_ini = 10
        y_ini = 35 
        
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

# --- NUEVA CLASE PARA LA PANTALLA DE RECURSOS ---
class PantallaRecurso(QWidget):
    def __init__(self, titulo):
        super().__init__()
        self.titulo = titulo
        self.setStyleSheet("background-color: #0b0b0b;") 
        
        layout_principal = QVBoxLayout()

        self.lbl_score = QLabel("Health Score: Calculando...")
        self.lbl_score.setStyleSheet("font-size: 28px; font-weight: bold; color: #2ecc71; padding: 10px;")
        layout_principal.addWidget(self.lbl_score)

        layout_h = QHBoxLayout()
        
        col_izq = QVBoxLayout()
        self.lbl_tit = QLabel(f"Análisis en tiempo real: {titulo}")
        self.lbl_tit.setStyleSheet("font-size: 18px; color: white;")
        col_izq.addWidget(self.lbl_tit)
        
        grafica = QFrame()
        grafica.setStyleSheet("background: #1a1a1a; border: 1px solid #333; border-radius: 5px;")
        grafica.setMinimumHeight(300)
        col_izq.addWidget(grafica)
        
        alertas_widget = QWidget()
        alertas_widget.setFixedWidth(280)
        
        # Guardamos la referencia al layout de alertas para modificarlo después
        self.col_der = QVBoxLayout(alertas_widget)
        
        lbl_alertas = QLabel("Alertas de procesos")
        lbl_alertas.setStyleSheet("color: white; font-weight: bold; font-size: 18px;")
        self.col_der.addWidget(lbl_alertas)
        
        # Stretch al final para empujar widgets hacia arriba
        self.stretch_spacer = self.col_der.addStretch()
        
        layout_h.addLayout(col_izq, stretch=2)
        layout_h.addWidget(alertas_widget)
        
        layout_principal.addLayout(layout_h)
        self.setLayout(layout_principal)

    # Método nuevo para inyectar datos de database.py
    def actualizar_alertas(self, datos_procesos, health_score):
        self.lbl_score.setText(f"Health Score: {health_score}%")
        
        # 1. Eliminar barras antiguas (manteniendo el label de título)
        for i in reversed(range(1, self.col_der.count() - 1)):
            widget = self.col_der.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                
        # 2. Insertar barras nuevas con los datos de la base de datos
        for proc in datos_procesos:
            nueva_barra = BarraProcesoPro(
                proc["nombre"], 
                proc["valor"], 
                proc["min"], 
                proc["max"]
            )
            # Insertar antes del stretch
            self.col_der.insertWidget(self.col_der.count() - 1, nueva_barra)

# --- VENTANA PRINCIPAL ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hack-UDC AI Monitor")
        self.resize(1100, 600)

        # Inicialización de conexión a BD (Hipotético)
        # self.db = database.Conexion()

        main_layout = QHBoxLayout()
        
        self.sidebar = QVBoxLayout()
        self.btn_inicio = QPushButton("🏠 Inicio")
        self.btn_cpu = QPushButton("📊 CPU")
        self.btn_ram = QPushButton("🧠 Memoria")
        
        self.sidebar.addWidget(self.btn_inicio)
        self.sidebar.addWidget(self.btn_cpu)
        self.sidebar.addWidget(self.btn_ram)
        
        for part in psutil.disk_partitions(all=False):
            if part.device.startswith('/dev/loop') or part.fstype in ('squashfs', 'tmpfs', 'devtmpfs', ''):
                continue
            
            btn = QPushButton(f"Disco ({part.mountpoint})")
            btn.clicked.connect(lambda ch, p=part.device: self.cambiar_pestaña_disco(p))
            self.sidebar.addWidget(btn)
        
        self.sidebar.addStretch()
        
        self.paginas = QStackedWidget()
        
        self.p_inicio = QWidget()
        self.p_inicio.setStyleSheet("background-color: black;")
        
        layout_ini = QVBoxLayout()
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
            "</ul>"
            "</div>"
        )
        texto_ini.setWordWrap(True)
        layout_ini.addWidget(texto_ini)
        layout_ini.addStretch()
        self.p_inicio.setLayout(layout_ini)
        
        # Referencias a las páginas para poder actualizarlas luego
        self.pantalla_cpu = PantallaRecurso("CPU")
        self.pantalla_ram = PantallaRecurso("Memoria")

        self.paginas.addWidget(self.p_inicio)
        self.paginas.addWidget(self.pantalla_cpu)
        self.paginas.addWidget(self.pantalla_ram)

        self.btn_inicio.clicked.connect(lambda: self.paginas.setCurrentIndex(0))
        self.btn_cpu.clicked.connect(lambda: self.paginas.setCurrentIndex(1))
        self.btn_ram.clicked.connect(lambda: self.paginas.setCurrentIndex(2))

        main_layout.setSpacing(0) 

        sidebar_container = QWidget()
        sidebar_container.setLayout(self.sidebar)
        sidebar_container.setStyleSheet("""
            QWidget { background-color: white; border-right: 2px solid #ced4da; }
            QPushButton { border: none; background-color: transparent; color: black; text-align: left; padding: 10px; font-size: 15px; font-weight: bold; }
            QPushButton:hover { background-color: #f1f3f5; }
        """)

        container = QWidget()
        main_layout.addWidget(sidebar_container, 1)
        main_layout.addWidget(self.paginas, 4)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # --- QTIMER PARA ACTUALIZACIÓN EN TIEMPO REAL ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.consultar_base_datos)
        self.timer.start(2000) # Se ejecuta cada 2000 ms (2 segundos)

    def consultar_base_datos(self):
        # Aquí llamas a tu database.py. Ejemplo de datos simulados:
        
        # datos_cpu = database.obtener_datos_recurso("CPU")
        datos_cpu = [
            {"nombre": "Firefox", "valor": 85, "min": 10, "max": 40},
            {"nombre": "Docker", "valor": 15, "min": 5, "max": 25}
        ]
        score_cpu = 88

        # datos_ram = database.obtener_datos_recurso("RAM")
        datos_ram = [
            {"nombre": "VSCode", "valor": 45, "min": 20, "max": 50},
            {"nombre": "System", "valor": 30, "min": 10, "max": 35}
        ]
        score_ram = 95
        
        # Actualizamos la UI pasando los datos
        self.pantalla_cpu.actualizar_alertas(datos_cpu, score_cpu)
        self.pantalla_ram.actualizar_alertas(datos_ram, score_ram)

    def cambiar_pestaña_disco(self, nombre):
        nueva_p_disco = PantallaRecurso(f"Disco {nombre}")
        self.paginas.addWidget(nueva_p_disco)
        self.paginas.setCurrentWidget(nueva_p_disco)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QPushButton { text-align: left; padding: 10px; font-size: 14px; border: none; }"
                      "QPushButton:hover { background-color: #dcdde1; }")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())