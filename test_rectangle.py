import cv2
import argparse
import time
import os
import sys
import xml.etree.ElementTree as ET


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--imageLocation", type=str, default="", required=True,
                help="name of image to test")
ap.add_argument("-b", "--boundingBox", type=str, default=False,
                help="bonding box file location")
args = vars(ap.parse_args())

dir_path = os.path.dirname(os.path.realpath(__file__))


def load_boxes(image):
    """ Load the box data from the drives if it exists.
           Currently only works on XML files that have 1 item listed.
                   """

    path1 = os.path.join(dir_path, args["boundingBox"])

    tree1 = ET.parse(path1)
    root1 = tree1.getroot()

    r1Xmin = root1[4][5][0].text
    r1Ymin = root1[4][5][1].text
    r1Xmax = root1[4][5][2].text
    r1Ymax = root1[4][5][3].text

    image2 = cv2.rectangle(image, (int(r1Xmin), int(r1Ymin)),
                           (int(r1Xmax), int(r1Ymax)), (0, 255, 0), 2)

    return image2


while True:
    path = os.path.join(dir_path, args["imageLocation"])

    image = cv2.imread(path)

    image2 = load_boxes(image)

    cv2.imshow("Image2", image2)

    if (cv2.waitKey(1) & 0xFF) == ord('q'):  # Hit `q` to exit
        cv2.destroyAllWindows()
        break
