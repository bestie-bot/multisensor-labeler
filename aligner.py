# import the necessary packages
from __future__ import print_function
from utils.multiSensorFrameAligner import MultiSensorFrameAligner
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class Application(Gtk.Application):
    def __init__(self):
        super().__init__()

    def do_activate(self):
        win = MultiSensorFrameAligner(self)
        win.show()

app = Application()
app.run()
