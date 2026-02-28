import gi
gi.require_version("Gtk", "4.0") # Usamos 3.0 por ser la más estable en Python
from gi.repository import Gtk, Pango

class MonitorSistemaIA(Gtk.Window):
    def __init__(self):
        super().__init__(title="AI System Health Monitor")
        self.set_default_size(1000, 600)

        # 1. Contenedor principal Horizontal (Divide Menú de Contenido)
        # Esto crea la línea divisoria física que pedías
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(self.main_box)

        # 2. BARRA LATERAL (Índice)
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.sidebar.set_size_request(200, -1)
        self.sidebar.get_style_context().add_class("sidebar") # Para CSS luego
        self.main_box.pack_start(self.sidebar, False, False, 0)

        # Añadimos un separador vertical (Línea divisoria visual)
        separador = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.pack_start(separador, False, False, 0)

        # 3. PANEL DE PÁGINAS (Stack)
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.main_box.pack_start(self.stack, True, True, 0)

        # Conectar el índice con las páginas
        sidebar_menu = Gtk.StackSidebar()
        sidebar_menu.set_stack(self.stack)
        self.sidebar.pack_start(sidebar_menu, True, True, 0)

        # --- CREACIÓN DE PÁGINAS ---
        self.crear_pagina_inicio()
        self.crear_pagina_recurso("CPU")
        self.crear_pagina_recurso("Memoria")

        self.show_all()

    def crear_pagina_inicio(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(30)
        box.set_margin_start(30)

        # Texto de Inicio Grande (Título)
        titulo = Gtk.Label()
        titulo.set_markup("<span size='xx-large' weight='bold' foreground='#1a237e'>Monitor de Salud Inteligente</span>")
        titulo.set_xalign(0)
        box.pack_start(titulo, False, False, 0)

        # Descripción basada en el Roadmap
        desc = Gtk.Label()
        desc.set_markup(
            "Este sistema recolecta métricas de <b>/proc</b> y utiliza IA para detectar anomalías.\n\n"
            "<b>Instrucciones:</b>\n"
            "1. Selecciona un recurso en la izquierda.\n"
            "2. Observa la gráfica de consumo en tiempo real.\n"
            "3. Revisa las alertas si el consumo sale del rango normal."
        )
        desc.set_line_wrap(True)
        desc.set_xalign(0)
        box.pack_start(desc, False, False, 0)

        self.stack.add_titled(box, "inicio", "🏠 Inicio")

    def crear_pagina_recurso(self, nombre):
        # Aquí iría tu diseño de: [Gráfica | Alertas]
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # Lado izquierdo: Espacio para Gráfica
        area_grafica = Gtk.Frame(label=f"Gráfica de {nombre}")
        area_grafica.set_shadow_type(Gtk.ShadowType.IN)
        box.pack_start(area_grafica, True, True, 10)

        # Lado derecho: Alertas (tus barras del dibujo)
        alertas_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        alertas_box.pack_start(Gtk.Label(label="Alertas detectadas"), False, False, 5)
        # Aquí añadiríamos las barras personalizadas más adelante
        box.pack_start(alertas_box, False, False, 10)

        self.stack.add_titled(box, nombre.lower(), f"📊 {nombre}")

if __name__ == "__main__":
    win = MonitorSistemaIA()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()