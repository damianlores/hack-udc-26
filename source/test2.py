import sys
import psutil
import sqlite3
import database
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton, QTextEdit)
from PyQt6.QtCore import QTimer

# Asumiendo que inicializar_base_datos() y registrar_metricas() 
# están definidas en este mismo archivo o importadas.

class SystemMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor de Sistema e IA")
        self.setGeometry(100, 100, 800, 600)

        # 1. Inicializar conexión SQLite persistente en el hilo principal
        self.db_conn = database.init_database()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["PID", "Nombre", "CPU (%)", "Memoria (MB)"])
        layout.addWidget(self.table)

        self.btn_analyze = QPushButton("Analizar Rendimiento con IA")
        self.btn_analyze.clicked.connect(self.trigger_ai_analysis)
        layout.addWidget(self.btn_analyze)

        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        layout.addWidget(self.ai_output)

        # 2. Reutilizar el QTimer para GUI y Base de Datos
        self.timer = QTimer()
        self.timer.timeout.connect(self.rutina_monitoreo)
        self.timer.start(2000) # Pulso cada 2 segundos

    def rutina_monitoreo(self):
        """Ejecuta la actualización visual y el registro en disco secuencialmente."""
        # A. Actualizar la interfaz (Tabla)
        self.actualizar_tabla()
        
        # B. Escribir en la base de datos
        database.metric_register(self.db_conn)

    def actualizar_tabla(self):
        self.table.setRowCount(0)
        processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']), 
                           key=lambda p: p.info['cpu_percent'], reverse=True)[:15]

        for row_idx, proc in enumerate(processes):
            self.table.insertRow(row_idx)
            info = proc.info
            mem_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0

            self.table.setItem(row_idx, 0, QTableWidgetItem(str(info['pid'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(info['name']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{info['cpu_percent']:.1f}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{mem_mb:.1f}"))

    def trigger_ai_analysis(self):
        # Punto de entrada para la API Groq
        pass

    def closeEvent(self, event):
        """Previene que la base de datos quede bloqueada (Locked) al cerrar la ventana."""
        if hasattr(self, 'db_conn'):
            self.db_conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMonitorApp()
    window.show()
    sys.exit(app.exec())