
# import the necessary packages
from __future__ import print_function
from utils.multiSensorMarkingApp import MultiSensorMarkingApp
gi.require_version('Gtk', '4.0')
import gi
from gi.repository import Gtk

# start the app
win = MultiSensorMarkingApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()