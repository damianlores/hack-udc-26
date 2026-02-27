# hack-udc-26

1. Captura de Datos (El Backend de Telemetría)

En Linux, la fuente de la verdad es el sistema de archivos /proc. Necesitas un "daemon" (servicio en segundo plano) que recolecte métricas periódicamente.

    Lenguaje recomendado: Python (por su ecosistema de IA) o Go/Rust (si buscas máxima eficiencia).

    Herramientas clave:

        psutil: Biblioteca estándar para obtener uso de CPU, RAM, disco y procesos activos.

        GPUtil: Para métricas de tarjetas NVIDIA.

    Qué recolectar: Porcentaje de carga por núcleo, temperatura, frecuencia del reloj, memoria swap y, crucialmente, la lista de aplicaciones abiertas (PID y nombre).

2. Almacenamiento e Historial (La Base de Datos)

Para que la IA haga sugerencias basadas en el pasado, necesitas guardar los datos sin saturar el disco.

    Estrategia: Usa una Base de Datos de Series Temporales (TSDB) como InfluxDB o una ligera como SQLite.

    Estructura:

        Timestamp | App_Name | CPU_Usage | RAM_Usage | Context (ej. "enchufado", "batería").

3. El Cerebro: Motor de Análisis con IA

Aquí es donde determinas si un comportamiento es "normal". No uses reglas fijas (ej. "si CPU > 80%"); usa Detección de Anomalías.

    Entrenamiento: Usa algoritmos de aprendizaje no supervisado como Isolation Forest o LSTM (Long Short-Term Memory) si quieres predecir tendencias futuras.

    Lógica de "Normalidad":

        La IA compara el consumo actual de firefox con su media histórica.

        Si firefox consume el 90% de la CPU pero solo tienes una pestaña de texto abierta, la IA marca una anomalía.

    Sugerencias: Basándote en el historial, la IA puede detectar que todos los martes a las 10:00 el sistema se ralentiza por un cron job y sugerir reprogramarlo.

4. La Interfaz Gráfica (Visualización)

Para interpretar los datos con gráficas en Linux de forma moderna:

    Framework: PyQt6 o Tkinter (Python), o si prefieres algo web-desktop, Electron o Tauri.

    Librerías de Gráficas: Plotly o Chart.js. Son excelentes para mostrar líneas de tiempo dinámicas donde el usuario puede ver los picos de consumo.

    Dashboard: Debe mostrar el "Score de Salud" del sistema y una lista de "Insights" (ej. "Slack está consumiendo un 20% más de lo habitual, ¿desea reiniciarlo?").

5. Implementación Paso a Paso (Roadmap)
Paso	Acción Técnica
1	Crea un script en Python que use psutil para imprimir en consola el uso de CPU cada 5 segundos.
2	Implementa una base de datos SQLite para guardar esos datos junto con el nombre del proceso más pesado.
3	Integra un modelo de Scikit-Learn (IsolationForest) que se entrene con los primeros 30 minutos de datos para definir qué es "normal".
4	Diseña una ventana básica en PyQt que lea la base de datos y muestre un gráfico de líneas.
5	Añade un sistema de notificaciones (libnotify en Linux) para las alertas de la IA.
6. Consideraciones de Linux

    Permisos: Algunos datos de hardware requieren privilegios de root.

    Desktop Environment: Asegúrate de que tu interfaz sea compatible con Wayland y X11.

    Empaquetado: Usa Flatpak o AppImage para que tu aplicación funcione en Ubuntu, Fedora y Arch sin problemas de dependencias.
