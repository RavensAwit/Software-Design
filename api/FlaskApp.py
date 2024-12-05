from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from Algorithm import capture_dimensions_from_image, genetic_algorithm, calculate_2d_bubble_wrap_size
import os
import base64
import cv2
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

api_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(api_dir, '..'))
public_dir = os.path.join(project_root, 'public')

@app.route('/')
def serve_frontend():
    filename = "Design.html"
    if not os.path.exists(os.path.join(public_dir, filename)):
        return f"html file not found in directory: {public_dir}", 404
    return send_from_directory(directory=public_dir, path=filename)

@app.route('/<path:filename>')
def serve_static_files(filename):
    file_path = os.path.join(public_dir, filename)
    if not os.path.exists(file_path):
        return f"File not found: {filename}", 404
    return send_from_directory(directory=public_dir, filename=filename)

@app.route('/capture-dimensions', methods=['POST'])
def capture_dimensions_route():
    data = request.get_json()
    if 'image' not in data:
        return jsonify({'error': 'No image provided.'}), 400

    image_data = data['image']
    # Remove the header if present
    if image_data.startswith('data:image'):
        image_data = image_data.split(',')[1]

    # Decode the image
    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Process the image
    dimensions = capture_dimensions_from_image(img)
    if dimensions is None:
        return jsonify({'error': 'Failed to process image.'}), 500

    length, width, height, output_path = dimensions
    return jsonify({
        'length': length,
        'width': width,
        'height': height,
        'image_url': f"/static/{os.path.basename(output_path)}"
    })

@app.route('/process-dimensions', methods=['POST'])
def process_dimensions():
    data = request.get_json()
    if not data or 'length' not in data or 'width' not in data or 'height' not in data:
        return jsonify({'error': 'Invalid input. Please provide length, width, and height in JSON format.'}), 400

    length = float(data['length'])
    width = float(data['width'])
    height = float(data['height'])

    object_dimensions = (length, width, height)
    best_dimensions = genetic_algorithm(object_dimensions)

    bubble_wrap_length, bubble_wrap_width = calculate_2d_bubble_wrap_size(best_dimensions)
    return jsonify({
        "optimal_dimensions": best_dimensions,
        "bubble_wrap_size": {
            "length": bubble_wrap_length,
            "width": bubble_wrap_width
        }
    })

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
