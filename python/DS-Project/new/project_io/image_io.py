import numpy as np
from PIL import Image

def load_image(image_path, mode='L'):
    """
    Loads an image and converts it to a specified mode.

    Args:
        image_path (str): The path to the image file.
        mode (str): The mode to convert the image to. 'L' for grayscale.

    Returns:
        np.ndarray: A numpy array representing the image.
    """
    with Image.open(image_path) as img:
        img_converted = img.convert(mode)
        return np.array(img_converted)

def save_image(image_path, array):
    """
    Saves a numpy array as an image.

    Args:
        image_path (str): The path to save the image to.
        array (np.ndarray): The numpy array to save.
    """
    img = Image.fromarray(array)
    img.save(image_path)
