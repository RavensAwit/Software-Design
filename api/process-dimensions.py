from flask import jsonify, request
from Algorithm import genetic_algorithm, calculate_2d_bubble_wrap_size

def handler(request):
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
