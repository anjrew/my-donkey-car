from dataclasses import dataclass
import math
from typing import Optional, Tuple
import cv2
import numpy as np
from simple_pid import PID
import logging

LOGGER = logging.getLogger(__name__)


@dataclass
class CannyEdgeDetectionParams:
    low_threshold: int
    high_threshold: int
    gaussian_blur_kernal_size: int


@dataclass
class HoughLineDetectionParams:
    rho: int
    theta: int
    threshold: int
    min_line_length: int
    max_line_gap: int


class EdgeDetectionParams:
    canny_params: CannyEdgeDetectionParams
    hough_params: HoughLineDetectionParams


class LineFollower:
    """
    OpenCV based controller
    This controller takes a horizontal slice of the image at a set Y coordinate.
    Then it converts to HSV and does a color thresh hold to find the yellow pixels.
    It does a histogram to find the pixel of maximum yellow. Then is uses that iPxel
    to guid a PID controller which seeks to maintain the max yellow at the same point
    in the image.
    """

    def __init__(self, pid: PID, cfg):
        self.overlay_image = cfg.OVERLAY_IMAGE
        self.scan_y = cfg.SCAN_Y  # num pixels from the top to start horiz scan
        self.scan_height = cfg.SCAN_HEIGHT  # num pixels high to grab from horiz scan
        self.color_thr_low = np.asarray(cfg.COLOR_THRESHOLD_LOW)  # hsv dark yellow
        self.color_thr_hi = np.asarray(cfg.COLOR_THRESHOLD_HIGH)  # hsv light yellow
        self.edge_color_thr_low = np.asarray(
            cfg.EDGE_COLOR_THRESHOLD_LOW
        )  # hsv dark edge color
        self.edge_color_thr_hi = np.asarray(
            cfg.EDGE_COLOR_THRESHOLD_HIGH
        )  # hsv light edge color
        self.target_pixel = (
            cfg.TARGET_PIXEL
        )  # of the N slots above, which is the ideal relationship target
        self.target_threshold = (
            cfg.TARGET_THRESHOLD
        )  # minimum distance from target_pixel before a steering change is made.
        self.confidence_threshold = (
            cfg.CONFIDENCE_THRESHOLD
        )  # percentage of yellow pixels that must be in target_pixel slice
        self.steering = 0.0  # from -1 to 1
        self.throttle = cfg.THROTTLE_INITIAL  # from -1 to 1
        self.delta_th = cfg.THROTTLE_STEP  # how much to change throttle when off
        self.throttle_max = cfg.THROTTLE_MAX
        self.throttle_min = cfg.THROTTLE_MIN
        self.show_steering = cfg.SHOW_STEERING
        self.show_throttle = cfg.SHOW_THROTTLE
        self.canny_params = CannyEdgeDetectionParams(
            cfg.CANNY_LOW_THRESHOLD,
            cfg.CANNY_HIGH_THRESHOLD,
            cfg.CANNY_KERNEL_SIZE,
        )
        self.hough_params = HoughLineDetectionParams(
            cfg.HOUGH_RHO,
            cfg.HOUGH_THETA,
            cfg.HOUGH_THRESHOLD,
            cfg.HOUGH_MIN_LINE_LENGTH,
            cfg.HOUGH_MAX_LINE_GAP,
        )
        self.pid_st = pid

    def get_roi_mask(self, cam_img: np.ndarray) -> np.ndarray:
        """
        Get the mask of the center region of the image based on the color thresholds.
        """
        # take a horizontal slice of the image
        i_slice = self.scan_y

        # Get all the pixels in the slice from the image from the top to the bottom of the
        # scan to the scan height with all horizontal pixels and all color channels
        scan_line = cam_img[
            i_slice : i_slice + self.scan_height, :, :  # flake8: ignore E203
        ]

        # convert to HSV color space
        img_hsv = cv2.cvtColor(scan_line, cv2.COLOR_RGB2HSV)

        # make a mask of the colors in our range we are looking for
        center_mask = cv2.inRange(img_hsv, self.color_thr_low, self.color_thr_hi)
        return center_mask

    def get_i_color(self, center_mask: np.ndarray) -> tuple[int, float]:
        """
        get the horizontal index of the color at the given slice of the image
        input: cam_image, an RGB numpy array
        output: index of max color, value of cumulative color at that index
        """
        # which index of the range has the highest amount of yellow?
        hist = np.sum(center_mask, axis=0)
        max_yellow = np.argmax(hist)

        return int(max_yellow), hist[max_yellow]

    def get_track_angle_deg_from_direction_line(
        self, direction_line: tuple[int, int, int, int]
    ) -> float:
        """
        Calculate the angle of the direction line with respect to the horizontal axis.
        input: direction_line(Tuple(x1, y1, x2, y2))
        output: angle(float)
        """
        x1, y1, x2, y2 = direction_line

        # Calculate the angle in radians
        angle_radians = math.atan2(y2 - y1, x2 - x1)

        # Convert the angle from radians to degrees
        angle_degrees = math.degrees(angle_radians)

        # Adjust the angle to match the desired convention
        angle_degrees = (90 - angle_degrees) % 180
        if angle_degrees > 90:
            angle_degrees = -(180 - angle_degrees)

        return angle_degrees

    def run_line_detection_on_hsv_mask(
        self, roi_mask: np.ndarray
    ) -> Tuple[int, int, int, int]:
        """
        Process the HSV feature extracted center_mask to perform edge detection and line detection.
        input: center_mask, a binary mask representing the extracted colors
        output: direction_line(Tuple(x1, y1, x2, y2))
        """
        # Apply Gaussian blur to reduce noise
        kernal_size = self.canny_params.gaussian_blur_kernal_size
        kernal = (kernal_size, kernal_size)
        sigma_standard_deviation = 0

        blurred = cv2.GaussianBlur(roi_mask, kernal, sigma_standard_deviation)

        # Perform Canny edge detecti
        edges = cv2.Canny(
            blurred, self.canny_params.low_threshold, self.canny_params.high_threshold
        )

        # Perform Hough transformation to detect lines
        hough_params = self.hough_params
        lines = cv2.HoughLinesP(
            edges,
            rho=hough_params.rho,
            theta=hough_params.theta,
            threshold=hough_params.threshold,
            minLineLength=hough_params.min_line_length,
            maxLineGap=hough_params.max_line_gap,
        )

        # Create a mask to store the detected lines
        line_mask = np.zeros_like(roi_mask)
        line_color = (0, 255, 0)

        # Draw the detected lines on the line_mask
        if lines is None:
            LOGGER.log(logging.DEBUG, "No lines detected")

        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_mask, (x1, y1), (x2, y2), line_color, 2)  # type: ignore

        # Extract the parameters of the detected lines
        lines_parameters = []

        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            slope, intercept = np.polyfit((x1, x2), (y1, y2), 1)
            lines_parameters.append((slope, intercept))

        average_slope_intercept = np.average(lines_parameters, axis=0)

        slope, intercept = average_slope_intercept
        y1 = roi_mask.shape[0]
        ratio_up_the_screen = 3 / 5
        y2 = int(y1 * (ratio_up_the_screen))
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
        direction_line = (x1, y1, x2, y2)

        return direction_line

    def run(self, img: np.ndarray) -> tuple[float, float, Optional[np.ndarray]]:
        """
        main runloop of the CV controller
        INPUT: cam_image, an RGB numpy array
        OUTPUT: steering, throttle, and the image.
        If overlay_image is True, then the output image
        includes and overlay that shows how the
        algorithm is working; otherwise the image
        is just passed-through untouched.
        """
        if img is None:
            return 0, 0, None

        roi_mask = self.get_roi_mask(
            img,
        )

        max_yellow, confidence = self.get_i_color(roi_mask)

        # Run edge detection and line detection on the HSV mask for the scan section
        try:
            track_direction_line = self.run_line_detection_on_hsv_mask(roi_mask)
            track_angle = self.get_track_angle_deg_from_direction_line(
                track_direction_line
            )
        except Exception as e:
            LOGGER.error(f"Error in line detection: {e}")
            track_direction_line = None
            track_angle = None

        if self.target_pixel is None:
            # Use the first run of get_i_color to set our relationship with the yellow line.
            # You could optionally init the target_pixel with the desired value.
            self.target_pixel = max_yellow
            LOGGER.info(f"Automatically chosen line position = {self.target_pixel}")

        assert self.target_pixel is not None, "No target pixel set."
        assert (
            type(self.target_pixel) is int
        ), f"Target pixel must be an integer but was {type(self.target_pixel)}."

        if self.pid_st.setpoint != self.target_pixel:
            # this is the target of our steering PID controller
            self.pid_st.setpoint = self.target_pixel

        if confidence >= self.confidence_threshold:
            # invoke the controller with the current yellow line position
            # get the new steering value as it chases the ideal
            self.steering = self.pid_st(int(max_yellow))

            # slow down linearly when away from ideal, and speed up when close
            if abs(max_yellow - self.target_pixel) > self.target_threshold:
                # we will be turning, so slow down
                if self.throttle > self.throttle_min:
                    self.throttle -= self.delta_th
                if self.throttle < self.throttle_min:
                    self.throttle = self.throttle_min
            else:
                # we are going straight, so speed up
                if self.throttle < self.throttle_max:
                    self.throttle += self.delta_th
                if self.throttle > self.throttle_max:
                    self.throttle = self.throttle_max
        else:
            LOGGER.info(
                f"No line detected: confidence {confidence} < {self.confidence_threshold}"
            )

        # show some diagnostics
        if self.overlay_image:
            img = self.overlay_display(
                img,
                roi_mask,
                max_yellow,
                confidence,
                int(self.target_pixel),
                track_direction_line,
                int(track_angle) if track_angle is not None else None,
            )

        steering = self.steering if self.steering is not None else 0.0
        return steering, self.throttle, img

    def draw_target_pixel(
        self,
        img: np.ndarray,
        target_pixel: int,
        scan_y: int,
        color: tuple = (0, 255, 255),
        size: int = 5,
        thickness: int = 2,
    ) -> None:
        """
        Draw a marker or circle at the target pixel location on the image.
        """
        cv2.drawMarker(
            img,
            (target_pixel, scan_y),
            color,
            cv2.MARKER_CROSS,
            markerSize=size,
            thickness=thickness,
        )

    def overlay_display(
        self,
        cam_img: np.ndarray,
        roi_mask: np.ndarray,
        max_yellow: int,
        confidence: float,
        target_pixel: int,
        track_direction_line: Optional[Tuple[int, int, int, int]] = None,
        track_angle_deg: Optional[int] = None,
    ) -> np.ndarray:
        """
        Composite mask on top the original image.
        show some values we are using for control
        """

        # Expand the dimensions of the mask to match the image shape
        mask_exp = np.stack((roi_mask,) * 3, axis=-1)

        # Define the region of interest (ROI) where the line is being detected
        i_slice = self.scan_y

        # Make a copy of the original image to avoid modifying it directly
        img = np.copy(cam_img)

        # Overlay the mask on the ROI of the image
        img[i_slice : i_slice + self.scan_height, :, :] = mask_exp

        neon_pink_rgb = (255, 0, 255)
        target_pixel_rgb: tuple = (0, 255, 255)  # Turqiose
        max_yellow_hori_rgb: tuple = (0, 0, 255)  # Blue
        text_bgr: tuple = (255, 0, 255)  # Neon Pink
        track_direction_rgb = (0, 255, 0)  # Green
        steering_line_rgb = neon_pink_rgb  # Neon Pink
        threshold_region_rgb = (255, 0, 0)  # Red

        # Draw a marker or circle at the target pixel location
        self.draw_target_pixel(img, target_pixel, i_slice, color=target_pixel_rgb)

        # Draw a marker or circle at the max_yellow position
        self.draw_target_pixel(img, int(max_yellow), i_slice, color=max_yellow_hori_rgb)

        # Draw the target pixel threshold region
        left_threshold = target_pixel - self.target_threshold
        right_threshold = target_pixel + self.target_threshold
        cv2.rectangle(
            img,
            (left_threshold, i_slice),
            (right_threshold, i_slice + self.scan_height),
            threshold_region_rgb,
            2,
        )
        # Prepare the display strings with relevant information
        display_str_col = []
        display_str_col.append(f"STEERING: {int(self.steering or 0)}")
        display_str_col.append("THROTTLE: {:.0f}%".format(self.throttle * 100))
        display_str_col.append("MAX YELLOW: {:d}".format(max_yellow))
        display_str_col.append("CONF: {:.2f}".format(confidence))
        display_str_col.append("TARGET PIXEL: {:d}".format(target_pixel))
        if track_angle_deg is not None:
            display_str_col.append(f"TRACK ANG: {int(track_angle_deg)}")

        # Set the initial position for displaying the text
        y = 10
        x = 10

        # Iterate over each display string and render it on the image
        for s in display_str_col:
            cv2.putText(
                img,
                s,
                org=(x, y),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.25,
                color=text_bgr,
                thickness=1,
                lineType=cv2.LINE_AA,
            )
            y += 10

        # Display the steering as a polar line at the bottom of the image, horizontally centered
        if self.show_steering:
            center_x = img.shape[1] // 2
            center_y = img.shape[0]
            steering_angle = np.radians(-self.steering)  # type: ignore # Convert steering to radians and invert the sign
            line_length = 50
            end_x = int(center_x + line_length * np.sin(steering_angle))
            end_y = int(center_y - line_length * np.cos(steering_angle))
            cv2.line(img, (center_x, center_y), (end_x, end_y), steering_line_rgb, 2)

        # Display the throttle as a bar
        if self.show_throttle:
            bar_width = 10
            bar_height = int(self.throttle * 100)
            bar_x = img.shape[1] - 20
            bar_y = img.shape[0] - 20
            cv2.rectangle(
                img,
                (bar_x, bar_y),
                (bar_x + bar_width, bar_y - bar_height),
                (0, 0, 255),
                -1,
            )

        # Draw the track direction line if detected
        if track_direction_line is not None:
            y_offset = i_slice
            x1, y1, x2, y2 = track_direction_line
            y1 += y_offset
            y2 += y_offset
            cv2.line(img, (x1, y1), (x2, y2), track_direction_rgb, 2)  # Yellow line

        return img
