# import the necessary packages
import time
import numpy as np
import argparse
import imutils
import glob
import cv2
# import matplotlib.pyplot as plt   
from detection import Utils

class FilamentDetector():
    """ 
    This FilamentDetector class uses Template matching and Structural Similarity Index Measure to classify
    extruder with filament flow and extruder with filament clogged or exhausted images. The template image is matched
    with the input frame image and identifies the closely resembling match (i.e.) extruder (ROI - Region of Interest).
    Further the ROI and template is checked for SSIM to classification with specific threshold value of (< 0).
    """   

    def __init__(self):
        self.utils = Utils()


    def resize(self, image, scale_percent=15):
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        return cv2.resize(image, dim, interpolation = cv2.INTER_AREA)


    def process(self, image_file):
        # load the image, resize, convert it to grayscale, and detect edges
        template = cv2.imread('template.jpg')
        template = self.resize(image=template)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template_copy = template.copy()
        template = cv2.Canny(template, 50, 200)
        (tH, tW) = template.shape[:2]

        '''load the image, convert it to grayscale, and initialize the
        bookkeeping variable to keep track of the matched region'''

        image = cv2.imread(image_file)
        image = self.resize(image=image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        found = None

        # loop over the scales of the image
        for scale in np.linspace(0.2, 1.0, 20)[::-1]:
            '''resize the image according to the scale, and keep track
            of the ratio of the resizing'''
            resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            '''if the resized image is smaller than the template, then break
            from the loop'''
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break

            '''detect edges in the resized, grayscale image and apply template
            matching to find the template in the image'''
            edged = cv2.Canny(resized, 50, 200)
            result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            '''if we have found a new maximum correlation value, then update
            the bookkeeping variable'''
            
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        '''unpack the bookkeeping variable and compute the (x, y) coordinates
        of the bounding box based on the resized ratio'''
        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

        # draw a bounding box around the detected result and display the image
        # cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)

        roi_image = image[startY:endY, startX:endX]
        roi_image = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
        roi = self.utils.resize_to_template(template, roi_image)
        response = self.utils.get_ssim(template, roi)
        return response
        # return (template_copy, roi, bw_diff)



'''
fd = FilamentDetector()
template, roi, bw_diff = fd.process()
plt.subplot(131),plt.imshow(template, cmap = 'gray')
plt.title('Template'), plt.xticks([]), plt.yticks([])
plt.subplot(132),plt.imshow(roi, cmap = 'gray')
plt.title('ROI'), plt.xticks([]), plt.yticks([])
plt.subplot(133),plt.imshow(bw_diff, cmap = 'gray')
plt.title('Difference'), plt.xticks([]), plt.yticks([])

plt.show()
'''
