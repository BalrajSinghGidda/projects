import numpy as np

def quantize(array, levels=4):
    """
    Reduces the number of colors in an array using quantization.

    Args:
        array (np.ndarray): The input array (grayscale or color).
        levels (int): The desired number of color levels. Must be > 1.

    Returns:
        np.ndarray: The quantized array.
    """
    if levels < 2:
        raise ValueError("Number of levels must be at least 2.")

    # Determine the factor by which to divide and multiply
    factor = 256 / levels
    
    # Quantize by dividing, flooring, and then rescaling
    quantized_array = (np.floor(array / factor) * factor).astype(np.uint8)
    
    return quantized_array
