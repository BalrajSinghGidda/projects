import numpy as np

def apply_threshold(array, threshold=128):
    """
    Applies a binary threshold to a grayscale or color array.
    If the image is color, it's converted to grayscale first.

    Args:
        array (np.ndarray): The input array.
        threshold (int): The threshold value (0-255).

    Returns:
        np.ndarray: The black and white (uint8) thresholded array.
    """
    if array.ndim == 3 and array.shape[2] in [3, 4]:
        # Convert RGB/RGBA to grayscale using luminosity method
        grayscale_array = np.dot(array[...,:3], [0.2989, 0.5870, 0.1140])
    else:
        grayscale_array = array
        
    return np.where(grayscale_array > threshold, 255, 0).astype(np.uint8)