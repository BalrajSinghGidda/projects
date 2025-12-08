import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

def create_sparsity_heatmap(sparse_obj, output_path, style='binary'):
    """
    Creates a heatmap for the sparse matrix.

    Args:
        sparse_obj: A sparse format object (DOK, COO, or CSR).
        output_path (str): Path to save the heatmap image.
        style (str): 'binary' for black & white, 'value' for a color heatmap.
    """
    dense_array = sparse_obj.to_dense()

    fig, ax = plt.subplots(figsize=(5, 5))
    
    if style == 'value':
        cmap = plt.cm.hot
        cmap.set_bad(color='#1a202c' if 'dark' in output_path else '#f0f0f0') # Match dark/light theme
        masked_array = np.ma.masked_where(dense_array == 0, dense_array)
        ax.imshow(masked_array, cmap=cmap, interpolation='nearest')
        ax.set_title("Value Heatmap (Brighter = Higher Value)")
    else: # Binary style
        ax.imshow(dense_array, cmap='gray', interpolation='nearest')
        ax.set_title("Sparsity Map (Non-zero pixels are white)")

    ax.set_xticks([])
    ax.set_yticks([])
    fig.savefig(output_path, bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.close(fig)