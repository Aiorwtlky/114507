# utils/distance_estimator.py

class DistanceEstimator:
    def __init__(self, pixel_height_at_1m=470, real_car_height_m=1.5):
        self.pixel_height_at_1m = pixel_height_at_1m
        self.real_car_height_m = real_car_height_m

    def estimate_distance(self, pixel_height):
        if pixel_height <= 0:
            return None
        estimated_distance = (self.pixel_height_at_1m / pixel_height) * 1
        return estimated_distance
