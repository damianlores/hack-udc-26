import interfaz
import resources
import prompt

if __name__ == "__main__":
    
    interfaz.init_ui()

#Señales: En tu MainWindow, cuando conectes el worker: self.worker_global.datos_actualizados.connect(self.tu_funcion), asegúrate de que tu_funcion reciba dos parámetros: (self, lista, texto).
