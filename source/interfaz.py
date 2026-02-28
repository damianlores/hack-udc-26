import sys
import psutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen

# --- REUTILIZAMOS TU BARRA PERSONALIZADA ---
class BarraProcesoPro(QWidget):
    def __init__(self, nombre, valor_actual, r_min, r_max):
        super().__init__()
        self.nombre, self.valor, self.r_min, self.r_max = nombre, valor_actual, r_min, r_max
        self.setMinimumHeight(50)

    def paintEvent(self, event):
        painter = QPainter(self)
        ancho, alto = self.width() - 40, 20
        x_ini, y_ini = 10, 25
        painter.setBrush(QColor("white"))
        painter.drawRect(x_ini, y_ini, ancho, alto)
        x_azul = x_ini + int((self.r_min / 100) * ancho)
        ancho_azul = int(((self.r_max - self.r_min) / 100) * ancho)
        painter.setBrush(QColor(52, 152, 219, 100))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x_azul, y_ini + 1, ancho_azul, alto - 1)
        esta_dentro = self.r_min <= self.valor <= self.r_max
        color_linea = QColor("#2ecc71") if esta_dentro else QColor("#e74c3c")
        emoji = "✅" if esta_dentro else "⚠️"
        x_valor = x_ini + int((self.valor / 100) * ancho)
        painter.setPen(QPen(color_linea, 4))
        painter.drawLine(x_valor, y_ini - 2, x_valor, y_ini + alto + 2)
        painter.setPen(QColor("black"))
        painter.drawText(x_ini, 15, f"{emoji} {self.nombre}: {self.valor}%")

# --- NUEVA CLASE PARA LA PANTALLA DE RECURSOS ---
class PantallaRecurso(QWidget):
    def __init__(self, titulo):
        super().__init__()
        layout = QHBoxLayout()
        col_izq = QVBoxLayout()
        
        # Título y placeholder de gráfica
        self.lbl = QLabel(f"Análisis en tiempo real: {titulo}")
        self.lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        col_izq.addWidget(self.lbl)
        
        grafica = QFrame()
        grafica.setStyleSheet("background: white; border: 1px solid #ccc; border-radius: 5px;")
        grafica.setMinimumHeight(300)
        col_izq.addWidget(grafica)
        
        # Alertas a la derecha (según tu dibujo)
        col_der = QVBoxLayout()
        col_der.addWidget(QLabel("Alertas de procesos"))
        col_der.addWidget(BarraProcesoPro("Firefox", 85, 10, 40))
        col_der.addWidget(BarraProcesoPro("System", 20, 5, 30))
        col_der.addStretch()
        
        layout.addLayout(col_izq, stretch=2)
        layout.addLayout(col_der, stretch=1)
        self.setLayout(layout)

# --- VENTANA PRINCIPAL ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hack-UDC AI Monitor")
        self.resize(1100, 600)

        main_layout = QHBoxLayout()
        
        # 1. BARRA LATERAL
        self.sidebar = QVBoxLayout()
        self.btn_inicio = QPushButton("🏠 Inicio")
        self.btn_cpu = QPushButton("📊 CPU")
        self.btn_ram = QPushButton("🧠 Memoria")
        
        self.sidebar.addWidget(self.btn_inicio)
        self.sidebar.addWidget(self.btn_cpu)
        self.sidebar.addWidget(self.btn_ram)
        
        # Detectar Discos automáticamente
        for part in psutil.disk_partitions():
            if 'fixed' in part.opts or part.fstype:
                btn = QPushButton(f"💾 Disco ({part.device})")
                btn.clicked.connect(lambda ch, p=part.device: self.cambiar_pestaña_disco(p))
                self.sidebar.addWidget(btn)
        
        self.sidebar.addStretch()
        
        # 2. CONTENEDOR DE PÁGINAS (Stacked Widget)
        self.paginas = QStackedWidget()
        
        # --- MODIFICACIÓN 2: INICIO MODO OSCURO ---
        self.p_inicio = QWidget()
        self.p_inicio.setStyleSheet("background-color: black;") # Fondo negro para toda la página
        
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
        layout_ini.addStretch() # Esto empuja el texto hacia arriba para que no quede centrado en medio de la nada
        self.p_inicio.setLayout(layout_ini)
        # Añadir páginas
        self.paginas.addWidget(self.p_inicio)
        self.paginas.addWidget(PantallaRecurso("CPU"))
        self.paginas.addWidget(PantallaRecurso("Memoria"))

        # Conectar botones
        self.btn_inicio.clicked.connect(lambda: self.paginas.setCurrentIndex(0))
        self.btn_cpu.clicked.connect(lambda: self.paginas.setCurrentIndex(1))
        self.btn_ram.clicked.connect(lambda: self.paginas.setCurrentIndex(2))

# --- MODIFICACIÓN 1: BARRA LATERAL ---
        main_layout.setSpacing(0) 

        sidebar_container = QWidget()
        sidebar_container.setLayout(self.sidebar)
        sidebar_container.setStyleSheet("""
            QWidget {
                background-color: white; /* Fondo totalmente blanco */
                border-right: 2px solid #ced4da; /* Línea divisoria gris */
            }
            QPushButton {
                border: none;
                background-color: transparent;
                color: black; /* Letra negra para que contraste bien */
                text-align: left;
                padding: 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f1f3f5; /* Gris muy clarito al pasar el ratón */
            }
        """)

        # Layout final
        container = QWidget()
        main_layout.addWidget(sidebar_container, 1)
        main_layout.addWidget(self.paginas, 4)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def cambiar_pestaña_disco(self, nombre):
        # Aquí crearíamos una nueva página para cada disco
        nueva_p_disco = PantallaRecurso(f"Disco {nombre}")
        self.paginas.addWidget(nueva_p_disco)
        self.paginas.setCurrentWidget(nueva_p_disco)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Estilo básico para botones
    app.setStyleSheet("QPushButton { text-align: left; padding: 10px; font-size: 14px; border: none; }"
                      "QPushButton:hover { background-color: #dcdde1; }")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())