import cv2
import numpy as np
from skimage.measure import compare_nrmse, compare_ssim
import imutils


class Utils():
    """
    This Utils class provides resizing image to template size and to get structural similarity
    index measure (ssim) between Template and ROI images.
    """

    def __init__(self):
        pass
    
    def resize_to_template(self, template, roi):
        width = template.shape[1]
        height = template.shape[0]
        dim = (width, height)
        # resize image
        resized_img = cv2.resize(roi, dim, interpolation = cv2.INTER_AREA)
        return resized_img
    
    def get_ssim(self, template, roi):
        # absolute difference of roi and template
        difference = cv2.absdiff(template, roi)

        # Normalized Root Mean Square Error calculation 
        nrmse = compare_nrmse(template, roi)

        # Structural Similarity Index Measure Calculation
        ssim = compare_ssim(template, roi)
        print('SSIM: %f'%(ssim))

        if ssim < 0:
            print('Filament flow error!! Printing stopped')
            return 2
        else:
            print('Printing...')
            return 1
        # return difference
