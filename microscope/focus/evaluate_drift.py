import cv2
import numpy as np


def evaluate_drift(image0, image1):
    """
    Calculate a score representing how well the image is focused.

    :param image0: The image to evaluate.
    :param image1: The image to evaluate.
    """

    image0 = np.array(image0)
    image1 = np.array(image1)


    # Ensure both images are in grayscale (2D)
    if len(image0.shape) > 2:
        image0 = cv2.cvtColor(image0, cv2.COLOR_BGR2GRAY)
    if len(image1.shape) > 2:
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

    # Convert to the same depth if necessary
    if image0.dtype != image1.dtype:
        if image0.dtype == np.uint8:
            image1 = cv2.convertScaleAbs(image1)
        elif image0.dtype == np.float32:
            image1 = np.float32(image1)    

    # Convert both images to np.float32 if they are not already
    if image0.dtype != np.float32:
        image0 = np.float32(image0)
    if image1.dtype != np.float32:
        image1 = np.float32(image1)

    
    result = cv2.matchTemplate(image0, image1, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return np.array(max_loc)