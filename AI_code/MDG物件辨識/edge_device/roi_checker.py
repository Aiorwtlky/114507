import math

class InnerWheelDiffROI:
    def __init__(self, axle_length, turn_angle_deg, pixels_per_meter, center_x, center_y):
        self.a = axle_length
        self.theta_deg = turn_angle_deg
        self.theta_rad = math.radians(turn_angle_deg)
        self.pixels_per_meter = pixels_per_meter
        self.center_x = center_x
        self.center_y = center_y
        self.calc_radii()

    def calc_radii(self):
        self.R = self.a / math.sin(self.theta_rad)
        self.r = self.a / math.tan(self.theta_rad)
        self.R_px = int(self.R * self.pixels_per_meter)
        self.r_px = int(self.r * self.pixels_per_meter)

    def update_angle(self, new_angle_deg):
        self.theta_deg = new_angle_deg
        self.theta_rad = math.radians(new_angle_deg)
        self.calc_radii()

    def is_point_in_roi(self, x, y):
        dist_sq = (x - self.center_x) ** 2 + (y - self.center_y) ** 2
        return self.r_px ** 2 <= dist_sq <= self.R_px ** 2

    def draw_roi(self, frame):
        import cv2
        cv2.circle(frame, (self.center_x, self.center_y), self.R_px, (255, 0, 0), 2)
        cv2.circle(frame, (self.center_x, self.center_y), self.r_px, (0, 255, 0), 2)
        # 可以再加標註文字
