import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1") # Recomendado para apps modernas en GTK4
from gi.repository import Gtk, Adw, Gio

class MonitorGTK4(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("AI System Health Monitor")
        self.set_default_size(1000, 600)

        # 1. Contenedor principal dividido (Gtk.Paned)
        # Esto crea la línea divisoria física que pedías
        self.split_view = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.set_content(self.split_view)

        # 2. LADO IZQUIERDO: Barra Lateral (Índice)
        self.sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.sidebar_box.set_size_request(220, -1)
        self.split_view.set_start_child(self.sidebar_box)

        # 3. LADO DERECHO: El Stack de páginas
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.split_view.set_end_child(self.stack)

        # Conector: StackSidebar (Crea el menú automáticamente)
        sidebar_menu = Gtk.StackSidebar()
        sidebar_menu.set_stack(self.stack)
        self.sidebar_box.append(sidebar_menu)

        # --- PÁGINAS ---
        self.crear_pagina_inicio()
        self.crear_pagina_recurso("CPU")
        self.crear_pagina_recurso("Memoria")
        
        # Opcional: Mostrar discos dinámicamente como en el plan previo
        # self.crear_pagina_recurso("Disco C:")

    def crear_pagina_inicio(self):
        # Página basada en tu descripción de "Inicio"
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_margin_top(40)
        vbox.set_margin_start(40)
        vbox.set_margin_end(40)

        # Título Grande con estilo GTK4
        titulo = Gtk.Label(label="Monitor de Salud Inteligente")
        titulo.add_css_class("title-1") # Estilo de texto muy grande
        titulo.set_halign(Gtk.Align.START)
        vbox.append(titulo)

        # Explicación del Roadmap
        desc_text = (
            "Esta herramienta analiza el sistema usando datos de <b>/proc</b>.\n\n"
            "• <b>IA:</b> Utiliza modelos como <i>Isolation Forest</i> para aprender qué es normal.\n"
            "• <b>Detección:</b> Si una aplicación como Firefox consume fuera de rango, verás una alerta.\n"
            "• <b>Interfaz:</b> Navega por las pestañas laterales para ver métricas específicas."
        )
        
        desc = Gtk.Label()
        desc.set_markup(desc_text)
        desc.set_wrap(True)
        desc.set_halign(Gtk.Align.START)
        vbox.append(desc)

        self.stack.add_titled(vbox, "inicio", "🏠 Inicio")

    def crear_pagina_recurso(self, nombre):
        # Estructura del boceto: [ Gráfica (izq) | Alertas (der) ]
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        hbox.set_margin_end(20)

        # Columna Izquierda: Espacio para el gráfico de líneas del boceto
        grafica_frame = Gtk.Frame()
        grafica_frame.set_hexpand(True)
        grafica_label = Gtk.Label(label=f"Aquí se renderizará el gráfico de {nombre}")
        grafica_frame.set_child(grafica_label)
        hbox.append(grafica_frame)

        # Columna Derecha: Alertas de procesos
        alertas_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        alertas_vbox.set_size_request(250, -1)
        
        lbl_alertas = Gtk.Label(label="Alertas y Procesos")
        lbl_alertas.add_css_class("heading")
        alertas_vbox.append(lbl_alertas)

        # Aquí irían los widgets de barras personalizadas (ej. Firefox, WhatsApp)
        hbox.append(alertas_vbox)

        self.stack.add_titled(hbox, nombre.lower(), f"📊 {nombre}")

class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.hackudc.monitor",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = MonitorGTK4(application=self)
        win.present()

if __name__ == "__main__":
    app = Application()
    app.run(None)