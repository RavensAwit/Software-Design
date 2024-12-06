from flask import jsonify, request
import base64
import cv2
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor
from Algorithm import capture_dimensions_from_image

# Create a ThreadPoolExecutor for offloading processing
executor = ThreadPoolExecutor(max_workers=2)

def decode_and_process_image(image_data):
    """
    Decodes and processes the image, returns dimensions or an error.
    """
    try:
        # Decode base64 image
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]

        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Resize image to reduce processing load
        img = cv2.resize(img, (640, 480))

        # Start processing
        start_time = time.time()
        dimensions = capture_dimensions_from_image(img)
        processing_time = time.time() - start_time

        if dimensions is None:
            return None, f"Failed to process image (processing time: {processing_time:.2f} seconds)"

        length, width, height, output_path = dimensions
        return {
            'length': length,
            'width': width,
            'height': height,
            'image_url': f"/static/{output_path}",
            'processing_time': processing_time
        }, None

    except Exception as e:
        return None, str(e)

def handler(request):
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': 'No image provided.'}), 400

    image_data = data['image']

    # Submit image processing to a separate thread
    future = executor.submit(decode_and_process_image, image_data)
    result, error = future.result()

    if error:
        return jsonify({'error': f'An error occurred: {error}'}), 500

    return jsonify({
        'length': result['length'],
        'width': result['width'],
        'height': result['height'],
        'image_url': result['image_url'],
        'processing_time': f"{result['processing_time']:.2f} seconds"
    })
