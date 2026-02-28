Sistema Inteligente de Monitoreo de Recursos con Análisis de Comportamiento Mediante IA


INTRODUCCIÓN

El proyecto consiste en una aplicación de escritorio diseñada para la supervisión en tiempo real de los recursos de hardware (CPU, RAM y Almacenamiento). A diferencia de los monitores de sistema convencionales, esta herramienta integra un motor de Inteligencia Artificial (Llama-3.3-70b) para interpretar datos técnicos y ofrecer diagnósticos en lenguaje natural, facilitando la comprensión para usuarios no expertos.


FUNCIONALIDADES IMPLEMENTADAS

El diagnóstico basado en comportamiento, el sistema no juzga procesos de forma aislada. Almacena 5 "samples" antes de realizar una consulta a la IA, lo que permite un análisis basado en la tendencia y no solo en un evento puntual.También se encarga de la gestión de almacenamiento, incluye un trabajador específico (WorkerEscaneo) que analiza las unidades de disco de forma recursiva para identificar los 10 archivos de mayor tamaño, ayudando al usuario a liberar espacio de manera eficiente. Además incluye un sistema de notificaciones inteligentes, cuando el análisis de la IA concluye en un estado crítico, el sistema dispara una notificación de escritorio automática para alertar al usuario incluso si la aplicación está en segundo plano.


ARQUITECTURA DE SOFTWARE

La aplicación sigue un diseño modular dividido en cuatro componentes críticos: la gestión de Interfaz (GUI) desarrollada con PyQt6, con multithreading que utiliza hilos secundarios (QThread) para la recolección de datos y el análisis de IA, evitando el bloqueo de la interfaz de usuario (UI) durante operaciones pesadas, también contene visualización dinámica incluye gráficas animadas que se actualizan cada 500ms para mostrar la fluctuación de carga de CPU y Memoria; Recolección de Métricas (resources.py) utilizando la librería psutil para la recopilación de métricas del sistema operativo; Análisis de Procesos filtrando y ordenando los 10 procesos con mayor consumo de recursos; por ultimo un historial de alertas, el cual recoge las últimas 10 alertas.


CONCLUSIÓN

Este trabajo representa una solución integral que combina la potencia del monitoreo de bajo nivel en Python con las capacidades interpretativas de los modelos de lenguaje de gran escala (LLMs). La arquitectura garantiza fluidez mediante el uso de hilos concurrentes y proporciona una experiencia de usuario simplificada para una tarea tradicionalmente técnica.
