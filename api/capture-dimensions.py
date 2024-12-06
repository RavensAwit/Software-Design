from flask import jsonify, request
import base64
import cv2
import numpy as np
from Algorithm import capture_dimensions_from_image

def handler(request):
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': 'No image provided.'}), 400

    # Decode the image
    image_data = data['image']
    if image_data.startswith('data:image'):
        image_data = image_data.split(',')[1]

    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    try:
        dimensions = capture_dimensions_from_image(img)
        
        if dimensions is None:
            return jsonify({'error': 'Failed to process image.'}), 500

        length, width, height, output_path = dimensions

        return jsonify({
            'length': length,
            'width': width,
            'height': height,
            'image_url': f"/static/{output_path}"
        })
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
