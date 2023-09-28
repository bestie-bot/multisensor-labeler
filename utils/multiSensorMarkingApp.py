# import the necessary packages
from __future__ import print_function
from PIL import Image
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GdkPixbuf
import xml.etree.ElementTree as ET
from filecmp import dircmp
import numpy as np
import datetime
import cv2
import os, sys
from natsort import natsorted, ns

class MultiSensorMarkingApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Multi-Sensor Marking App")
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
        self.red_value_min = 0
        self.green_value_min = 0
        self.blue_value_min = 0
        self.red_value_max = 0
        self.green_value_max = 0
        self.blue_value_max = 0

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

        button4 = Gtk.Button("Choose Sensor 1 Save Folder")
        button4.connect("clicked", self.on_save_folder, 1)
        grid.attach(button4, 2, 1, 1, 1)

        button5 = Gtk.Button("Choose Sensor 2 Save Folder")
        button5.connect("clicked", self.on_save_folder, 2)
        grid.attach(button5, 3, 1, 1, 1)

        button6 = Gtk.Button("Load next image")
        button6.connect("clicked", self.load_next_image)
        grid.attach(button6, 1, 2, 1, 1) #grid location

        button7 = Gtk.Button("Load previous image")
        button7.connect("clicked", self.load_prev_image)
        grid.attach(button7, 2, 2, 1, 1) #grid location

        button8 = Gtk.Button("Detect Blobs")
        button8.connect("clicked", self.detect_blobs)
        grid.attach(button8, 2, 7, 1, 1) #grid location

        button9 = Gtk.Button("Save Labels")
        button9.connect("clicked", self.save_labels)
        grid.attach(button9, 2, 8, 1, 1) #grid location

        button10 = Gtk.Button("Reset Labels")
        button10.connect("clicked", self.reset_labels)
        grid.attach(button10, 2, 9, 1, 1) #grid location

        button11 = Gtk.Button("Calc S2 Boxes Manually")
        button11.connect("clicked", self.calc_manual_rectangles)
        grid.attach(button11, 2, 10, 1, 1) #grid location

        self.image1 = Gtk.Image()
        grid.attach(self.image1, 0, 3, 1, 1)

        self.image2 = Gtk.Image()
        grid.attach(self.image2, 1, 3, 1, 1)

        self.image3 = Gtk.Image()
        grid.attach(self.image3, 2, 3, 1, 1)

        self.fileLabel1 = Gtk.Label()
        self.fileLabel1.set_text("")
        self.fileLabel1.set_justify(Gtk.Justification.LEFT)
        grid.attach(self.fileLabel1, 0, 4, 1, 1)

        self.fileLabel2 = Gtk.Label()
        self.fileLabel2.set_text("")
        self.fileLabel2.set_justify(Gtk.Justification.LEFT)
        grid.attach(self.fileLabel2, 1, 4, 1, 1)

        threshold_mins_label = Gtk.Label()
        threshold_mins_label.set_label("Threshold Mins (RGB)")
        grid.attach(threshold_mins_label, 0, 7, 1, 1)

        self.trackbarBoxRMin = Gtk.Scale.new_with_range(0, 0, 255, 1)
        self.trackbarBoxRMin.connect("value-changed", self.change_value, 'r', 'min')
        grid.attach(self.trackbarBoxRMin, 0, 8, 1, 1)

        self.trackbarBoxGMin = Gtk.Scale.new_with_range(0, 0, 255, 1)
        self.trackbarBoxGMin.connect("value-changed", self.change_value, 'g', 'min')
        grid.attach(self.trackbarBoxGMin, 0, 9, 1, 1)

        self.trackbarBoxBMin = Gtk.Scale.new_with_range(0, 0, 255, 1)
        self.trackbarBoxBMin.connect("value-changed", self.change_value, 'b', 'min')
        grid.attach(self.trackbarBoxBMin, 0, 10, 1, 1)

        threshold_max_label = Gtk.Label()
        threshold_max_label.set_label("Threshold Maxes (RGB)")
        grid.attach(threshold_max_label, 1, 7, 1, 1)

        self.trackbarBoxRMax = Gtk.Scale.new_with_range(0, 0, 255, 1)
        self.trackbarBoxRMax.connect("value-changed", self.change_value, 'r', 'max')
        grid.attach(self.trackbarBoxRMax, 1, 8, 1, 1)

        self.trackbarBoxGMax = Gtk.Scale.new_with_range(0, 0, 255, 1)
        self.trackbarBoxGMax.connect("value-changed", self.change_value, 'g', 'max')
        grid.attach(self.trackbarBoxGMax, 1, 9, 1, 1)

        self.trackbarBoxBMax = Gtk.Scale.new_with_range(0, 0, 255, 1)
        self.trackbarBoxBMax.connect("value-changed", self.change_value, 'b', 'max')
        grid.attach(self.trackbarBoxBMax, 1, 10, 1, 1)

        label1XMinX = Gtk.Label()
        label1XMinX.set_text("Sensor 1 X Min")
        label1XMinX.set_justify(Gtk.Justification.LEFT)
        grid.attach(label1XMinX, 0, 11, 1, 1)

        self.xMin1SensorOne = Gtk.Entry()
        grid.attach(self.xMin1SensorOne, 0, 12, 1, 1)

        label1XMaxX = Gtk.Label()
        label1XMaxX.set_text("Sensor 1 X Max")
        label1XMaxX.set_justify(Gtk.Justification.LEFT)
        grid.attach(label1XMaxX, 0, 13, 1, 1)

        self.xMax1SensorOne = Gtk.Entry()
        grid.attach(self.xMax1SensorOne, 0, 14, 1, 1)

        label1YMin = Gtk.Label()
        label1YMin.set_text("Sensor 1 Y Min")
        label1YMin.set_justify(Gtk.Justification.LEFT)
        grid.attach(label1YMin, 0, 15, 1, 1)

        self.yMin1SensorOne = Gtk.Entry()
        grid.attach(self.yMin1SensorOne, 0, 16, 1, 1)

        label1YMax = Gtk.Label()
        label1YMax.set_text("Sensor 1 Y Min")
        label1YMax.set_justify(Gtk.Justification.LEFT)
        grid.attach(label1YMax, 0, 17, 1, 1)

        self.yMax1SensorOne = Gtk.Entry()
        grid.attach(self.yMax1SensorOne, 0, 18, 1, 1)

        label2XMinX = Gtk.Label()
        label2XMinX.set_text("Sensor 2 X Min")
        label2XMinX.set_justify(Gtk.Justification.LEFT)
        grid.attach(label2XMinX, 1, 11, 1, 1)

        self.xMin1SensorTwo = Gtk.Entry()
        grid.attach(self.xMin1SensorTwo, 1, 12, 1, 1)

        label2XMaxX = Gtk.Label()
        label2XMaxX.set_text("Sensor 2 X Max")
        label2XMaxX.set_justify(Gtk.Justification.LEFT)
        grid.attach(label2XMaxX, 1, 13, 1, 1)

        self.xMax1SensorTwo = Gtk.Entry()
        grid.attach(self.xMax1SensorTwo, 1, 14, 1, 1)

        label2YMin = Gtk.Label()
        label2YMin.set_text("Sensor 2 Y Min")
        label2YMin.set_justify(Gtk.Justification.LEFT)
        grid.attach(label2YMin, 1, 15, 1, 1)

        self.yMin1SensorTwo = Gtk.Entry()
        grid.attach(self.yMin1SensorTwo, 1, 16, 1, 1)

        label2YMax = Gtk.Label()
        label2YMax.set_text("Sensor 2 Y Min")
        label2YMax.set_justify(Gtk.Justification.LEFT)
        grid.attach(label2YMax, 1, 17, 1, 1)

        self.yMax1SensorTwo = Gtk.Entry()
        grid.attach(self.yMax1SensorTwo, 1, 18, 1, 1)

        label3XMinX = Gtk.Label()
        label3XMinX.set_text("Offset X Min")
        label3XMinX.set_justify(Gtk.Justification.LEFT)
        grid.attach(label3XMinX, 2, 11, 1, 1)

        self.xMinOffset = Gtk.Entry()
        self.xMinOffset.set_text("5")
        grid.attach(self.xMinOffset, 2, 12, 1, 1)

        label3XMaxX = Gtk.Label()
        label3XMaxX.set_text("Offset X Max")
        label3XMaxX.set_justify(Gtk.Justification.LEFT)
        grid.attach(label3XMaxX, 2, 13, 1, 1)

        self.xMaxOffset = Gtk.Entry()
        self.xMaxOffset.set_text("-8")
        grid.attach(self.xMaxOffset, 2, 14, 1, 1)

        label3YMin = Gtk.Label()
        label3YMin.set_text("Offset Y Min")
        label3YMin.set_justify(Gtk.Justification.LEFT)
        grid.attach(label3YMin, 2, 15, 1, 1)

        self.yMinOffset = Gtk.Entry()
        self.yMinOffset.set_text("-5")
        grid.attach(self.yMinOffset, 2, 16, 1, 1)

        label3YMax = Gtk.Label()
        label3YMax.set_text("Offset Y Min")
        label3YMax.set_justify(Gtk.Justification.LEFT)
        grid.attach(label3YMax, 2, 17, 1, 1)

        self.yMaxOffset = Gtk.Entry()
        self.yMaxOffset.set_text("-35")
        grid.attach(self.yMaxOffset, 2, 18, 1, 1)

        # self.setup_trackbars(self.range_filter)

    def load_image(self, widget, sensor):
        self.imageArray1 = cv2.imread(os.path.join(self.sensorOnePath, self.sensorOneImages[self.count]))
        self.imageArray1 = cv2.cvtColor(self.imageArray1, cv2.COLOR_BGR2RGB)
        self.imageArray1 = cv2.resize(self.imageArray1, (320, 240))
        h1, w1, d1 = self.imageArray1.shape
        pixbuf1 = GdkPixbuf.Pixbuf.new_from_data(self.imageArray1.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w1, h1, w1*3, None, None)
            
        self.imageArray2 = cv2.imread(os.path.join(self.sensorTwoPath, self.sensorTwoImages[self.count]))
        self.imageArray2 = cv2.cvtColor(self.imageArray2, cv2.COLOR_BGR2RGB)
        self.imageArray2 = cv2.resize(self.imageArray2, (320, 240))
        h2, w2, d2 = self.imageArray2.shape
        pixbuf2 = GdkPixbuf.Pixbuf.new_from_data(self.imageArray2.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w2, h2, w2*3, None, None)
            
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
            if sensor_number == 1:
                self.sensorOneSaveFolderPath = dialog.get_filename()
                print("Save folder selected for Sensor 1: " + self.sensorOneSaveFolderPath)
            else:
                self.sensorTwoSaveFolderPath = dialog.get_filename()
                print("Save folder selected for Sensor 2: " + self.sensorTwoSaveFolderPath)

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
        self.sensorOneImages = natsorted(self.sensorOneImages, key=lambda y: y.lower())
        self.sensorTwoImages = natsorted(self.sensorTwoImages, key=lambda y: y.lower())

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


        img = cv2.rectangle(self.imageArray1,((int(xMin1Sensor2)+int(self.xMinOffset.get_text())),(int(yMin1Sensor2)+int(self.yMinOffset.get_text()))),((int(xMax1Sensor2)+int(self.xMaxOffset.get_text())),(int(yMax1Sensor2)+int(self.yMaxOffset.get_text()))),(0,255,0),2)
        img2 = cv2.rectangle(self.imageArray2,(int(xMin1Sensor2), int(yMin1Sensor2)),(int(xMax1Sensor2),int(yMax1Sensor2)),(0,255,0),2)
        
        self.xMin1SensorOne.set_text(str(int(xMin1Sensor2)+int(self.xMinOffset.get_text())))
        self.yMin1SensorOne.set_text(str(int(yMin1Sensor2)+int(self.yMinOffset.get_text())))
        self.xMax1SensorOne.set_text(str(int(xMax1Sensor2)+int(self.xMaxOffset.get_text())))
        self.yMax1SensorOne.set_text(str(int(yMax1Sensor2)+int(self.yMaxOffset.get_text())))

        h1, w1, d1 = img.shape
        pixbuf1 = GdkPixbuf.Pixbuf.new_from_data(img.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w1, h1, w1*3, None, None)        
        self.image1.set_from_pixbuf(pixbuf1)

        h3, w3, d3 = img2.shape
        pixbuf2 = GdkPixbuf.Pixbuf.new_from_data(img2.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w3, h3, w3*3, None, None)
        self.image2.set_from_pixbuf(pixbuf2)

    def change_value(self, value, channel, minMax):
        if minMax == 'min':
            if channel == 'r':
                self.red_value_min = value.get_value()
            elif channel == 'g':
                self.green_value_min = value.get_value()
            else:
                self.blue_value_min = value.get_value()
        else:
            if channel == 'r':
                self.red_value_max = value.get_value()
            elif channel == 'g':
                self.green_value_max = value.get_value()
            else:
                self.blue_value_max = value.get_value()

        frame_to_thresh = self.imageArray2.copy()
        thresh = cv2.inRange(frame_to_thresh, (self.red_value_min, self.green_value_min, self.blue_value_min), (self.red_value_max, self.green_value_max, self.blue_value_max))
        preview = cv2.bitwise_and(self.imageArray2, self.imageArray2, mask=thresh)

        h3, w3, d3 = preview.shape
        pixbuf3 = GdkPixbuf.Pixbuf.new_from_data(preview.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w3, h3, w3*3, None, None)
        self.image3.set_from_pixbuf(pixbuf3)

    def setup_trackbars(self, range_filter):
        # cv2.namedWindow("Trackbars", 0)

        for i in ["MIN", "MAX"]:
            v = 0 if i == "MIN" else 255

            for j in self.range_filter:
                cv2.createTrackbar("%s_%s" % (j, i), 'Multi-Sensor Marking App', v, 255, self.callback)

    def get_trackbar_values(self, range_filter):
        values = []

        for i in ["MIN", "MAX"]:
            for j in self.range_filter:
                v = cv2.getTrackbarPos("%s_%s" % (j, i), self.trackbarBox)
                values.append(v)

        return values

    def detect_blobs(self, widget):
        lower = np.array([self.red_value_min, self.green_value_min, self.blue_value_min], dtype = "uint8")
        upper = np.array([self.red_value_max, self.green_value_max, self.blue_value_max], dtype = "uint8")

        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv2.inRange(self.imageArray2, lower, upper)
        # mask = cv2.GaussianBlur(mask, (3,3), 0)

        (cnts, _) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) > 0:
            cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
            x,y,w,h = cv2.boundingRect(cnt)
            self.contourXmin = x
            self.contourYmin = y
            self.contourXmax = x + w
            self.contourYmax = y + h
            img = cv2.rectangle(self.imageArray1,((x+int(self.xMinOffset.get_text())),(y+int(self.xMaxOffset.get_text()))),((x+w+int(self.yMinOffset.get_text())),(y+h+int(self.yMaxOffset.get_text()))),(0,255,0),2)
            img2 = cv2.rectangle(self.imageArray2,(x,y),(x+w,y+h),(0,255,0),2)
            self.xMin1SensorOne.set_text(str(x+int(self.xMinOffset.get_text())))
            self.yMin1SensorOne.set_text(str(y+int(self.yMinOffset.get_text())))
            self.xMax1SensorOne.set_text(str(x+w+int(self.xMaxOffset.get_text())))
            self.yMax1SensorOne.set_text(str(y+h+int(self.yMaxOffset.get_text())))
            self.xMin1SensorTwo.set_text(str(x))
            self.xMax1SensorTwo.set_text(str(x+w))
            self.yMin1SensorTwo.set_text(str(y))
            self.yMax1SensorTwo.set_text(str(y+h))


        h1, w1, d1 = img.shape
        pixbuf1 = GdkPixbuf.Pixbuf.new_from_data(img.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w1, h1, w1*3, None, None)        
        self.image1.set_from_pixbuf(pixbuf1)

        h3, w3, d3 = img2.shape
        pixbuf2 = GdkPixbuf.Pixbuf.new_from_data(img2.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w3, h3, w3*3, None, None)
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

    def load_prior_boxes(self):
        """ Load the box data from the drives if it exists.
        Currently only works on XML files that have 1 item listed.
         """
        path1 = os.path.join(self.sensorOneSaveFolderPath, self.sensorOneImages[self.count])        
        path1 = path1.replace('.jpg', '.xml')

        path2 = os.path.join(self.sensorTwoSaveFolderPath, self.sensorTwoImages[self.count])
        path2 = path2.replace('.jpg', '.xml')

        tree1 = ET.parse(path1)
        root1 = tree1.getroot()

        tree2 = ET.parse(path2)
        root2 = tree2.getroot()

        r1Xmin = root1[3][1][0].text
        r1Ymin = root1[3][1][1].text
        r1Xmax = root1[3][1][2].text
        r1Ymax = root1[3][1][3].text

        r2Xmin = root2[3][1][0].text
        r2Ymin = root2[3][1][1].text
        r2Xmax = root2[3][1][2].text
        r2Ymax = root2[3][1][3].text

        img = cv2.rectangle(self.imageArray1,((int(r2Xmin)+int(self.xMinOffset.get_text())),(int(r2Ymin)+int(self.yMinOffset.get_text()))),((int(r2Xmax)+int(self.xMaxOffset.get_text())),(int(r2Ymax)+int(self.yMaxOffset.get_text()))),(0,255,0),2)
        img2 = cv2.rectangle(self.imageArray2,(int(r2Xmin),int(r2Ymin)),(int(r2Xmax),int(r2Ymax)),(0,255,0),2)
        
        self.xMin1SensorOne.set_text(r1Xmin)
        self.yMin1SensorOne.set_text(r1Ymin)
        self.xMax1SensorOne.set_text(r1Xmax)
        self.yMax1SensorOne.set_text(r1Ymax)
        self.xMin1SensorTwo.set_text(r2Xmin)
        self.yMin1SensorTwo.set_text(r2Ymin)
        self.xMax1SensorTwo.set_text(r2Xmax)
        self.yMax1SensorTwo.set_text(r2Ymax)

        h1, w1, d1 = img.shape
        pixbuf1 = GdkPixbuf.Pixbuf.new_from_data(img.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w1, h1, w1*3, None, None)        
        self.image1.set_from_pixbuf(pixbuf1)

        h3, w3, d3 = img2.shape
        pixbuf2 = GdkPixbuf.Pixbuf.new_from_data(img2.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w3, h3, w3*3, None, None)
        self.image2.set_from_pixbuf(pixbuf2)

    def save_labels(self, widget):
        img = cv2.imread(os.path.join(self.sensorTwoPath, self.sensorTwoImages[self.count]))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (320, 240))

        h, w, d = img.shape

        # create the file structure for sensor 2
        annotation = ET.Element('annotation')  
        folder = ET.SubElement(annotation, 'folder')
        folder.text = "thermal"
        filename = ET.SubElement(annotation, 'filename')
        filename.text = self.sensorTwoImages[self.count] 

        size = ET.SubElement(annotation, 'size')
        width = ET.SubElement(size, 'width')
        height = ET.SubElement(size, 'height')
        depth = ET.SubElement(size, 'depth')
        width.text = str(w)
        height.text = str(h)
        depth.text = str(d)

        obj = ET.SubElement(annotation, 'object')
        name = ET.SubElement(obj, 'name')
        bndbox = ET.SubElement(obj, 'name')
        xmin = ET.SubElement(bndbox, 'xmin')
        ymin = ET.SubElement(bndbox, 'ymin')
        xmax = ET.SubElement(bndbox, 'xmax')
        ymax = ET.SubElement(bndbox, 'ymax')

        name.text = 'person'
        xmin.text = str(self.contourXmin)
        ymin.text = str(self.contourYmin)
        xmax.text = str(self.contourXmax)
        ymax.text = str(self.contourYmax)     

        # create a new XML file with the results
        tree = ET.ElementTree(annotation)
        path = os.path.join(self.sensorTwoSaveFolderPath, self.sensorTwoImages[self.count])
        path = path.replace('.jpg', '.xml')
        print("[Saved Thermal XML file at]: ", path)
        tree.write(path)

        # create the file structure for sensor 1
        annotation = ET.Element('annotation') 
        folder = ET.SubElement(annotation, 'folder')
        folder.text = "rgb"
        filename = ET.SubElement(annotation, 'filename')
        filename.text = self.sensorOneImages[self.count] 

        size = ET.SubElement(annotation, 'size')
        width = ET.SubElement(size, 'width')
        height = ET.SubElement(size, 'height')
        depth = ET.SubElement(size, 'depth')
        width.text = str(w)
        height.text = str(h)
        depth.text = str(d)

        obj = ET.SubElement(annotation, 'object')
        name = ET.SubElement(obj, 'name')
        bndbox = ET.SubElement(obj, 'name')
        xmin = ET.SubElement(bndbox, 'xmin')
        ymin = ET.SubElement(bndbox, 'ymin')
        xmax = ET.SubElement(bndbox, 'xmax')
        ymax = ET.SubElement(bndbox, 'ymax')

        name.text = 'person'
        xmin.text = str(self.contourXmin + 5)
        ymin.text = str(self.contourYmin - 8)
        xmax.text = str(self.contourXmax - 5)
        ymax.text = str(self.contourYmax - 35)     

        # create a new XML file with the results
        tree = ET.ElementTree(annotation)
        path = os.path.join(self.sensorOneSaveFolderPath, self.sensorOneImages[self.count])
        path = path.replace('.jpg', '.xml')
        print("[Saved RGB XML file at]: ", path)
        tree.write(path)
        