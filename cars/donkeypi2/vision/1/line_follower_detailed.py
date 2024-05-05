from typing import Optional
import cv2
import numpy as np
from simple_pid import PID
import logging

logger = logging.getLogger(__name__)


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
        self.edge_color_thr_low = np.asarray(cfg.EDGE_COLOR_THRESHOLD_LOW)  # hsv dark edge color
        self.edge_color_thr_hi = np.asarray(cfg.EDGE_COLOR_THRESHOLD_HIGH)  # hsv light edge color
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
        self.pid_st = pid

    def get_i_color(self, cam_img: np.ndarray) -> tuple[int, float, np.ndarray]:
        """
        get the horizontal index of the color at the given slice of the image
        input: cam_image, an RGB numpy array
        output: index of max color, value of cumulative color at that index, and mask of pixels in range
        """
        # take a horizontal slice of the image
        i_slice = self.scan_y

        # Get all the pixels in the slice from the image from the top to the bottom of the
        # scan to the scan height with all horizontal pixels and all color channels
        scan_line = cam_img[i_slice: i_slice + self.scan_height, :, :]

        # convert to HSV color space
        img_hsv = cv2.cvtColor(scan_line, cv2.COLOR_RGB2HSV)

        # make a mask of the colors in our range we are looking for
        center_mask = cv2.inRange(img_hsv, self.color_thr_low, self.color_thr_hi)

        # which index of the range has the highest amount of yellow?
        hist = np.sum(center_mask, axis=0)
        max_yellow = np.argmax(hist)

        return int(max_yellow), hist[max_yellow], center_mask

    def run(self, cam_img: np.ndarray) -> tuple[float, float, Optional[np.ndarray]]:
        """
        main runloop of the CV controller
        INPUT: cam_image, an RGB numpy array
        OUTPUT: steering, throttle, and the image.
        If overlay_image is True, then the output image
        includes and overlay that shows how the
        algorithm is working; otherwise the image
        is just passed-through untouched.
        """
        if cam_img is None:
            return 0, 0, None

        max_yellow, confidence, mask = self.get_i_color(cam_img)

        if self.target_pixel is None:
            # Use the first run of get_i_color to set our relationship with the yellow line.
            # You could optionally init the target_pixel with the desired value.
            self.target_pixel = max_yellow
            logger.info(f"Automatically chosen line position = {self.target_pixel}")

        assert self.target_pixel is not None, "No target pixel set."
        assert type(self.target_pixel) is int, f"Target pixel must be an integer but was {type(self.target_pixel)}."

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
            logger.info(
                f"No line detected: confidence {confidence} < {self.confidence_threshold}"
            )

        # show some diagnostics
        if self.overlay_image:
            cam_img = self.overlay_display(
                cam_img,
                mask,
                max_yellow,
                confidence,
                int(self.target_pixel)
            )

        steering = self.steering if self.steering is not None else 0.0
        return steering, self.throttle, cam_img

    def draw_target_pixel(
        self,
        img: np.ndarray,
        target_pixel: int,
        scan_y: int,
        color: tuple = (0, 255, 255),
        size: int = 5,
        thickness: int = 2
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
            thickness=thickness
        )

    def overlay_display(
        self,
        cam_img: np.ndarray,
        mask: np.ndarray,
        max_yellow: int,
        confidence: float,
        target_pixel: int,
    ) -> np.ndarray:
        """
        Composite mask on top the original image.
        show some values we are using for control
        """

        # Expand the dimensions of the mask to match the image shape
        mask_exp = np.stack((mask,) * 3, axis=-1)

        # Define the region of interest (ROI) where the line is being detected
        i_slice = self.scan_y

        # Make a copy of the original image to avoid modifying it directly
        img = np.copy(cam_img)

        # Overlay the mask on the ROI of the image
        img[i_slice: i_slice + self.scan_height, :, :] = mask_exp

        target_pixel_color: tuple = (0, 255, 255)  # Yellow
        max_yellow_color: tuple = (0, 0, 255)  # Red
        text_color: tuple = (255, 0, 255)  # Neon Pink

        # Draw a marker or circle at the target pixel location
        self.draw_target_pixel(
            img, target_pixel, i_slice, color=target_pixel_color
        )

        # Draw a marker or circle at the max_yellow position
        self.draw_target_pixel(
            img, int(max_yellow), i_slice, color=max_yellow_color
        )

        # Draw the target pixel threshold region
        left_threshold = target_pixel - self.target_threshold
        right_threshold = target_pixel + self.target_threshold
        cv2.rectangle(
            img,
            (left_threshold, i_slice),
            (right_threshold, i_slice + self.scan_height),
            (255, 0, 0),
            2,
        )

        # Prepare the display strings with relevant information
        display_str_col = []
        display_str_col.append("STEERING: {:.1f}".format(self.steering))
        display_str_col.append("THROTTLE: {:.2f}%".format(self.throttle * 100))
        display_str_col.append("MAX YELLOW: {:d}".format(max_yellow))
        display_str_col.append("CONF: {:.2f}".format(confidence))
        display_str_col.append(
            "TARGET PIXEL: {:d}".format(target_pixel)
        )

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
                color=text_color,
                thickness=1,
                lineType=cv2.LINE_AA
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
            cv2.line(img, (center_x, center_y), (end_x, end_y), (0, 255, 0), 2)

        # Display the throttle as a bar
        if self.show_throttle:
            bar_width = 10
            bar_height = int(self.throttle * 100)
            bar_x = img.shape[1] - 20
            bar_y = img.shape[0] - 20
            cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y - bar_height), (0, 0, 255), -1)

        return img
