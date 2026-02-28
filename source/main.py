import interfaz
import resources
import prompt
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    
    import sys
    
    app = QApplication(sys.argv)
    w = interfaz.MainWindow()
    w.show()
    sys.exit(app.exec())