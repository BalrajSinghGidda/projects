import os
import sys
import numpy as np
from flask import Flask, render_template, request, url_for, redirect, send_from_directory
from werkzeug.utils import secure_filename
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_io import image_io, compressed_io
from core import ds_utils
from ops import rotate, flip, crop
from alg import thresholding, quantization
from .visualize import create_sparsity_heatmap

# --- App Setup ---
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config.update({'UPLOAD_FOLDER': STATIC_DIR, 'MAX_CONTENT_LENGTH': 16 * 1024 * 1024})

# --- Filters ---
@app.template_filter()
def format_bytes(size):
    if size is None: return "N/A"
    power, n = 1024, 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G'}
    while size > power and n < len(power_labels) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"

# --- Main Processing Functions (Unchanged) ---
# process_compression, etc.
def process_compression(image_path, opts):
    base_filename = os.path.basename(image_path)
    ts = os.path.splitext(base_filename)[0]
    filenames = {'compressed_file':f"{ts}.npz",'reconstructed_image':f"recon_{ts}.png",'heatmap_image':f"heat_{ts}.png",'original_image':base_filename}
    paths = {k: os.path.join(app.config['UPLOAD_FOLDER'], v) for k, v in filenames.items()}
    dense_array = image_io.load_image(image_path, mode=None)
    if dense_array.ndim == 2: dense_array = np.stack([dense_array]*3, axis=-1)
    is_color = opts['compress_color']
    if is_color:
        channels = [dense_array[..., i] for i in range(3)]
        if opts['use_quantization']: channels = [quantization.quantize(c, opts['quantize_levels']) for c in channels]
    else:
        gray_channel = np.dot(dense_array[...,:3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        if opts['use_threshold']: gray_channel = thresholding.apply_threshold(gray_channel, opts['threshold_value'])
        channels = [gray_channel]
    dok_channels = [ds_utils.dense_to_dok(c) for c in channels]
    format_map = {'DOK': lambda d: d, 'COO': ds_utils.dok_to_coo, 'CSR': ds_utils.dok_to_csr}
    sparse_channels = [format_map[opts['format'].upper()](d) for d in dok_channels]
    compressed_io.save_sparse(paths['compressed_file'], sparse_channels)
    loaded_channels = compressed_io.load_sparse(paths['compressed_file'])
    dense_recon_channels = [s.to_dense() for s in loaded_channels]
    reconstructed_array = np.stack(dense_recon_channels, axis=-1) if len(dense_recon_channels) == 3 else dense_recon_channels[0]
    image_io.save_image(paths['reconstructed_image'], reconstructed_array)
    create_sparsity_heatmap(loaded_channels[0], paths['heatmap_image'], style='value' if opts['heatmap_style_value'] else 'binary')
    return {
        'format': opts['format'].upper(), 'is_color': is_color,
        'original_size': os.path.getsize(image_path), 'compressed_size': os.path.getsize(paths['compressed_file']),
        'ratio': os.path.getsize(image_path) / os.path.getsize(paths['compressed_file']),
        'nnz': sum(s.nnz for s in sparse_channels), 'total_pixels': dense_array.size if is_color else dense_array.size / 3,
        **filenames
    }

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    # (Unchanged)
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '': return redirect(request.url)
        filename = f"{int(time.time())}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        opts = {'format': request.form.get('format', 'csr'),'use_threshold': 'use_threshold' in request.form,'threshold_value': int(request.form.get('threshold_value', 128)),'use_quantization': 'use_quantization' in request.form,'quantize_levels': int(request.form.get('quantize_levels', 4)),'heatmap_style_value': 'heatmap_style_value' in request.form,'compress_color': 'compress_color' in request.form,}
        try: return render_template('index.html', result=process_compression(filepath, opts))
        except Exception as e:
            app.logger.error(f"Error: {e}", exc_info=True)
            return render_template('index.html', error=str(e))
    return render_template('index.html', result=None)

@app.route('/decompress', methods=['GET', 'POST'])
def decompress():
    # (Unchanged)
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.npz'): return render_template('decompress.html', error="Invalid file format.")
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            loaded_channels = compressed_io.load_sparse(filepath)
            first_channel = loaded_channels[0]
            dense_recon_channels = [s.to_dense() for s in loaded_channels]
            is_color = len(dense_recon_channels) == 3
            reconstructed_array = np.stack(dense_recon_channels, axis=-1) if is_color else dense_recon_channels[0]
            ts = os.path.splitext(filename)[0]
            reconstructed_filename = f"recon_{ts}.png"
            heatmap_filename = f"heat_{ts}.png"
            image_io.save_image(os.path.join(app.config['UPLOAD_FOLDER'], reconstructed_filename), reconstructed_array)
            create_sparsity_heatmap(first_channel, os.path.join(app.config['UPLOAD_FOLDER'], heatmap_filename))
            total_pixels = first_channel.shape[0] * first_channel.shape[1]
            if is_color: total_pixels *=3
            result = {'format': first_channel.__class__.__name__,'is_color': is_color,'compressed_size': os.path.getsize(filepath),'nnz': sum(s.nnz for s in loaded_channels),'total_pixels': total_pixels,'reconstructed_image': reconstructed_filename,'heatmap_image': heatmap_filename}
            return render_template('decompress.html', result=result)
        except Exception as e:
            app.logger.error(f"Decompression Error: {e}", exc_info=True)
            return render_template('decompress.html', error=str(e))
    return render_template('decompress.html', result=None)

@app.route('/transform', methods=['GET', 'POST'])
def transform():
    if request.method == 'POST':
        # STEP 2: A transform is being applied to a previously uploaded file
        if 'source_file' in request.form:
            try:
                filename = request.form['source_file']
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                transform_type = request.form.get('transform')
                
                loaded_channels = compressed_io.load_sparse(filepath)
                
                # Apply transformation
                if transform_type == 'crop':
                    x1, y1 = int(request.form.get('crop_x')), int(request.form.get('crop_y'))
                    w, h = int(request.form.get('crop_w')), int(request.form.get('crop_h'))
                    box = (x1, y1, x1 + w, y1 + h)
                    transformed_channels = [crop.crop(s, box) for s in loaded_channels]
                else:
                    transform_map = {'rotate90': rotate.rotate90, 'flip_vertical': lambda s: flip.flip(s, 'vertical'), 'flip_horizontal': lambda s: flip.flip(s, 'horizontal')}
                    transformed_channels = [transform_map[transform_type](s) for s in loaded_channels]
                
                # Save and reconstruct "After" image
                ts = os.path.splitext(filename)[0]
                transformed_filename_npz = f"trans_{transform_type}_{ts}.npz"
                compressed_io.save_sparse(os.path.join(app.config['UPLOAD_FOLDER'], transformed_filename_npz), transformed_channels)
                dense_after = [s.to_dense() for s in transformed_channels]
                after_array = np.stack(dense_after, axis=-1) if len(dense_after) == 3 else dense_after[0]
                after_filename_img = f"after_{ts}.png"
                image_io.save_image(os.path.join(app.config['UPLOAD_FOLDER'], after_filename_img), after_array)

                # "Before" image should still be on disk from Step 1
                before_filename_img = f"before_{ts}.png"
                
                return render_template('transform.html', result={'before_image': before_filename_img, 'after_image': after_filename_img, 'transformed_file': transformed_filename_npz})
            except Exception as e:
                app.logger.error(f"Transform Error: {e}", exc_info=True)
                return render_template('transform.html', error=str(e))

        # STEP 1: User uploads a file for the first time
        elif 'file' in request.files:
            file = request.files.get('file')
            if not file or not file.filename.endswith('.npz'):
                return render_template('transform.html', error="Invalid file format. Please upload a .npz file.")
            
            filename = f"trans_orig_{int(time.time())}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Reconstruct image to display in the canvas
                loaded_channels = compressed_io.load_sparse(filepath)
                dense_recon_channels = [s.to_dense() for s in loaded_channels]
                reconstructed_array = np.stack(dense_recon_channels, axis=-1) if len(dense_recon_channels) == 3 else dense_recon_channels[0]
                
                before_filename = f"before_{os.path.splitext(filename)[0]}.png"
                image_io.save_image(os.path.join(app.config['UPLOAD_FOLDER'], before_filename), reconstructed_array)
                
                # Re-render the page with the image ready for cropping
                return render_template('transform.html', interact_mode=True, source_file=filename, image_to_crop=before_filename)
            except Exception as e:
                app.logger.error(f"Transform Upload Error: {e}", exc_info=True)
                return render_template('transform.html', error=str(e))

    # Initial GET request
    return render_template('transform.html', interact_mode=False, result=None)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(STATIC_DIR): os.makedirs(STATIC_DIR)
    app.run(debug=True, port=5001)