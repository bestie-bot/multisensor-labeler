
# import the necessary packages
from __future__ import print_function
from utils.multiSensorMarkingApp import MultiSensorMarkingApp
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# start the app
win = MultiSensorMarkingApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()