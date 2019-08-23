# import the necessary packages
from __future__ import print_function
import gi
from PIL import Image
from gi.repository import Gtk, GdkPixbuf
import xml.etree.ElementTree as ET
from filecmp import dircmp
import numpy as np
import datetime
import cv2
from natsort import natsorted, ns
import os
import sys
gi.require_version('Gtk', '3.0')


class MultiSensorFrameAligner(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(
            self, title="Multi-Sensor Image Alignment for 2 Sensors")
        self.set_border_width(16)

        self.sensorOnePath = ''
        self.sensorOneImages = []
        self.sensorTwoPath = ''
        self.sensorTwoImages = []
        self.sensorOneSaveFolderPath = ''
        self.sensorTwoSaveFolderPath = ''
        self.imageArray1 = []
        self.imageArray2 = []
        self.currentIndex = 0
        self.count = 0
        self.filter = 'rgb'
        self.range_filter = self.filter.upper()
        self.opacity = 50
        self.x_offset = 0
        self.y_offset = 0
        self.rotateLR = 0
        self.rotateUD = 0

        grid = Gtk.Grid()
        self.add(grid)

        button1 = Gtk.Button("Choose Sensor 1 Images Folder")
        button1.connect("clicked", self.on_folder_clicked, 1)
        grid.attach(button1, 0, 1, 1, 1)

        button2 = Gtk.Button("Choose Sensor 2 Images Folder")
        button2.connect("clicked", self.on_folder_clicked, 2)
        grid.attach(button2, 1, 1, 1, 1)

        button3 = Gtk.Button("Sync Folders")
        button3.connect("clicked", self.on_sync_folders)
        grid.attach(button3, 0, 2, 1, 1)

        button5 = Gtk.Button("Choose Sensor 2 Save Folder")
        button5.connect("clicked", self.on_save_folder, 2)
        grid.attach(button5, 2, 1, 1, 1)

        button6 = Gtk.Button("Load next image")
        button6.connect("clicked", self.load_next_image)
        grid.attach(button6, 1, 2, 1, 1)  # grid location

        button7 = Gtk.Button("Load previous image")
        button7.connect("clicked", self.load_prev_image)
        grid.attach(button7, 2, 2, 1, 1)  # grid location

        button11 = Gtk.Button("Save Adjusted Image")
        button11.connect("clicked", self.calc_manual_rectangles)
        grid.attach(button11, 1, 8, 1, 1)  # grid location

        self.image1 = Gtk.Image()
        grid.attach(self.image1, 0, 3, 1, 1)

        self.fileLabel1 = Gtk.Label()
        self.fileLabel1.set_text("")
        self.fileLabel1.set_justify(Gtk.Justification.LEFT)
        grid.attach(self.fileLabel1, 0, 4, 1, 1)

        offset_labels = Gtk.Label()
        offset_labels.set_label("Image Offsets")
        grid.attach(offset_labels, 0, 7, 1, 1)

        labelOpacity = Gtk.Label()
        labelOpacity.set_text("Opacity")
        labelOpacity.set_justify(Gtk.Justification.LEFT)
        grid.attach(labelOpacity, 0, 8, 1, 1)

        self.trackbarOpacity = Gtk.Scale.new_with_range(0, 0, 100, 1)
        self.trackbarOpacity.connect(
            "value-changed", self.change_value, 'opacity')
        grid.attach(self.trackbarOpacity, 0, 8, 1, 1)

        labelOpacity = Gtk.Label()
        labelOpacity.set_text("X Position")
        labelOpacity.set_justify(Gtk.Justification.LEFT)
        grid.attach(labelOpacity, 0, 9, 1, 1)

        self.trackbarOffsetX = Gtk.Scale.new_with_range(0, -100, 100, 1)
        self.trackbarOffsetX.connect(
            "value-changed", self.change_value, 'x')
        grid.attach(self.trackbarOffsetX, 0, 9, 1, 1)

        labelOpacity = Gtk.Label()
        labelOpacity.set_text("Y Position")
        labelOpacity.set_justify(Gtk.Justification.LEFT)
        grid.attach(labelOpacity, 0, 10, 1, 1)

        self.trackbarOffsetY = Gtk.Scale.new_with_range(0, -100, 100, 1)
        self.trackbarOffsetY.connect(
            "value-changed", self.change_value, 'y')
        grid.attach(self.trackbarOffsetY, 0, 10, 1, 1)

        labelOpacity = Gtk.Label()
        labelOpacity.set_text("Rotate L/R")
        labelOpacity.set_justify(Gtk.Justification.LEFT)
        grid.attach(labelOpacity, 0, 11, 1, 1)

        self.trackbarRotateLR = Gtk.Scale.new_with_range(0, -90, 90, 1)
        self.trackbarRotateLR.connect(
            "value-changed", self.change_value, 'rotateLR')
        grid.attach(self.trackbarRotateLR, 0, 11, 1, 1)

        labelOpacity = Gtk.Label()
        labelOpacity.set_text("Rotate U/D")
        labelOpacity.set_justify(Gtk.Justification.LEFT)
        grid.attach(labelOpacity, 0, 12, 1, 1)

        self.trackbarRotateUD = Gtk.Scale.new_with_range(0, -90, 90, 1)
        self.trackbarRotateUD.connect(
            "value-changed", self.change_value, 'rotateUD')
        grid.attach(self.trackbarRotateUD, 0, 12, 1, 1)

        labelIndexGoTo = Gtk.Label()
        labelIndexGoTo.set_text("Current Index")
        labelIndexGoTo.set_justify(Gtk.Justification.LEFT)
        grid.attach(labelIndexGoTo, 1, 10, 1, 1)

        self.indexGoTo = Gtk.Entry()
        grid.attach(self.indexGoTo, 1, 11, 1, 1)

        button12 = Gtk.Button("Go to Index")
        button12.connect("clicked", self.go_to_index)
        grid.attach(button12, 1, 12, 1, 1)  # grid location

        # self.setup_trackbars(self.range_filter)

    def go_to_index(self, widget):
        index = self.indexGoTo.get_text()
        print(f"Current index {index}")

    def load_image(self, widget, sensor):
        self.imageArray1 = cv2.imread(os.path.join(
            self.sensorOnePath, self.sensorOneImages[self.count]))
        self.imageArray1 = cv2.cvtColor(self.imageArray1, cv2.COLOR_BGR2RGB)
        self.imageArray1 = cv2.resize(self.imageArray1, (320, 240))
        h1, w1, d1 = self.imageArray1.shape
        pixbuf1 = GdkPixbuf.Pixbuf.new_from_data(self.imageArray1.tostring(
        ), GdkPixbuf.Colorspace.RGB, False, 8, w1, h1, w1*3, None, None)

        self.imageArray2 = cv2.imread(os.path.join(
            self.sensorTwoPath, self.sensorTwoImages[self.count]))
        self.imageArray2 = cv2.cvtColor(self.imageArray2, cv2.COLOR_BGR2RGB)
        self.imageArray2 = cv2.resize(self.imageArray2, (320, 240))
        h2, w2, d2 = self.imageArray2.shape
        pixbuf2 = GdkPixbuf.Pixbuf.new_from_data(self.imageArray2.tostring(
        ), GdkPixbuf.Colorspace.RGB, False, 8, w2, h2, w2*3, None, None)

        if sensor == 1:
            self.image1.set_from_pixbuf(pixbuf1)
        elif sensor == 2:
            self.image2.set_from_pixbuf(pixbuf2)
        else:
            self.image1.set_from_pixbuf(pixbuf1)
            self.image2.set_from_pixbuf(pixbuf2)

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def load_folder_images(self, image_path, sensor):
        """Load folder images using a path
        Tells it which folder to load, and which sensor
        array to add the listing of images to
        """
        for f in os.listdir(os.path.join(image_path)):
            if sensor == 1:
                self.sensorOneImages.append(f)
            else:
                self.sensorTwoImages.append(f)

    def on_save_folder(self, widget, sensor_number):
        """Where to save images. Sets the proper
        path for self.sensorXsave
        """
        dialog = Gtk.FileChooserDialog("Please choose a save folder for your annotations", self,
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")

            # set the global filePath for the dialog buttons
            self.sensorTwoSaveFolderPath = dialog.get_filename()
            print("Save folder selected for Sensor 2: " +
                  self.sensorTwoSaveFolderPath)

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def on_sync_folders(self, widget):
        """Sync the image folders in case of
        any non-matching images
        """

        # Remove DS_Store in case came over from Macs
        if '.DS_Store' in self.sensorOneImages:
            self.sensorOneImages.remove('.DS_Store')

        if '.DS_Store' in self.sensorTwoImages:
            self.sensorTwoImages.remove('.DS_Store')

        # Sort images in arrays to make comparisons easier
        # Makes it easier to read in debugger, though is
        # probably unnecessary in the function overall
        self.sensorOneImages = natsorted(
            self.sensorOneImages, key=lambda y: y.lower())
        self.sensorTwoImages = natsorted(
            self.sensorTwoImages, key=lambda y: y.lower())

        # set the initial point to the next item to be labeled
        # since this is determined by array position, 0 positioning doesn't matter
        if self.sensorOneSaveFolderPath:
            self.count = len(os.listdir(self.sensorOneSaveFolderPath))

        # Do a directoy comparison
        dcmp = dircmp(self.sensorOnePath, self.sensorTwoPath)

        # Delete images that only exist one directory or another
        for filename in dcmp.left_only:
            os.remove(os.path.join(self.sensorOnePath, filename))

        for filename in dcmp.right_only:
            os.remove(os.path.join(self.sensorTwoPath, filename))

        print('Sync complete. Unmatched files deleted.')

        self.fileLabel1.set_text(self.sensorOneImages[self.count])
        self.fileLabel2.set_text(self.sensorTwoImages[self.count])

        self.load_image(self.image1, 1)
        self.load_image(self.image2, 2)

    def on_folder_clicked(self, widget, sensor_number):
        dialog = Gtk.FileChooserDialog("Please choose a folder", self,
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())

            # set the global filePath for the dialog buttons
            if sensor_number == 1:
                self.sensorOnePath = dialog.get_filename()
                self.load_folder_images(self.sensorOnePath, sensor_number)
            else:
                self.sensorTwoPath = dialog.get_filename()
                self.load_folder_images(self.sensorTwoPath, sensor_number)

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def load_next_image(self, widget):
        if self.count >= (len(self.sensorOneImages) - 1):
            print('End of folder reached.')
        else:
            self.count += 1

        self.load_image(self.image1, 1)
        self.load_image(self.image2, 2)

        # If we're in the labeled zone, add labels
        if (len(os.listdir(self.sensorOneSaveFolderPath)) > self.count):
            self.load_prior_boxes()

        self.fileLabel1.set_text(self.sensorOneImages[self.count])
        self.fileLabel2.set_text(self.sensorTwoImages[self.count])

    def load_prev_image(self, widget):
        if self.count == 0:
            print('Beginning of folder reached.')
        else:
            self.count -= 1

        self.load_image(self.image1, 1)
        self.load_image(self.image2, 2)

        # If we're in the labeled zone, add labels
        if (len(os.listdir(self.sensorOneSaveFolderPath)) > self.count):
            self.load_prior_boxes()

        self.fileLabel1.set_text(self.sensorOneImages[self.count])
        self.fileLabel2.set_text(self.sensorTwoImages[self.count])

    def callback(self, value):
        pass

    def calc_manual_rectangles(self, widget):
        self.load_image(self.image1, 1)
        self.load_image(self.image2, 2)

        xMin1Sensor2 = str(self.xMin1SensorTwo.get_text())
        xMax1Sensor2 = str(self.xMax1SensorTwo.get_text())
        yMin1Sensor2 = str(self.yMin1SensorTwo.get_text())
        yMax1Sensor2 = str(self.yMax1SensorTwo.get_text())

        img = cv2.rectangle(self.imageArray1, ((int(xMin1Sensor2)+int(self.xMinOffset.get_text())), (int(yMin1Sensor2)+int(self.yMinOffset.get_text()))),
                            ((int(xMax1Sensor2)+int(self.xMaxOffset.get_text())), (int(yMax1Sensor2)+int(self.yMaxOffset.get_text()))), (0, 255, 0), 2)
        img2 = cv2.rectangle(self.imageArray2, (int(xMin1Sensor2), int(
            yMin1Sensor2)), (int(xMax1Sensor2), int(yMax1Sensor2)), (0, 255, 0), 2)

        self.xMin1SensorOne.set_text(
            str(int(xMin1Sensor2)+int(self.xMinOffset.get_text())))
        self.yMin1SensorOne.set_text(
            str(int(yMin1Sensor2)+int(self.yMinOffset.get_text())))
        self.xMax1SensorOne.set_text(
            str(int(xMax1Sensor2)+int(self.xMaxOffset.get_text())))
        self.yMax1SensorOne.set_text(
            str(int(yMax1Sensor2)+int(self.yMaxOffset.get_text())))

        h1, w1, d1 = img.shape
        pixbuf1 = GdkPixbuf.Pixbuf.new_from_data(
            img.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w1, h1, w1*3, None, None)
        self.image1.set_from_pixbuf(pixbuf1)

        h3, w3, d3 = img2.shape
        pixbuf2 = GdkPixbuf.Pixbuf.new_from_data(
            img2.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w3, h3, w3*3, None, None)
        self.image2.set_from_pixbuf(pixbuf2)

    def change_value(self, value, channel):
        if channel == 'opacity':
            self.opacity = value.get_value()
        elif channel == 'x':
            self.x_offset = value.get_value()
        elif channel == 'y':
            self.y_offset = value.get_value()
        elif channel == 'rotateLR':
            self.rotateLR = value.get_value()
        elif channel == 'rotateUD':
            self.rotateUD = value.get_value()
        else:
            pass

        frame_to_thresh = self.imageArray2.copy()
        thresh = cv2.inRange(frame_to_thresh, (self.red_value_min, self.green_value_min,
                                               self.blue_value_min), (self.red_value_max, self.green_value_max, self.blue_value_max))
        preview = cv2.bitwise_and(
            self.imageArray2, self.imageArray2, mask=thresh)

        h3, w3, d3 = preview.shape
        pixbuf3 = GdkPixbuf.Pixbuf.new_from_data(preview.tostring(
        ), GdkPixbuf.Colorspace.RGB, False, 8, w3, h3, w3*3, None, None)
        self.image3.set_from_pixbuf(pixbuf3)

    def setup_trackbars(self, range_filter):
        # cv2.namedWindow("Trackbars", 0)

        for i in ["MIN", "MAX"]:
            v = 50 if i == "MIN" else 75

            for j in self.range_filter:
                cv2.createTrackbar("%s_%s" % (
                    j, i), 'Multi-Sensor Marking App', v, 100, self.callback)

    def get_trackbar_values(self, range_filter):
        values = []

        for i in ["MIN", "MAX"]:
            for j in self.range_filter:
                v = cv2.getTrackbarPos("%s_%s" % (j, i), self.trackbarBox)
                values.append(v)

        return values

    def detect_blobs(self, widget):
        lower = np.array(
            [self.red_value_min, self.green_value_min, self.blue_value_min], dtype="uint8")
        upper = np.array(
            [self.red_value_max, self.green_value_max, self.blue_value_max], dtype="uint8")

        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv2.inRange(self.imageArray2, lower, upper)
        # mask = cv2.GaussianBlur(mask, (3,3), 0)

        (cnts, _) = cv2.findContours(mask.copy(),
                                     cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) > 0:
            cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
            x, y, w, h = cv2.boundingRect(cnt)
            self.contourXmin = x
            self.contourYmin = y
            self.contourXmax = x + w
            self.contourYmax = y + h
            img = cv2.rectangle(self.imageArray1, ((x+int(self.xMinOffset.get_text())), (y+int(self.xMaxOffset.get_text()))),
                                ((x+w+int(self.yMinOffset.get_text())), (y+h+int(self.yMaxOffset.get_text()))), (0, 255, 0), 2)
            img2 = cv2.rectangle(self.imageArray2, (x, y),
                                 (x+w, y+h), (0, 255, 0), 2)
            self.xMin1SensorOne.set_text(
                str(x+int(self.xMinOffset.get_text())))
            self.yMin1SensorOne.set_text(
                str(y+int(self.yMinOffset.get_text())))
            self.xMax1SensorOne.set_text(
                str(x+w+int(self.xMaxOffset.get_text())))
            self.yMax1SensorOne.set_text(
                str(y+h+int(self.yMaxOffset.get_text())))
            self.xMin1SensorTwo.set_text(str(x))
            self.xMax1SensorTwo.set_text(str(x+w))
            self.yMin1SensorTwo.set_text(str(y))
            self.yMax1SensorTwo.set_text(str(y+h))

        h1, w1, d1 = img.shape
        pixbuf1 = GdkPixbuf.Pixbuf.new_from_data(
            img.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w1, h1, w1*3, None, None)
        self.image1.set_from_pixbuf(pixbuf1)

        h3, w3, d3 = img2.shape
        pixbuf2 = GdkPixbuf.Pixbuf.new_from_data(
            img2.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w3, h3, w3*3, None, None)
        self.image2.set_from_pixbuf(pixbuf2)

    def reset_labels(self, widget):
        self.load_image(self.image1, 1)
        self.load_image(self.image2, 2)

        self.xMin1SensorOne.set_text("0")
        self.yMin1SensorOne.set_text("0")
        self.xMax1SensorOne.set_text("0")
        self.yMax1SensorOne.set_text("0")
        self.xMin1SensorTwo.set_text("0")
        self.xMax1SensorTwo.set_text("0")
        self.yMin1SensorTwo.set_text("0")
        self.yMax1SensorTwo.set_text("0")
