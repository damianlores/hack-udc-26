# Sistema Inteligente de Monitoreo de Recursos con Análisis de Comportamiento Mediante IA
## INTRODUCCIÓN

Este proyecto presenta una solución avanzada de escritorio para la supervisión en tiempo real de recursos críticos (CPU, RAM y Almacenamiento). A diferencia de las herramientas tradicionales que solo muestran cifras frías, este sistema integra el modelo de lenguaje Llama-3.3-70b. Su objetivo es traducir datos técnicos complejos en diagnósticos en lenguaje natural, democratizando el acceso a la gestión de sistemas para usuarios no expertos.

## FUNCIONALIDADES IMPLEMENTADAS

El sistema implementa un diagnóstico basado en el comportamiento temporal, evitando juicios precipitados sobre procesos aislados; para ello, almacena un historial de cinco muestras (samples) antes de consultar a la IA, lo que garantiza un análisis fundamentado en tendencias reales y no en picos de consumo puntuales. Complementariamente, la herramienta optimiza la gestión de almacenamiento mediante un hilo especializado (WorkerEscaneo) que rastrea de forma recursiva las unidades de disco para localizar los diez archivos de mayor tamaño, facilitando así una liberación de espacio inteligente y dirigida. Finalmente, el software integra un sistema de notificaciones proactivas: si el motor de IA identifica un estado crítico en el rendimiento, se dispara automáticamente una alerta de escritorio que mantiene al usuario informado en tiempo real, incluso cuando la aplicación opera en segundo plano

## ARQUITECTURA DE SOFTWARE

La aplicación sigue un diseño modular dividido en cuatro componentes críticos que garantizan su eficiencia. En primer lugar, la Gestión de Interfaz (GUI), desarrollada con PyQt6, ofrece una visualización dinámica mediante gráficas animadas que se actualizan cada 500ms para mostrar la fluctuación de carga de CPU y Memoria. Para evitar el bloqueo de esta interfaz durante operaciones pesadas, se implementó un sistema de Multithreading (QThread) que delega la recolección de datos y el análisis de la IA a hilos secundarios. En el núcleo técnico, la Recolección de Métricas se realiza a través del módulo resources.py utilizando la librería psutil para la extracción de datos de bajo nivel del sistema operativo. Por último, el sistema incluye un motor de Análisis de Procesos que filtra y ordena los diez procesos con mayor consumo, manteniendo un historial de las últimas diez alertas generadas para su revisión posterior.

## CONCLUSIÓN

Este trabajo demuestra la viabilidad de integrar modelos de lenguaje masivos (LLMs) en herramientas de sistema locales, logrando un equilibrio entre precisión técnica y accesibilidad. El uso de una arquitectura multihilo ha resultado fundamental, permitiendo que el procesamiento intensivo de la IA y el escaneo recursivo de archivos coexistan con una interfaz fluida y de baja latencia. En definitiva, el proyecto no solo optimiza el monitoreo de recursos, sino que establece un precedente sobre cómo la IA generativa puede actuar como una capa de interpretación crítica, transformando datos brutos en información estratégica y preventiva para el mantenimiento del hardware.
