import cv2
import numpy as np
import random
import math
import os

REFERENCE_DIAMETER_COIN_CM = 3.0
REFERENCE_LENGTH_PHONE_CM = 15.0
REFERENCE_WIDTH_PHONE_CM = 7.5
PREDETERMINED_COIN_PIXELS = 100
PREDETERMINED_PHONE_PIXELS_LENGTH = 300
CALIBRATION_FACTOR_COIN = REFERENCE_DIAMETER_COIN_CM / PREDETERMINED_COIN_PIXELS
CALIBRATION_FACTOR_PHONE_LENGTH = REFERENCE_LENGTH_PHONE_CM / PREDETERMINED_PHONE_PIXELS_LENGTH
adjustment_factor = 3

def determine_reference_object(bbox):
    x, y, w, h = bbox
    aspect_ratio = w / h

    if 0.8 <= aspect_ratio <= 1.2:
        return "coin"
    else:
        return "phone"

def capture_dimensions_from_image(img):
    _, bbox = get_largest_contour(img)
    if bbox is None:
        print("No object detected.")
        return None

    x, y, w, h = bbox
    reference_object = determine_reference_object(bbox)

    calibration_factor = CALIBRATION_FACTOR_COIN if reference_object == "coin" else CALIBRATION_FACTOR_PHONE_LENGTH
    length_cm = round(h * calibration_factor, 2)
    width_cm = round(w * calibration_factor, 2)
    height_cm = round(w * calibration_factor * 0.25 + adjustment_factor, 2) 

    print(f"Detected Dimensions (cm): Length: {length_cm:.2f}, Width: {width_cm:.2f}, Height: {height_cm:.2f}")

    os.makedirs("static", exist_ok=True)
    output_path = "static/captured_image_with_box.jpg"
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imwrite(output_path, img)
    print(f"Processed image saved as {output_path}")

    return length_cm, width_cm, height_cm, output_path

def get_largest_contour(img, min_area=1000):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)
    img_canny = cv2.Canny(img_blur, 50, 150)
    kernel = np.ones((5, 5))
    img_dilate = cv2.dilate(img_canny, kernel, iterations=2)
    img_erode = cv2.erode(img_dilate, kernel, iterations=1)

    contours, _ = cv2.findContours(img_erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = None
    largest_bbox = None
    max_area = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area and area > max_area:
            max_area = area
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            largest_bbox = cv2.boundingRect(approx)
            largest_contour = contour

    return img, largest_bbox

def fitness_function(solution, object_dimensions, sealing_margin=2):
    length, width, height = solution
    min_length = object_dimensions[0] + sealing_margin
    min_width = object_dimensions[1] + sealing_margin
    min_height = object_dimensions[2] + sealing_margin

    length_penalty = max(0, min_length - length)
    width_penalty = max(0, min_width - width)
    height_penalty = max(0, min_height - height)

    return length_penalty + width_penalty + height_penalty

def genetic_algorithm(object_dimensions, population_size=15, generations=80, sealing_margin=2, mutation_rate=0.1):
    population = [
        np.array([
            object_dimensions[0] + sealing_margin + random.uniform(0, 0.1),
            object_dimensions[1] + sealing_margin + random.uniform(0, 0.1),
            object_dimensions[2] + sealing_margin + random.uniform(0, 0.1)
        ])
        for _ in range(population_size)
    ]

    for generation in range(generations):
        population.sort(key=lambda individual: fitness_function(individual, object_dimensions, sealing_margin))
        best_solution = population[0]

        new_population = []
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(population[:5], 2)
            child = (parent1 + parent2) / 2
            if random.random() < mutation_rate:
                child += np.random.normal(0, 0.1, 3)
            new_population.append(child)

        population = new_population

    best_solution = min(population, key=lambda individual: fitness_function(individual, object_dimensions, sealing_margin))
    return {
        "Optimal Length": best_solution[0],
        "Optimal Width": best_solution[1],
        "Optimal Height": best_solution[2]
    }

def calculate_2d_bubble_wrap_size(optimal_dimensions):
    optimal_length = optimal_dimensions["Optimal Length"]
    optimal_width = optimal_dimensions["Optimal Width"]
    optimal_height = optimal_dimensions["Optimal Height"]
    bubble_wrap_length = 2 * optimal_length + 2 * optimal_height
    bubble_wrap_width = optimal_width + optimal_height
    return bubble_wrap_length, bubble_wrap_width
