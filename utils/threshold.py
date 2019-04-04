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

# shifted = cv2.pyrMeanShiftFiltering(image, 21, 51)
# cv2.imshow("Input", image)
 
# convert the mean shift image to grayscale, then apply
# Otsu's thresholding
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# U, thresh = cv2.threshold(blurred, 170, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
# cv2.imshow("Thresh", thresh)

# compute the exact Euclidean distance from every binary
# pixel to the nearest zero pixel, then find peaks in this
# distance map
# D = ndimage.distance_transform_edt(thresh)
# localMax = peak_local_max(D, indices=False, min_distance=20,
# 	labels=thresh)
 
# perform a connected component analysis on the local peaks,
# using 8-connectivity, then appy the Watershed algorithm
# markers = ndimage.label(localMax, structure=np.ones((3, 3)))[0]
# labels = watershed(D, markers, mask=thresh)
# print("[INFO] {} unique segments found".format(len(np.unique(labels)) - 1))

# cv2.imshow("image: ", image)

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

	# xrank = np.argsort(coords[:, 0])

	# left = coords[xrank[:2], :]
	# yrank = np.argsort(left[:, 1])
	# left = left[yrank, :]

	# right = coords[xrank[2:], :]
	# yrank = np.argsort(right[:, 1])
	# right = right[yrank, :]

    # #            top-left,       top-right,       bottom-right,    bottom-left
	# box_coords = tuple(left[0]), tuple(right[0]), tuple(right[1]), tuple(left[1])
	# box_dims = rotbox[1]
	# box_centroid = int((left[0][0] + right[1][0]) / 2.0), int((left[0][1] + right[1][1]) / 2.0)
	# # cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]

	# print("box coords: ", box_coords, left[0])
	# cv2.circle(thresh,tuple(left[0]), 10, (60,255,255), -1)
	# cv2.circle(thresh,tuple(left[1]), 10, (120,255,255), -1)
	# cv2.circle(thresh,tuple(right[0]), 10, (185,255,255), -1)
	# cv2.circle(thresh,tuple(left[0]), 10, (255,255,255), -1)

	# leftie = left[1][::-1]
	# rightie = right[1][::-1]
	# print('leftie: ', leftie, rightie) 

	# rect = np.int32(cv2.boxPoints(cv2.minAreaRect(cnt)))
	# print('rects: ', rect)
	# thresh = cv2.drawContours(thresh, [rect], -1, (255, 255, 255), 2)
	# cv2.rectangle(thresh, tuple(left[0]), tuple(right[1]), (255, 255, 255), 2)

# cv2.imshow("TI: ", threshInv)
cv2.imshow("TB: ", thresh)



# cv2.imshow("BA: ", cv2.bitwise_and(image, image, mask = threshInv))
cv2.waitKey(0)

# detector = cv2.SimpleBlobDetector_create(params)

# keypoints = detector.detect(image)
# print('keypoints: ', keypoints)
# im_with_keypoints = cv2.drawKeypoints(image, keypoints, np.array([]), (200,200,200), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# print('shapes: ', image.shape, gray_image.shape)

# cv2.imshow("images", np.hstack([image, gray_image]))
# cv2.imshow("images: ", im_with_keypoints)
# cv2.waitKey(0)

# define the list of boundaries
# boundaries = [
# 	([175, 175, 175], [255, 255, 255])
# ]

