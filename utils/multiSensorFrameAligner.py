import gi
gi.require_version('Gtk', '4.0')
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
from functools import partial
import time



class MultiSensorFrameAligner(Gtk.Window):
    def __init__(self, app=None):
        super().__init__(title="Multi-Sensor Image Alignment for 2 Sensors")

        if app:
            self.set_application(app)

        self.sensorOnePath = ''
        self.sensorOneImages = []
        self.sensorTwoPath = ''
        self.sensorTwoImages = []
        self.sensorOneSaveFolderPath = ''
        self.sensorTwoSaveFolderPath = ''
        self.imageArray1 = []
        self.imageArray2 = []
        self.imageArray3 = []
        self.currentIndex = 0
        self.count = 0
        self.filter = 'rgb'
        self.range_filter = self.filter.upper()
        self.opacity = 50
        self.x_offset = 0
        self.y_offset = 0
        self.rotateLR = 0
        self.rotateUD = 0
        self.ongoing_x_offset = 0
        self.initial_y_offset = 0
        self.time_through = 0
        self.scale = 1.0

        grid = Gtk.Grid()
        self.set_child(grid)

        button1 = Gtk.Button(label="Choose Sensor 1 Images Folder")
        button1.connect("clicked", self.on_folder_clicked, 1)
        grid.attach(button1, 0, 1, 1, 1)

        button2 = Gtk.Button(label="Choose Sensor 2 Images Folder")
        button2.connect("clicked", self.on_folder_clicked, 2)
        grid.attach(button2, 1, 1, 1, 1)

        button3 = Gtk.Button(label="Sync Folders")
        button3.connect("clicked", self.on_sync_folders)
        grid.attach(button3, 0, 2, 1, 1)

        button5 = Gtk.Button(label="Choose Sensor 2 Save Folder")
        button5.connect("clicked", self.on_save_folder)
        grid.attach(button5, 2, 1, 1, 1)

        self.button6 = Gtk.Button(label="Load next image")
        self.button6.connect("clicked", self.load_next_image)
        grid.attach(self.button6, 1, 2, 1, 1)  # grid location

        button7 = Gtk.Button(label="Load previous image")
        button7.connect("clicked", self.load_prev_image)
        grid.attach(button7, 2, 2, 1, 1)  # grid location

        self.button11 = Gtk.Button(label="Calculate Offsets")
        self.button11.connect("clicked", self.calc_offsets)
        grid.attach(self.button11, 0, 12, 1, 1)  # grid location

        button12 = Gtk.Button(label="Save Adjusted Image")
        button12.connect("clicked", self.save_image)
        grid.attach(button12, 1, 8, 1, 1)  # grid location

        self.image1 = Gtk.Picture()
        self.image2 = Gtk.Picture()
        self.image3 = Gtk.Picture()
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

        self.trackbarOpacity = Gtk.Entry()
        grid.attach(self.trackbarOpacity, 0, 8, 1, 1)
        self.trackbarOpacity.set_text(str(50))

        labelScale = Gtk.Label()
        labelScale.set_text("Scale")
        labelScale.set_justify(Gtk.Justification.LEFT)
        grid.attach(labelScale, 0, 9, 1, 1)

        self.trackbarScale = Gtk.Entry()
        grid.attach(self.trackbarScale, 0, 9, 1, 1)
        self.trackbarScale.set_text(str(1))

        labelOffsetX = Gtk.Label()
        labelOffsetX.set_text("X Position")
        labelOffsetX.set_justify(Gtk.Justification.LEFT)
        grid.attach(labelOffsetX, 0, 10, 1, 1)

        self.trackbarOffsetX = Gtk.Entry()
        grid.attach(self.trackbarOffsetX, 0, 10, 1, 1)
        self.trackbarOffsetX.set_text(str(0))

        labelOffsetY = Gtk.Label()
        labelOffsetY.set_text("Y Position")
        labelOffsetY.set_justify(Gtk.Justification.LEFT)
        grid.attach(labelOffsetY, 0, 11, 1, 1)

        self.trackbarOffsetY = Gtk.Entry()
        grid.attach(self.trackbarOffsetY, 0, 11, 1, 1)
        self.trackbarOffsetY.set_text(str(0))

        labelIndexGoTo = Gtk.Label()
        labelIndexGoTo.set_text("Current Index")
        labelIndexGoTo.set_justify(Gtk.Justification.LEFT)
        grid.attach(labelIndexGoTo, 1, 10, 1, 1)

        self.indexGoTo = Gtk.Entry()
        grid.attach(self.indexGoTo, 1, 11, 1, 1)
        self.indexGoTo.set_text(str(self.count + 1))

        button12 = Gtk.Button(label="Go to Index")
        button12.connect("clicked", self.go_to_index)
        grid.attach(button12, 1, 12, 1, 1)  # grid location

        # self.setup_trackbars(self.range_filter)

    def go_to_index(self, widget):
        self.count = (int(self.indexGoTo.get_text()) - 1)
        self.fileLabel1.set_text(self.sensorOneImages[self.count])
        self.load_image(self.image1, 1)

    def load_image(self, widget, sensor):
        print('Loading image...')
        self.imageArray1 = cv2.imread(os.path.join(
            self.sensorOnePath, self.sensorOneImages[self.count]))
        self.imageArray1 = cv2.cvtColor(self.imageArray1, cv2.COLOR_BGR2RGB)
        self.imageArray1 = cv2.resize(self.imageArray1, (320, 240))
        print('Image 1 loaded.')

        self.imageArray2 = cv2.imread(os.path.join(
            self.sensorTwoPath, self.sensorTwoImages[self.count]))
        self.imageArray2 = cv2.cvtColor(self.imageArray2, cv2.COLOR_BGR2RGB)
        self.imageArray2 = cv2.resize(self.imageArray2, (320, 240))
        print('Image 2 loaded.')

        self.calc_offsets(self.button11)

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserNative("Please choose a file", self,
                                       Gtk.FileChooserAction.OPEN,
                                       "Open", "Cancel")

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

    def on_save_folder_response(self, dialog, response_id):
        print("Sorting response...")
        
        if response_id == Gtk.ResponseType.OK:
            print("Select clicked")

            # set the global filePath for the dialog buttons
            self.sensorTwoSaveFolderPath = dialog.get_file().get_path()
            print("Save folder selected for Sensor 2: " + self.sensorTwoSaveFolderPath)
        elif response_id == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()

    def on_save_folder(self, widget):
        """Where to save images. Sets the proper path for self.sensorXsave
        """
        
        dialog = Gtk.FileChooserDialog(
            title="Please choose a save folder for your annotations",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )

        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda w: dialog.response(Gtk.ResponseType.CANCEL))
        dialog.add_action_widget(cancel_button, Gtk.ResponseType.CANCEL)

        open_button = Gtk.Button(label="Open")
        open_button.connect("clicked", lambda w: dialog.response(Gtk.ResponseType.OK))
        dialog.add_action_widget(open_button, Gtk.ResponseType.OK)

        dialog.connect("response", self.on_save_folder_response)
        dialog.present()

    def calc_offsets(self, widget):
        print('Calculating offsets...')

        self.opacity = int(self.trackbarOpacity.get_text())
        self.x_offset = int(self.trackbarOffsetX.get_text())
        self.y_offset = int(self.trackbarOffsetY.get_text())
        self.scale = float(self.trackbarScale.get_text())

        print('Opacity: ', self.opacity)
        print('X Offset: ', self.x_offset)
        print('Y Offset: ', self.y_offset)
        print('Scale: ', self.scale)

        imageFromScale = self.calc_scale(self.scale)
        imageFromMove = self.move_image(
            self.x_offset, self.y_offset, imageFromScale)
        imageFromOpacity = self.calc_opacity(self.opacity, imageFromMove)
        print('Offsets calculated.')

        self.load_overlay_image(imageFromOpacity)

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

        self.load_image(self.image1, 1)

    def on_dialog_response(self, dialog, response_id, sensor_number):
        print("Sorting response...")
        
        if response_id == Gtk.ResponseType.OK:
            print("Selected folder:", dialog.get_file().get_path())
            # print("Folder selected: " + dialog.get_filename())

            # set the global filePath for the dialog buttons
            if sensor_number == 1:
                self.sensorOnePath = dialog.get_file().get_path()
                self.load_folder_images(self.sensorOnePath, sensor_number)
            else:
                self.sensorTwoPath = dialog.get_file().get_path()
                self.load_folder_images(self.sensorTwoPath, sensor_number)
        elif response_id == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()

    def on_folder_clicked(self, widget, sensor_number):
        print("Button clicked, attempting to open dialog...")

        dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )

        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda w: dialog.response(Gtk.ResponseType.CANCEL))
        dialog.add_action_widget(cancel_button, Gtk.ResponseType.CANCEL)

        open_button = Gtk.Button(label="Open")
        open_button.connect("clicked", lambda w: dialog.response(Gtk.ResponseType.OK))
        dialog.add_action_widget(open_button, Gtk.ResponseType.OK)

        dialog.connect("response", self.on_dialog_response, sensor_number)
        dialog.present()

    def load_next_image(self, widget):
        if self.count >= (len(self.sensorOneImages) - 1):
            print('End of folder reached.')
        else:
            self.count += 1

        self.load_image(self.image1, 1)
        self.load_image(self.image2, 2)

        # Set the index count box
        self.indexGoTo.set_text(str(self.count + 1))

        self.calc_offsets(self.button11)

        # If we're in the labeled zone, add labels
        # if (len(os.listdir(self.sensorOneSaveFolderPath)) > self.count):
        # self.load_prior_boxes()

        self.fileLabel1.set_text(self.sensorOneImages[self.count])

    def load_prev_image(self, widget):
        if self.count == 0:
            print('Beginning of folder reached.')
        else:
            self.count -= 1

        self.load_image(self.image1, 1)
        self.load_image(self.image2, 2)

        # Set the index count box
        self.indexGoTo.set_text(str(self.count + 1))

        self.calc_offsets(self.button11)

        # If we're in the labeled zone, add labels
        # if (len(os.listdir(self.sensorOneSaveFolderPath)) > self.count):
        # self.load_prior_boxes()

        self.fileLabel1.set_text(str(self.sensorOneImages[self.count]))

    def callback(self, value):
        pass

    def load_overlay_image(self, image):
        print('Loading overlay image...')
        h3, w3, d3 = self.imageArray1.shape
        pixbuf3 = GdkPixbuf.Pixbuf.new_from_data(
            image.tostring(), GdkPixbuf.Colorspace.RGB, False, 8, w3, h3, w3*3, None, None)
        print('Overlay image loaded.')
        if pixbuf3:
            print(f"Pixbuf dimensions: {pixbuf3.get_width()} x {pixbuf3.get_height()}")
        else:
            print("Pixbuf is None!")

        cv2.imwrite("/home/richardeverts/Documents/Bestie Bot/Product/test_image.png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        
        print('Displaying overlay image...')
        self.image1.set_size_request(320, 240)
        self.image1.set_pixbuf(pixbuf3)


    def calc_opacity(self, value, image):
        alpha = value / 100
        frame1 = self.imageArray1.copy()

        # if len(self.imageArray3) > 0:
        #     frame2 = self.imageArray3.copy()
        # else:
        #     frame2 = self.imageArray2.copy()
        #     self.imageArray3 = frame2

        revisedImage = cv2.addWeighted(
            image, alpha, frame1, 1 - alpha, 0, frame1)

        return revisedImage

    def move_image(self, x=0, y=0, image=None):
        # Store height and width of the image
        # if len(self.imageArray3) > 0:
        #     frame2 = self.imageArray3.copy()
        # else:
        #     frame2 = self.imageArray2.copy()

        height, width = image.shape[:2]

        T = np.float32([[1, 0, x], [0, 1, y]])

        revisedImage = cv2.warpAffine(image, T, (width, height))

        return revisedImage

    def calc_scale(self, scale):
        if scale <= 0:
            print("Invalid scale value:", scale)
            return self.imageArray2
        
        desired_h = 240
        desired_w = 320

        # old_size is in (height, width) format
        h, w = self.imageArray1.shape[:2]

        h1 = int(240 * scale)
        w1 = int(320 * scale)

        im = cv2.resize(self.imageArray2, (0, 0),
                        fx=scale, fy=scale)

        delta_w = desired_w - w1
        delta_h = desired_h - h1
        top, bottom = delta_h//2, delta_h-(delta_h//2)
        left, right = delta_w//2, delta_w-(delta_w//2)

        # Make sure rounding errors accounted for
        new_h, new_w = im.shape[:2]

        if (left + right + new_w) != desired_w:
            right -= 1

        if (top + bottom + new_h) != desired_h:
            bottom -= 1

        color = [0, 0, 0]
        image = cv2.copyMakeBorder(im, int(top), int(bottom), int(left), int(right), cv2.BORDER_CONSTANT,
                                   value=color)

        return image

    def save_image(self, widget):
        path = self.sensorTwoSaveFolderPath + \
            '/' + self.sensorOneImages[self.count]

        self.x_offset = int(self.trackbarOffsetX.get_text())
        self.y_offset = int(self.trackbarOffsetY.get_text())
        self.scale = float(self.trackbarScale.get_text())

        imageFromScale = self.calc_scale(self.scale)
        imageFromMove = self.move_image(
            self.x_offset, self.y_offset, imageFromScale)

        image = cv2.cvtColor(imageFromMove, cv2.COLOR_BGR2GRAY)

        cv2.imwrite(path, image)

        self.imageArray3 = []
        self.time_through = 0

        self.load_next_image(self.button6)
        self.calc_offsets(self.button11)
