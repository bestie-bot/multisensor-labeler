# Standard imports
from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
import cv2
import argparse
import numpy as np


ap = argparse.ArgumentParser()
ap.add_argument('-i', '--image', required=False, help='Path to the image')
args = vars(ap.parse_args())
 
# Read image
image = cv2.imread(args['image'])
dim = (320, 240)
image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(image, (5, 5), 0)

(T, thresh) = cv2.threshold(blurred, 170, 255, cv2.THRESH_BINARY)

# (T, threshInv) = cv2.threshold(blurred, 155, 255, cv2.THRESH_BINARY_INV)

(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print('cnts: ', len(cnts))

# NEXT STEP: GO THROUGH AND GRAB ALL THE BLOBS WITH A CERTAIN SIZE. LOOK
# AT PYIMAGSERACH SPECIAL WATERSHED ALGORITHM

for i in range(2):
	cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[i]
	rotbox = cv2.minAreaRect(cnt)
	coords = cv2.boxPoints(rotbox)
	rect = cv2.boundingRect(cnt)

	# print("coords: ", coords)
	# print("vontour area:", rect)
	x,y,w,h = rect
	cv2.rectangle(thresh,(x,y),(x+w,y+h),(255,255,255),2)

cv2.imshow("TB: ", thresh)



# cv2.imshow("BA: ", cv2.bitwise_and(image, image, mask = threshInv))
cv2.waitKey(0)