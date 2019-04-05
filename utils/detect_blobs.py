# Standard imports
import cv2
import argparse
import numpy as np


ap = argparse.ArgumentParser()
ap.add_argument('-i', '--image', required=False, help='Path to the image')
args = vars(ap.parse_args())
 
# Read image
image = cv2.imread(args['image'])

# image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
dim = (320, 240)

image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

lower = np.array([0, 106, 190], dtype = "uint8")
upper = np.array([255, 255, 255], dtype = "uint8")

# find the colors within the specified boundaries and apply
# the mask
mask = cv2.inRange(image, lower, upper)
mask = cv2.GaussianBlur(mask, (3,3), 0)

(cnts, _) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if len(cnts) > 0:
	cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
	x,y,w,h = cv2.boundingRect(cnt)
	image = cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)


# print('mask', mask)
output = cv2.bitwise_and(image, image, mask = mask)
# show the images
print("shapes: ", image.shape, mask.shape)
cv2.imshow("images", np.hstack([image]))
cv2.waitKey(0)