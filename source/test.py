import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

def on_button_clicked(widget):
    print("Acción ejecutada")

def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)
    button = Gtk.Button(label="Hello, World!")
    button.connect('clicked', lambda x: win.close())
    button.connect('clicked', on_button_clicked)
    win.set_child(button)
    win.present()

app = Gtk.Application(application_id='org.hackudc.NOMBRE_DEL_PROYECTO')
app.connect('activate', on_activate)
app.run(None)